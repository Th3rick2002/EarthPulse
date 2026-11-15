"""In-process jobs for provider queries that exceed a normal HTTP request."""

from dataclasses import dataclass
from datetime import date
import asyncio
import time
from uuid import uuid4

from app.services.providers import MonthlyPoint, ProviderError


@dataclass
class SeriesJob:
    job_id: str
    query: tuple[str, str, date, date]
    status: str = "processing"
    points: list[MonthlyPoint] | None = None
    error: Exception | None = None
    expires_at: float = 0


_jobs: dict[str, SeriesJob] = {}
_jobs_by_query: dict[str, str] = {}
_retention_seconds = 24 * 60 * 60


def get_or_start_series_job(
    query_key: str,
    query: tuple[str, str, date, date],
    factory,
) -> SeriesJob:
    """Reuse a completed/running query or start one background task."""
    now = time.monotonic()
    job_id = _jobs_by_query.get(query_key)
    existing = _jobs.get(job_id) if job_id else None
    if existing and (
        existing.status == "processing"
        or (existing.status == "completed" and existing.expires_at > now)
    ):
        return existing

    job = SeriesJob(job_id=uuid4().hex, query=query)
    _jobs[job.job_id] = job
    _jobs_by_query[query_key] = job.job_id

    async def run() -> None:
        try:
            job.points = await factory()
            job.status = "completed"
        except Exception as exc:
            job.error = exc
            job.status = "failed"
        finally:
            job.expires_at = time.monotonic() + _retention_seconds

    asyncio.create_task(run())
    return job


def get_series_job(job_id: str) -> SeriesJob | None:
    job = _jobs.get(job_id)
    if job and job.expires_at and job.expires_at <= time.monotonic():
        _jobs.pop(job_id, None)
        return None
    return job
