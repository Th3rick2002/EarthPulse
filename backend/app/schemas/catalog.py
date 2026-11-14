"""Schemas for /variables and /regions endpoints."""

from pydantic import BaseModel, Field
from typing import Literal


class VariableSourceResponse(BaseModel):
    """Source/product metadata for a variable."""
    provider: Literal["planetary-computer", "meteomatics"]
    product: str
    source_id: str
    native_unit: str
    scale_factor: float | None = None
    aggregation: Literal["mean", "sum"]
    resolution: str
    access_method: str


class VariableResponse(BaseModel):
    """Variable catalog entry."""
    id: str
    name: str
    definition: str
    category: str
    canonical_unit: str
    min_years: int
    frequency: Literal["monthly"]
    source: VariableSourceResponse
    supported_region_ids: list[str]


class RegionResponse(BaseModel):
    """Region catalog entry."""
    id: str
    name: str
    description: str
    type: Literal["predefined", "custom"]
    bbox: tuple[float, float, float, float]  # lat_min, lat_max, lon_min, lon_max
    crs: Literal["EPSG:4326"]
    supported_variable_ids: list[str]


class VariablesListResponse(BaseModel):
    """Response for GET /variables."""
    variables: list[VariableResponse]


class RegionsListResponse(BaseModel):
    """Response for GET /regions."""
    regions: list[RegionResponse]