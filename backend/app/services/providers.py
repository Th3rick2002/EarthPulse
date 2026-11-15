"""Data provider clients and series fetching."""

from datetime import date, timedelta
import asyncio
import csv
import io
import math
import re
import threading
import time
from typing import Protocol
from dataclasses import dataclass
import httpx
from calendar import monthrange
from app.data.catalog import get_variable, get_region


@dataclass
class MonthlyPoint:
    """Internal representation of a monthly data point."""
    date: date
    value: float
    quality: str  # "observed", "interpolated", "missing"


class ProviderError(Exception):
    """Provider failure that can be translated to the public API error contract."""

    def __init__(self, provider: str, code: str, status_code: int, message: str):
        super().__init__(message)
        self.provider = provider
        self.code = code
        self.status_code = status_code


class DataProvider(Protocol):
    """Protocol for data provider clients."""

    async def fetch_monthly(
        self,
        variable_id: str,
        region_bbox: tuple[float, float, float, float],
        start_date: date,
        end_date: date,
    ) -> list[MonthlyPoint]:
        """Fetch monthly aggregated observations."""
        ...


class MeteomaticsClient:
    """Fetch daily regional aggregates and roll them up to calendar months."""

    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        base_url: str = "https://api.meteomatics.com",
        source_overrides: dict[str, str] | None = None,
    ):
        self.username = username
        self.password = password
        self.base_url = base_url.rstrip("/")
        self.source_overrides = source_overrides or {}
        self._session: httpx.AsyncClient | None = None

    async def _get_session(self):
        """Get or create HTTP session."""
        if self._session is None:
            self._session = httpx.AsyncClient(
                auth=(self.username, self.password) if self.username else None,
                timeout=310.0,
            )
        return self._session

    async def close(self) -> None:
        """Close the pooled HTTP session when the API process shuts down."""
        if self._session is not None:
            await self._session.aclose()
            self._session = None

    @staticmethod
    def _polygon_for_bbox(region_bbox: tuple[float, float, float, float]) -> str:
        """Encode a bbox as Meteomatics polygons (lat,lon; separated with U)."""
        lat_min, lat_max, lon_min, lon_max = region_bbox

        # A full-longitude polar cap cannot be represented as one ordinary bbox.
        # Unite adjacent wedges so the area does not collapse at the antimeridian.
        if lon_max - lon_min >= 359.0:
            segments = 12
            step = (lon_max - lon_min) / segments
            polygons = []
            for index in range(segments):
                west = lon_min + index * step
                east = lon_min + (index + 1) * step
                polygons.append(
                    f"{lat_min},{west}_{lat_min},{east}_{lat_max},{east}_{lat_max},{west}"
                )
            return "U".join(polygons) + ":mean"

        return (
            f"{lat_min},{lon_min}_{lat_min},{lon_max}_"
            f"{lat_max},{lon_max}_{lat_max},{lon_min}:mean"
        )

    @staticmethod
    def _parse_csv_values(body: str, parameter: str) -> dict[date, float | None]:
        """Read Meteomatics polygon CSV into UTC date/value pairs."""
        reader = csv.DictReader(io.StringIO(body), delimiter=";")
        if not reader.fieldnames:
            raise ValueError("Meteomatics returned an empty CSV response")
        reader.fieldnames = [name.lstrip("\ufeff") for name in reader.fieldnames]

        date_column = next(
            (name for name in reader.fieldnames if name.strip().lower() in {"validdate", "date"}),
            None,
        )
        value_column = next(
            (name for name in reader.fieldnames if name.strip() == parameter),
            None,
        )
        if date_column is None or value_column is None:
            raise ValueError("Meteomatics response is missing the date or parameter column")

        values: dict[date, float | None] = {}
        for row in reader:
            raw_date = (row.get(date_column) or "").strip()
            if not raw_date:
                continue
            # Meteomatics emits UTC timestamps, usually ending in Z.
            observed_on = date.fromisoformat(raw_date[:10])
            raw_value = (row.get(value_column) or "").strip()
            try:
                parsed = float(raw_value)
                is_reserved = parsed in {-999, -888, -777, -666}
                values[observed_on] = parsed if math.isfinite(parsed) and not is_reserved else None
            except ValueError:
                values[observed_on] = None
        return values

    async def fetch_monthly(
        self,
        variable_id: str,
        region_bbox: tuple[float, float, float, float],
        start_date: date,
        end_date: date,
    ) -> list[MonthlyPoint]:
        """Fetch daily area statistics and aggregate them into monthly values.

        Meteomatics interval values are right-bounded. Querying midnight on the
        day after each observation makes each daily value correspond to its
        calendar day, including the final day of the requested range.
        """
        variable = get_variable(variable_id)
        if variable is None:
            raise ValueError(f"Variable {variable_id} not found")
        if variable.source.provider != "meteomatics":
            raise ValueError(f"Variable {variable_id} is not provided by Meteomatics")
        if not self.username or not self.password:
            raise ValueError("Meteomatics credentials are not configured")
        if start_date > end_date:
            raise ValueError("start_date must be before end_date")

        parameter = variable.source.source_id
        query_start = start_date + timedelta(days=1)
        query_end = end_date + timedelta(days=1)
        time_range = (
            f"{query_start.isoformat()}T00:00:00Z--"
            f"{query_end.isoformat()}T00:00:00Z:P1D"
        )
        location = self._polygon_for_bbox(region_bbox)
        url = f"{self.base_url}/{time_range}/{parameter}/{location}/csv"
        session = await self._get_session()
        response = await session.get(
            url,
            params={
                "source": self.source_overrides.get(variable_id, variable.source.product),
                "polygon_sampling": "model_grid",
                "on_invalid": "fill_with_invalid",
            },
        )
        response.raise_for_status()

        daily_values = self._parse_csv_values(response.text, parameter)
        monthly_values: dict[date, list[float | None]] = {}
        current = date(start_date.year, start_date.month, 1)
        while current <= end_date:
            days_in_month = monthrange(current.year, current.month)[1]
            month_observations: list[float | None] = []
            for day in range(1, days_in_month + 1):
                calendar_day = date(current.year, current.month, day)
                if start_date <= calendar_day <= end_date:
                    # The API timestamp is the right edge of the 24-hour period.
                    month_observations.append(daily_values.get(calendar_day + timedelta(days=1)))
            monthly_values[current] = month_observations
            current = date(current.year + (current.month == 12), current.month % 12 + 1, 1)

        points: list[MonthlyPoint] = []
        for month, observations in monthly_values.items():
            expected_days = monthrange(month.year, month.month)[1]
            valid_values = [value for value in observations if value is not None]
            # Do not turn partial area coverage into a complete monthly datum.
            if len(observations) != expected_days or len(valid_values) != expected_days:
                points.append(MonthlyPoint(date=month, value=0.0, quality="missing"))
                continue

            if variable.source.aggregation == "sum":
                monthly_value = sum(valid_values)
            else:
                monthly_value = sum(valid_values) / len(valid_values)
            points.append(MonthlyPoint(
                date=month,
                value=round(monthly_value, 4),
                quality="observed",
            ))
        return points


