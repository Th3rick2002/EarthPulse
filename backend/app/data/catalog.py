"""MVP catalog of variables and regions with validated metadata."""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class VariableSource:
    """Source/product metadata for a variable."""
    provider: Literal["planetary-computer", "meteomatics"]
    product: str
    source_id: str
    native_unit: str
    scale_factor: float | None = None
    aggregation: Literal["mean", "sum"] = "mean"
    resolution: str = ""
    access_method: str = ""


@dataclass(frozen=True)
class Variable:
    """Earth science variable with canonical metadata."""
    id: str
    name: str
    definition: str
    category: str
    canonical_unit: str
    min_years: int
    frequency: Literal["monthly"]
    source: VariableSource
    supported_region_ids: list[str]


@dataclass(frozen=True)
class Region:
    """Predefined region with WGS84 bbox and variable allowlist."""
    id: str
    name: str
    description: str
    type: Literal["predefined", "custom"]
    bbox: tuple[float, float, float, float]  # lat_min, lat_max, lon_min, lon_max
    crs: Literal["EPSG:4326"]
    supported_variable_ids: list[str]


# Variable sources
NDVI_SOURCE = VariableSource(
    provider="planetary-computer",
    product="modis-13Q1-061",
    source_id="250m_16_days_NDVI",
    native_unit="index",
    scale_factor=0.0001,
    aggregation="mean",
    resolution="250m / 16-day",
    access_method="STAC API / rasterio",
)

AIR_TEMP_SOURCE = VariableSource(
    provider="meteomatics",
    product="ecmwf-era5",
    source_id="t_2m:C",
    native_unit="°C",
    aggregation="mean",
    resolution="~30km / hourly",
    access_method="Meteomatics API",
)

PRECIP_SOURCE = VariableSource(
    provider="meteomatics",
    product="chc-chirps3",
    source_id="precip_24h:mm",
    native_unit="mm",
    aggregation="sum",
    resolution="~5km / daily",
    access_method="Meteomatics API",
)

# Variables catalog
VARIABLES: dict[str, Variable] = {
    "ndvi": Variable(
        id="ndvi",
        name="NDVI (Normalized Difference Vegetation Index)",
        definition="Vegetation health index from MODIS surface reflectance. Values range -1 to 1; higher = greener.",
        category="vegetation",
        canonical_unit="index",
        min_years=5,
        frequency="monthly",
        source=NDVI_SOURCE,
        supported_region_ids=["amazon"],
    ),
    "air_temperature": Variable(
        id="air_temperature",
        name="Air Temperature (2m)",
        definition="Near-surface air temperature from ERA5 reanalysis. Monthly mean of hourly values.",
        category="temperature",
        canonical_unit="°C",
        min_years=5,
        frequency="monthly",
        source=AIR_TEMP_SOURCE,
        supported_region_ids=["arctic"],
    ),
    "precipitation": Variable(
        id="precipitation",
        name="Precipitation",
        definition="Total monthly precipitation from CHIRPS satellite-gauge blend. Sum of daily 24h accumulations.",
        category="precipitation",
        canonical_unit="mm",
        min_years=5,
        frequency="monthly",
        source=PRECIP_SOURCE,
        supported_region_ids=["amazon"],
    ),
    # land_surface_temperature deferred per spec
}

# Regions catalog (WGS84: lat_min, lat_max, lon_min, lon_max)
REGIONS: dict[str, Region] = {
    "amazon": Region(
        id="amazon",
        name="Amazon Basin",
        description="Amazon rainforest extent for vegetation and precipitation monitoring.",
        type="predefined",
        bbox=(-20.0, 5.0, -80.0, -45.0),  # lat_min, lat_max, lon_min, lon_max
        crs="EPSG:4326",
        supported_variable_ids=["ndvi", "precipitation"],
    ),
    "arctic": Region(
        id="arctic",
        name="Arctic Circle",
        description="High-latitude region for air temperature trend monitoring (crosses antimeridian).",
        type="predefined",
        bbox=(66.5, 90.0, -180.0, 180.0),  # Full longitudinal span
        crs="EPSG:4326",
        supported_variable_ids=["air_temperature"],
    ),
}


def get_variable(var_id: str) -> Variable | None:
    """Get variable by ID."""
    return VARIABLES.get(var_id)


def get_region(region_id: str) -> Region | None:
    """Get region by ID."""
    return REGIONS.get(region_id)


def list_variables() -> list[Variable]:
    """List all variables."""
    return list(VARIABLES.values())


def list_regions() -> list[Region]:
    """List all regions."""
    return list(REGIONS.values())


def validate_variable_region(var_id: str, region_id: str) -> tuple[bool, str | None]:
    """Check if variable is supported in region."""
    var = get_variable(var_id)
    region = get_region(region_id)
    if not var:
        return False, f"Variable '{var_id}' not found"
    if not region:
        return False, f"Region '{region_id}' not found"
    if region_id not in var.supported_region_ids:
        return False, f"Variable '{var_id}' not supported in region '{region_id}'"
    return True, None


def bbox_to_provider_format(bbox: tuple[float, float, float, float], provider: str) -> dict:
    """Convert internal bbox (lat_min, lat_max, lon_min, lon_max) to provider-specific format."""
    lat_min, lat_max, lon_min, lon_max = bbox
    if provider == "planetary-computer":
        # Planetary Computer STAC expects [lon_min, lat_min, lon_max, lat_max]
        return {"bbox": [lon_min, lat_min, lon_max, lat_max]}
    elif provider == "meteomatics":
        # Meteomatics expects lat,lon format for bbox queries
        return {
            "lat_min": lat_min,
            "lat_max": lat_max,
            "lon_min": lon_min,
            "lon_max": lon_max,
        }
    return {"bbox": [lon_min, lat_min, lon_max, lat_max]}
