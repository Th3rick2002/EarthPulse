"""SQLite repository implementation for local development."""

import sqlite3
import json
from pathlib import Path
from datetime import date, datetime
from typing import Optional
from contextlib import contextmanager

from app.repositories.base import BaseRepository, BaseCacheRepository
from app.schemas.series import Observation, Coverage, Analysis


DB_PATH = Path("backend/data/trendscope.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_db_connection():
    """Get SQLite connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database schema."""
    with get_db_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS observations (
                variable_id TEXT NOT NULL,
                region_id TEXT NOT NULL,
                period_start TEXT NOT NULL,  -- ISO date
                value REAL NOT NULL,
                quality TEXT NOT NULL,
                unit TEXT NOT NULL,
                source_provider TEXT NOT NULL,
                source_product TEXT NOT NULL,
                source_id TEXT NOT NULL,
                fetched_at TEXT NOT NULL,  -- ISO datetime
                PRIMARY KEY (variable_id, region_id, period_start, source_provider, source_product)
            );

            CREATE INDEX IF NOT EXISTS idx_obs_var_region_date
                ON observations (variable_id, region_id, period_start);

            CREATE TABLE IF NOT EXISTS cache (
                cache_key TEXT PRIMARY KEY,
                variable_id TEXT NOT NULL,
                region_id TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                observations_json TEXT NOT NULL,
                coverage_json TEXT NOT NULL,
                analysis_json TEXT,
                fetched_at TEXT NOT NULL,
                expires_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_cache_expires ON cache (expires_at);
        """)
        conn.commit()


class SQLiteRepository(BaseRepository):
    """SQLite-backed observation repository."""

    def __init__(self):
        init_db()

    async def get_observations(
        self,
        variable_id: str,
        region_id: str,
        start_date: date,
        end_date: date,
    ) -> list[Observation]:
        with get_db_connection() as conn:
            rows = conn.execute(
                """
                SELECT period_start, value, quality
                FROM observations
                WHERE variable_id = ? AND region_id = ?
                  AND period_start >= ? AND period_start <= ?
                ORDER BY period_start
                """,
                (variable_id, region_id, start_date.isoformat(), end_date.isoformat()),
            ).fetchall()

        return [
            Observation(
                date=date.fromisoformat(row["period_start"]),
                value=row["value"],
                quality=row["quality"],
            )
            for row in rows
        ]

    async def save_observations(
        self,
        variable_id: str,
        region_id: str,
        observations: list[Observation],
    ) -> None:
        if not observations:
            return

        variable = variable_id  # In real impl, fetch from catalog
        # For now, we need source info - would come from catalog
        with get_db_connection() as conn:
            for obs in observations:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO observations
                    (variable_id, region_id, period_start, value, quality, unit,
                     source_provider, source_product, source_id, fetched_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        variable_id,
                        region_id,
                        obs.date.isoformat(),
                        obs.value,
                        obs.quality.value,
                        "index",  # Would come from variable catalog
                        "mock",
                        "mock",
                        "mock",
                        datetime.utcnow().isoformat(),
                    ),
                )
            conn.commit()


class SQLiteCacheRepository(BaseCacheRepository):
    """SQLite-backed query cache repository."""

    def __init__(self):
        init_db()

    def _make_cache_key(
        self,
        variable_id: str,
        region_id: str,
        start_date: date,
        end_date: date,
        source_provider: str,
        source_product: str,
    ) -> str:
        return f"{variable_id}:{region_id}:{start_date}:{end_date}:{source_provider}:{source_product}"

    async def get_cached_series(
        self,
        cache_key: str,
    ) -> tuple[list[Observation], Coverage, Analysis | None] | None:
        with get_db_connection() as conn:
            row = conn.execute(
                """
                SELECT observations_json, coverage_json, analysis_json, expires_at
                FROM cache WHERE cache_key = ?
                """,
                (cache_key,),
            ).fetchone()

        if not row:
            return None

        # Check expiration
        expires_at = datetime.fromisoformat(row["expires_at"])
        if datetime.utcnow() > expires_at:
            await self.invalidate(cache_key)
            return None

        observations = [
            Observation(
                date=date.fromisoformat(o["date"]),
                value=o["value"],
                quality=o["quality"],
            )
            for o in json.loads(row["observations_json"])
        ]
        coverage = Coverage(**json.loads(row["coverage_json"]))
        analysis = Analysis(**json.loads(row["analysis_json"])) if row["analysis_json"] else None

        return observations, coverage, analysis

    async def set_cached_series(
        self,
        cache_key: str,
        observations: list[Observation],
        coverage: Coverage,
        analysis: Analysis | None,
        ttl_seconds: int = 86400,
    ) -> None:
        fetched_at = datetime.utcnow()
        expires_at = datetime.fromtimestamp(fetched_at.timestamp() + ttl_seconds)

        # Parse variable_id, region_id, dates from cache_key for indexing
        parts = cache_key.split(":")
        variable_id = parts[0] if len(parts) > 0 else ""
        region_id = parts[1] if len(parts) > 1 else ""
        start_date = parts[2] if len(parts) > 2 else ""
        end_date = parts[3] if len(parts) > 3 else ""

        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO cache
                (cache_key, variable_id, region_id, start_date, end_date,
                 observations_json, coverage_json, analysis_json, fetched_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    cache_key,
                    variable_id,
                    region_id,
                    start_date,
                    end_date,
                    json.dumps([o.model_dump(mode="json") for o in observations]),
                    json.dumps(coverage.model_dump(mode="json")),
                    json.dumps(analysis.model_dump(mode="json")) if analysis else None,
                    fetched_at.isoformat(),
                    expires_at.isoformat(),
                ),
            )
            conn.commit()

    async def invalidate(self, cache_key: str) -> None:
        with get_db_connection() as conn:
            conn.execute("DELETE FROM cache WHERE cache_key = ?", (cache_key,))
            conn.commit()


# Initialize on import
init_db()