class PlanetaryComputerClient:
    """Microsoft Planetary Computer client for MODIS 16-day NDVI COGs."""

    _cache_lock = threading.Lock()
    _series_cache: dict[str, tuple[float, list[MonthlyPoint]]] = {}
    _cache_ttl_seconds = 24 * 60 * 60

    def __init__(self):
        self.stac_url = "https://planetarycomputer.microsoft.com/api/stac/v1/"

    async def fetch_monthly(
        self,
        variable_id: str,
        region_bbox: tuple[float, float, float, float],
        start_date: date,
        end_date: date,
    ) -> list[MonthlyPoint]:
        """Fetch monthly NDVI from regional GeoTIFFs served by Planetary Computer."""
        import numpy as np
        import pystac_client
        import rasterio
        from rasterio.io import MemoryFile

        variable = get_variable(variable_id)
        if variable is None:
            raise ValueError(f"Variable {variable_id} not found")
        if variable.source.provider != "planetary-computer":
            raise ValueError(f"Variable {variable_id} is not provided by Planetary Computer")
        if start_date > end_date:
            raise ValueError("start_date must be before end_date")

        cache_key = (
            f"{variable_id}:{region_bbox}:{start_date.isoformat()}:{end_date.isoformat()}"
        )
        with self._cache_lock:
            cached = self._series_cache.get(cache_key)
            if cached and cached[0] > time.monotonic():
                return [MonthlyPoint(point.date, point.value, point.quality) for point in cached[1]]
            self._series_cache.pop(cache_key, None)

        scenes = await asyncio.to_thread(
            self._search_scenes,
            variable,
            region_bbox,
            start_date,
            end_date,
            pystac_client,
        )
        scale = variable.source.scale_factor or 1.0
        lat_min, lat_max, lon_min, lon_max = region_bbox
        data_api = "https://planetarycomputer.microsoft.com/api/data/v1"
        limits = httpx.Limits(max_connections=32, max_keepalive_connections=32)
        timeout = httpx.Timeout(90.0, connect=20.0)
        semaphore = asyncio.Semaphore(32)

        async def read_scene(client: httpx.AsyncClient, scene):
            month, item_id, item_bbox = scene
            west = max(lon_min, item_bbox[0])
            south = max(lat_min, item_bbox[1])
            east = min(lon_max, item_bbox[2])
            north = min(lat_max, item_bbox[3])
            if west >= east or south >= north:
                return month, 0.0, 0

            polygon = {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [west, south], [east, south], [east, north],
                        [west, north], [west, south],
                    ]],
                },
                "properties": {},
            }
            params = [
                ("collection", variable.source.product),
                ("item", item_id),
                ("assets", variable.source.source_id),
                ("assets", "250m_16_days_pixel_reliability"),
                ("asset_as_band", "true"),
                ("coord_crs", "EPSG:4326"),
                ("resampling", "nearest"),
            ]

            async with semaphore:
                response = None
                for attempt in range(4):
                    response = await client.post(
                        f"{data_api}/item/feature/256x256.tif",
                        params=params,
                        json=polygon,
                    )
                    if response.status_code not in {429, 500, 502, 503, 504}:
                        response.raise_for_status()
                        break
                    if attempt == 3:
                        response.raise_for_status()
                    retry_after = response.headers.get("Retry-After")
                    delay = float(retry_after) if retry_after and retry_after.isdigit() else 2**attempt
                    await asyncio.sleep(delay)

            with MemoryFile(response.content) as memory_file:
                with memory_file.open() as raster:
                    if raster.count < 2:
                        raise ValueError(f"Planetary Computer item {item_id} returned fewer than two bands")
                    ndvi_values = raster.read(1).astype(np.float32)
                    reliability = raster.read(2)
                    alpha = raster.read(3) if raster.count >= 3 else np.full(ndvi_values.shape, 255)
                    valid = (
                        (ndvi_values >= -2000)
                        & (ndvi_values <= 10000)
                        & (reliability == 0)
                        & (alpha > 0)
                    )
                    if not np.any(valid):
                        return month, 0.0, 0
                    # The data API returns these crops in EPSG:4326. Weight
                    # samples by approximate ground area so rows at different
                    # latitudes and crops with different cell sizes are comparable.
                    row_latitudes = (
                        raster.transform.f
                        + (np.arange(raster.height, dtype=np.float64) + 0.5)
                        * raster.transform.e
                    )
                    pixel_area = abs(raster.transform.a * raster.transform.e)
                    row_weights = pixel_area * np.cos(np.deg2rad(row_latitudes))
                    weights = np.broadcast_to(row_weights[:, None], valid.shape)
                    return (
                        month,
                        float(np.sum(ndvi_values[valid] * weights[valid], dtype=np.float64)),
                        float(np.sum(weights[valid], dtype=np.float64)),
                    )

        monthly_sums: dict[date, float] = {}
        monthly_counts: dict[date, float] = {}
        async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:
            results = await asyncio.gather(*(read_scene(client, scene) for scene in scenes))
        for month, scene_sum, scene_count in results:
            monthly_sums[month] = monthly_sums.get(month, 0.0) + scene_sum
            monthly_counts[month] = monthly_counts.get(month, 0) + scene_count

        points: list[MonthlyPoint] = []
        current = date(start_date.year, start_date.month, 1)
        while current <= end_date:
            count = monthly_counts.get(current, 0)
            if count == 0:
                points.append(MonthlyPoint(date=current, value=0.0, quality="missing"))
            else:
                points.append(MonthlyPoint(
                    date=current,
                    value=round(monthly_sums[current] / count * scale, 4),
                    quality="observed",
                ))
            current = date(current.year + (current.month == 12), current.month % 12 + 1, 1)

        with self._cache_lock:
            self._series_cache[cache_key] = (
                time.monotonic() + self._cache_ttl_seconds,
                [MonthlyPoint(point.date, point.value, point.quality) for point in points],
            )
        return points

    def _search_scenes(
        self,
        variable,
        region_bbox: tuple[float, float, float, float],
        start_date: date,
        end_date: date,
        pystac_client,
    ) -> list[tuple[date, str, list[float]]]:
        lat_min, lat_max, lon_min, lon_max = region_bbox
        catalog = pystac_client.Client.open(self.stac_url)
        search = catalog.search(
            collections=[variable.source.product],
            bbox=[lon_min, lat_min, lon_max, lat_max],
            datetime=(
                f"{start_date.isoformat()}T00:00:00Z/"
                f"{end_date.isoformat()}T23:59:59Z"
            ),
            query={"platform": {"eq": "terra"}},
            # The STAC service defaults to small pages; a five-year Amazon
            # search spans more than 1,500 MODIS granules. Larger pages avoid
            # dozens of sequential pagination round trips.
            limit=1000,
        )

        # MOD13Q1 supplies 16-day composites, commonly two per month. For a
        # monthly product, use the composite closest to mid-month per MODIS
        # tile, rather than fetching both composites for every tile.
        monthly_tile_scenes: dict[tuple[date, str], tuple[int, tuple]] = {}
        for item in search.items():
            scene_date = item.datetime.date() if item.datetime is not None else None
            if scene_date is None:
                # MODIS items describe a 16-day composite interval and may set
                # `datetime` to null while supplying `start_datetime` instead.
                interval_start = item.properties.get("start_datetime")
                if interval_start:
                    scene_date = date.fromisoformat(str(interval_start)[:10])
            if scene_date is None:
                continue
            ndvi_asset = item.assets.get(variable.source.source_id)
            qa_asset = item.assets.get("250m_16_days_pixel_reliability")
            if ndvi_asset is not None and qa_asset is not None:
                tile_match = re.search(r"h\d{2}v\d{2}", item.id)
                tile_id = tile_match.group(0) if tile_match else item.id
                month = date(scene_date.year, scene_date.month, 1)
                distance_from_midmonth = abs(scene_date.day - 15)
                scene = (month, item.id, item.bbox)
                key = (month, tile_id)
                previous = monthly_tile_scenes.get(key)
                if previous is None or distance_from_midmonth < previous[0]:
                    monthly_tile_scenes[key] = (distance_from_midmonth, scene)

        return [entry[1] for entry in monthly_tile_scenes.values()]


