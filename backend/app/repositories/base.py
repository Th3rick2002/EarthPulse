"""Base repository interfaces."""

from abc import ABC, abstractmethod
from datetime import date
from typing import Protocol
from app.schemas.series import Observation, Coverage, Analysis


class Repository(Protocol):
    """Protocol for series data repository."""

    async def get_observations(
        self,
        variable_id: str,
        region_id: str,
        start_date: date,
        end_date: date,
    ) -> list[Observation]:
        """Retrieve cached observations."""
        ...

    async def save_observations(
        self,
        variable_id: str,
        region_id: str,
        observations: list[Observation],
    ) -> None:
        """Store observations."""
        ...


class CacheRepository(Protocol):
    """Protocol for query cache repository."""

    async def get_cached_series(
        self,
        cache_key: str,
    ) -> tuple[list[Observation], Coverage, Analysis | None] | None:
        """Get cached series response."""
        ...

    async def set_cached_series(
        self,
        cache_key: str,
        observations: list[Observation],
        coverage: Coverage,
        analysis: Analysis | None,
        ttl_seconds: int = 86400,  # 24 hours
    ) -> None:
        """Cache series response."""
        ...

    async def invalidate(self, cache_key: str) -> None:
        """Invalidate cache entry."""
        ...


class BaseRepository(ABC):
    """Abstract base repository."""

    @abstractmethod
    async def get_observations(
        self,
        variable_id: str,
        region_id: str,
        start_date: date,
        end_date: date,
    ) -> list[Observation]:
        pass

    @abstractmethod
    async def save_observations(
        self,
        variable_id: str,
        region_id: str,
        observations: list[Observation],
    ) -> None:
        pass


class BaseCacheRepository(ABC):
    """Abstract base cache repository."""

    @abstractmethod
    async def get_cached_series(
        self,
        cache_key: str,
    ) -> tuple[list[Observation], Coverage, Analysis | None] | None:
        pass

    @abstractmethod
    async def set_cached_series(
        self,
        cache_key: str,
        observations: list[Observation],
        coverage: Coverage,
        analysis: Analysis | None,
        ttl_seconds: int = 86400,
    ) -> None:
        pass

    @abstractmethod
    async def invalidate(self, cache_key: str) -> None:
        pass