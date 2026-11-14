"""Data provider clients and series fetching."""

from datetime import date
from typing import Protocol
from app.data.catalog import get_variable, bbox_to_provider_format
from app.schemas.series import Observation


class DataProvider(Protocol):
    """Protocol for data provider clients."""

    async def fetch_monthly(
        self,
        variable_id: str,
        region_bbox: tuple[float, float, float, float],
        start_date: date,
        end_date: date,
    ) -> list[Observation]:
        """Fetch monthly aggregated observations."""
        ...


class MeteomaticsClient:
    """Meteomatics API client (skeleton for future implementation)."""

    def __init__(self, username: str | None = None, password: str | None = None):
        self.username = username
        self.password = password
        self.base_url = "https://api.meteomatics.com"
        self._session = None

    async def _get_session(self):
        """Get or create HTTP session."""
        if self._session is None:
            import httpx
            self._session = httpx.AsyncClient(
                auth=(self.username, self.password) if self.username else None,
                timeout=30.0,
            )
        return self._session

    async def fetch_monthly(
        self,
        variable_id: str,
        region_bbox: tuple[float, float, float, float],
        start_date: date,
        end_date: date,
    ) -> list[Observation]:
        """
        Fetch monthly data from Meteomatics.

        TODO: Implement actual Meteomatics API calls.
        Expected endpoint pattern:
        GET /{date_range}/{parameters}/{coordinates}/{format}
        """
        # Placeholder - will implement when credentials are available
        raise NotImplementedError("Meteomatics client not yet implemented")


class PlanetaryComputerClient:
    """Microsoft Planetary Computer STAC client (skeleton)."""

    def __init__(self):
        self.stac_url = "https://planetarycomputer.microsoft.com/api/stac/v1"

    async def fetch_monthly(
        self,
        variable_id: str,
        region_bbox: tuple[float, float, float, float],
        start_date: date,
        end_date: date,
    ) -> list[Observation]:
        """
        Fetch monthly data from Planetary Computer (MODIS NDVI).

        TODO: Implement actual STAC search and raster reading.
        Steps:
        1. Search STAC catalog for modis-13Q1-061 collection
        2. Filter by bbox and date range
        3. Read NDVI band from COGs using rasterio/rioxarray
        4. Spatial aggregate (mean over region)
        5. Temporal resample to monthly (mean of 16-day composites)
        6. Apply scale factor (0.0001)
        """
        # Placeholder - will implement when needed
        raise NotImplementedError("Planetary Computer client not yet implemented")


# Mock provider for development
class MockProvider:
    """Mock provider returning synthetic data for development."""

    async def fetch_monthly(
        self,
        variable_id: str,
        region_bbox: tuple[float, float, float, float],
        start_date: date,
        end_date: date,
    ) -> list[Observation]:
        """Generate synthetic monthly observations."""
        import random

        observations = []
        current = date(start_date.year, start_date.month, 1)

        base_values = {
            "ndvi": 0.65,
            "air_temperature": -10.0,
            "precipitation": 200.0,
        }
        base = base_values.get(variable_id, 0.0)

        seasonal = {
            "ndvi": lambda m: 0.1 * (1 if m in [3, 4, 5] else -0.5 if m in [9, 10, 11] else 0),
            "air_temperature": lambda m: 15 * (1 if m in [6, 7, 8] else -1 if m in [12, 1, 2] else 0),
            "precipitation": lambda m: 100 if m in [12, 1, 2, 3] else -50,
        }
        seasonal_fn = seasonal.get(variable_id, lambda m: 0)

        while current <= end_date:
            year_frac = (current.year - start_date.year) + (current.month - 1) / 12
            trend = 0.002 * year_frac * base
            value = base + trend + seasonal_fn(current.month) + random.uniform(-0.05 * abs(base), 0.05 * abs(base))

            if variable_id == "ndvi":
                value = max(-1.0, min(1.0, value))
            elif variable_id == "precipitation":
                value = max(0.0, value)

            observations.append(Observation(
                date=current,
                value=round(value, 4),
                quality="observed",
            ))

            if current.month == 12:
                current = date(current.year + 1, 1, 1)
            else:
                current = date(current.year, current.month + 1, 1)

        return observations


# Provider instances (singleton pattern)
_meteomatics_client: MeteomaticsClient | None = None
_planetary_computer_client: PlanetaryComputerClient | None = None
_mock_provider = MockProvider()


def get_meteomatics_client() -> MeteomaticsClient:
    """Get or create Meteomatics client."""
    global _meteomatics_client
    if _meteomatics_client is None:
        import os
        _meteomatics_client = MeteomaticsClient(
            username=os.getenv("METEOMATICS_USERNAME"),
            password=os.getenv("METEOMATICS_PASSWORD"),
        )
    return _meteomatics_client


def get_planetary_computer_client() -> PlanetaryComputerClient:
    """Get or create Planetary Computer client."""
    global _planetary_computer_client
    if _planetary_computer_client is None:
        _planetary_computer_client = PlanetaryComputerClient()
    return _planetary_computer_client


async def fetch_monthly_series(
    variable_id: str,
    region_id: str,
    start_date: date,
    end_date: date,
) -> list[Observation]:
    """
    Fetch monthly aggregated series for a variable/region.

    Routes to appropriate provider based on variable source.
    Falls back to mock provider if real client not configured.
    """
    variable = get_variable(variable_id)
    if not variable:
        raise ValueError(f"Variable {variable_id} not found")

    provider = variable.source.provider

    from app.data.catalog import get_region
    region = get_region(region_id)
    if not region:
        raise ValueError(f"Region {region_id} not found")

    bbox = region.bbox

    if provider == "meteomatics":
        client = get_meteomatics_client()
        # Check if credentials are configured
        if client.username and client.password:
            try:
                return await client.fetch_monthly(variable_id, bbox, start_date, end_date)
            except Exception:
                pass  # Fall through to mock
        return await _mock_provider.fetch_monthly(variable_id, bbox, start_date, end_date)

    elif provider == "planetary-computer":
        client = get_planetary_computer_client()
        try:
            return await client.fetch_monthly(variable_id, bbox, start_date, end_date)
        except Exception:
            pass  # Fall through to mock
        return await _mock_provider.fetch_monthly(variable_id, bbox, start_date, end_date)

    return await _mock_provider.fetch_monthly(variable_id, bbox, start_date, end_date)