# Mock provider for development
class MockProvider:
    """Mock provider returning synthetic data for development."""

    async def fetch_monthly(
        self,
        variable_id: str,
        region_bbox: tuple[float, float, float, float],
        start_date: date,
        end_date: date,
    ) -> list[MonthlyPoint]:
        """Generate synthetic monthly observations."""
        import random

        points = []
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

            # Mostly "observed", occasionally "interpolated", rarely "missing"
            quality_roll = random.random()
            if quality_roll < 0.95:
                quality = "observed"
            elif quality_roll < 0.98:
                quality = "interpolated"
            else:
                quality = "missing"

            points.append(MonthlyPoint(
                date=current,
                value=round(value, 4),
                quality=quality,
            ))

            if current.month == 12:
                current = date(current.year + 1, 1, 1)
            else:
                current = date(current.year, current.month + 1, 1)

        return points


# Provider instances (singleton pattern)
_meteomatics_client: MeteomaticsClient | None = None
_planetary_computer_client: PlanetaryComputerClient | None = None


def get_meteomatics_client() -> MeteomaticsClient:
    """Get or create Meteomatics client."""
    global _meteomatics_client
    if _meteomatics_client is None:
        import os
        _meteomatics_client = MeteomaticsClient(
            username=os.getenv("METEOMATICS_USERNAME"),
            password=os.getenv("METEOMATICS_PASSWORD"),
            base_url=os.getenv("METEOMATICS_BASE_URL", "https://api.meteomatics.com"),
            source_overrides={
                "air_temperature": os.getenv("METEOMATICS_TEMPERATURE_SOURCE", "ecmwf-era5"),
                "precipitation": os.getenv("METEOMATICS_PRECIPITATION_SOURCE", "chc-chirps3"),
            },
        )
    return _meteomatics_client


