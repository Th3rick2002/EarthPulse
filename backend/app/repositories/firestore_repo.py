"""Firestore repository implementation for production (Cloud Run)."""

from datetime import date, datetime, timedelta
from typing import Optional
from abc import ABC

from app.repositories.base import BaseRepository, BaseCacheRepository
from app.schemas.series import Observation, Coverage, Analysis


class FirestoreRepository(BaseRepository):
    """Firestore-backed observation repository (skeleton)."""

    def __init__(self, project_id: str | None = None):
        self.project_id = project_id
        self._client = None
        # TODO: Initialize Firestore client when deployed
        # from google.cloud import firestore
        # self._client = firestore.Client(project=project_id)

    def _get_client(self):
        """Lazy-initialize Firestore client."""
        if self._client is None:
            try:
                from google.cloud import firestore
                self._client = firestore.Client(project=self.project_id)
            except ImportError:
                raise RuntimeError("google-cloud-firestore not installed")
        return self._client

    async def get_observations(
        self,
        variable_id: str,
        region_id: str,
        start_date: date,
        end_date: date,
    ) -> list[Observation]:
        client = self._get_client()
        # Query observations collection
        # Collection: observations/{variable_id}_{region_id}/data/{period_start}
        coll_id = f"{variable_id}_{region_id}"
        docs = (
            client.collection("observations")
            .document(coll_id)
            .collection("data")
            .where("period_start", ">=", start_date.isoformat())
            .where("period_start", "<=", end_date.isoformat())
            .order_by("period_start")
            .stream()
        )

        observations = []
        for doc in docs:
            data = doc.to_dict()
            observations.append(
                Observation(
                    date=date.fromisoformat(data["period_start"]),
                    value=data["value"],
                    quality=data["quality"],
                )
            )
        return observations

    async def save_observations(
        self,
        variable_id: str,
        region_id: str,
        observations: list[Observation],
    ) -> None:
        if not observations:
            return

        client = self._get_client()
        coll_id = f"{variable_id}_{region_id}"
        batch = client.batch()

        for obs in observations:
            doc_ref = (
                client.collection("observations")
                .document(coll_id)
                .collection("data")
                .document(obs.date.isoformat())
            )
            batch.set(doc_ref, {
                "period_start": obs.date.isoformat(),
                "value": obs.value,
                "quality": obs.quality.value,
                "unit": "index",  # From catalog
                "source_provider": "mock",
                "source_product": "mock",
                "source_id": "mock",
                "fetched_at": datetime.utcnow().isoformat(),
            })

        batch.commit()


class FirestoreCacheRepository(BaseCacheRepository):
    """Firestore-backed query cache repository (skeleton)."""

    def __init__(self, project_id: str | None = None):
        self.project_id = project_id
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from google.cloud import firestore
                self._client = firestore.Client(project=self.project_id)
            except ImportError:
                raise RuntimeError("google-cloud-firestore not installed")
        return self._client

    async def get_cached_series(
        self,
        cache_key: str,
    ) -> tuple[list[Observation], Coverage, Analysis | None] | None:
        client = self._get_client()
        doc = client.collection("cache").document(cache_key).get()

        if not doc.exists:
            return None

        data = doc.to_dict()
        expires_at = datetime.fromisoformat(data["expires_at"])
        if datetime.utcnow() > expires_at:
            await self.invalidate(cache_key)
            return None

        import json
        observations = [
            Observation(
                date=date.fromisoformat(o["date"]),
                value=o["value"],
                quality=o["quality"],
            )
            for o in json.loads(data["observations_json"])
        ]
        coverage = Coverage(**json.loads(data["coverage_json"]))
        analysis = Analysis(**json.loads(data["analysis_json"])) if data.get("analysis_json") else None

        return observations, coverage, analysis

    async def set_cached_series(
        self,
        cache_key: str,
        observations: list[Observation],
        coverage: Coverage,
        analysis: Analysis | None,
        ttl_seconds: int = 86400,
    ) -> None:
        client = self._get_client()
        fetched_at = datetime.utcnow()
        expires_at = datetime.fromtimestamp(fetched_at.timestamp() + ttl_seconds)

        import json
        parts = cache_key.split(":")
        variable_id = parts[0] if len(parts) > 0 else ""
        region_id = parts[1] if len(parts) > 1 else ""
        start_date = parts[2] if len(parts) > 2 else ""
        end_date = parts[3] if len(parts) > 3 else ""

        client.collection("cache").document(cache_key).set({
            "cache_key": cache_key,
            "variable_id": variable_id,
            "region_id": region_id,
            "start_date": start_date,
            "end_date": end_date,
            "observations_json": json.dumps([o.model_dump(mode="json") for o in observations]),
            "coverage_json": json.dumps(coverage.model_dump(mode="json")),
            "analysis_json": json.dumps(analysis.model_dump(mode="json")) if analysis else None,
            "fetched_at": fetched_at.isoformat(),
            "expires_at": expires_at.isoformat(),
        })

    async def invalidate(self, cache_key: str) -> None:
        client = self._get_client()
        client.collection("cache").document(cache_key).delete()