def get_planetary_computer_client() -> PlanetaryComputerClient:
    """Get or create Planetary Computer client."""
    global _planetary_computer_client
    if _planetary_computer_client is None:
        _planetary_computer_client = PlanetaryComputerClient()
    return _planetary_computer_client


async def close_provider_clients() -> None:
    """Release provider network resources during application shutdown."""
    if _meteomatics_client is not None:
        await _meteomatics_client.close()


async def fetch_monthly_series(
    variable_id: str,
    region_id: str,
    start_date: date,
    end_date: date,
    region_bbox: tuple[float, float, float, float] | None = None,
) -> list[MonthlyPoint]:
    """
    Fetch monthly aggregated series for a variable/region.

    Routes to the configured provider and surfaces failures instead of returning
    synthetic observations as if they were real measurements.
    """
    variable = get_variable(variable_id)
    if not variable:
        raise ValueError(f"Variable {variable_id} not found")

    provider = variable.source.provider
    if region_bbox is None:
        region = get_region(region_id)
        if not region:
            raise ValueError(f"Region {region_id} not found")
        bbox = region.bbox
    else:
        bbox = region_bbox

    if provider == "meteomatics":
        client = get_meteomatics_client()
        if not client.username or not client.password:
            raise ProviderError(
                provider="meteomatics",
                code="PROVIDER_UNAVAILABLE",
                status_code=503,
                message="Meteomatics credentials are not configured",
            )
        return await _fetch_from_provider(client, provider, variable_id, bbox, start_date, end_date)

    elif provider == "planetary-computer":
        client = get_planetary_computer_client()
        return await _fetch_from_provider(client, provider, variable_id, bbox, start_date, end_date)

    raise ProviderError(
        provider=str(provider),
        code="PROVIDER_UNAVAILABLE",
        status_code=503,
        message="No provider is configured for this variable",
    )


async def _fetch_from_provider(
    client: DataProvider,
    provider: str,
    variable_id: str,
    bbox: tuple[float, float, float, float],
    start_date: date,
    end_date: date,
) -> list[MonthlyPoint]:
    try:
        return await client.fetch_monthly(variable_id, bbox, start_date, end_date)
    except NotImplementedError as exc:
        raise ProviderError(
            provider=provider,
            code="PROVIDER_UNAVAILABLE",
            status_code=503,
            message=f"The {provider} integration is not implemented yet",
        ) from exc
    except (httpx.TimeoutException, TimeoutError) as exc:
        raise ProviderError(
            provider=provider,
            code="PROVIDER_TIMEOUT",
            status_code=504,
            message=f"The {provider} request timed out",
        ) from exc
    except httpx.HTTPStatusError as exc:
        raise ProviderError(
            provider=provider,
            code="PROVIDER_ERROR",
            status_code=502,
            message=f"The {provider} request failed with status {exc.response.status_code}",
        ) from exc
    except Exception as exc:
        raise ProviderError(
            provider=provider,
            code="PROVIDER_ERROR",
            status_code=502,
            message=f"The {provider} request failed",
        ) from exc
