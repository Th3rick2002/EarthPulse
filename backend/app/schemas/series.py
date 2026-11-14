"""Schemas for GET /series endpoint."""

from pydantic import BaseModel, Field, field_validator
from typing import Literal
from datetime import date


class SeriesRequest(BaseModel):
    """Query parameters for GET /series."""
    variable_id: str = Field(..., alias="variableId", description="Variable identifier from catalog")
    region_id: str = Field(..., alias="regionId", description="Region identifier from catalog")
    start_date: date = Field(..., alias="startDate", description="Start date (YYYY-MM-DD)")
    end_date: date = Field(..., alias="endDate", description="End date (YYYY-MM-DD)")

    @field_validator("end_date")
    @classmethod
    def end_after_start(cls, v: date, info) -> date:
        if "start_date" in info.data and v <= info.data["start_date"]:
            raise ValueError("endDate must be after startDate")
        return v

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "variableId": "ndvi",
                "regionId": "amazon",
                "startDate": "2018-01-01",
                "endDate": "2023-12-31",
            }
        },
    }


class Observation(BaseModel):
    """Single monthly observation."""
    period_start: date = Field(..., description="Period start date (YYYY-MM-DD)", alias="date")
    value: float
    quality: str = "observed"


class Coverage(BaseModel):
    """Data coverage assessment."""
    start: date
    end: date
    valid_observations: int = Field(..., alias="validObservations")
    expected_observations: int = Field(..., alias="expectedObservations")
    coverage_ratio: float = Field(..., alias="coverageRatio", ge=0.0, le=1.0)
    insufficient_reason: str | None = Field(None, alias="insufficientReason")

    model_config = {"populate_by_name": True}


class SourceInfo(BaseModel):
    """Data source identification."""
    provider: Literal["planetary-computer", "meteomatics"]
    product: str
    source_id: str = Field(..., alias="sourceId")

    model_config = {"populate_by_name": True}


class Analysis(BaseModel):
    """Trend analysis result."""
    method: str = "mann-kendall"
    slope: float
    slope_unit: str = Field(..., alias="slopeUnit")
    p_value: float = Field(..., alias="pValue")
    significant: bool
    n_observations: int = Field(..., alias="nObservations")
    interpretation: str
    period_start: date = Field(..., alias="periodStart")
    period_end: date = Field(..., alias="periodEnd")

    model_config = {"populate_by_name": True}


# Forward references for VariableResponse and RegionResponse
class VariableRef(BaseModel):
    id: str
    name: str
    definition: str
    category: str
    canonical_unit: str
    min_years: int
    frequency: Literal["monthly"]
    source: dict
    supported_region_ids: list[str]


class RegionRef(BaseModel):
    id: str
    name: str
    description: str
    type: Literal["predefined", "custom"]
    bbox: tuple[float, float, float, float]
    crs: Literal["EPSG:4326"]
    supported_variable_ids: list[str]


class SeriesResponse(BaseModel):
    """Response for GET /series."""
    variable: VariableRef
    region: RegionRef
    source: SourceInfo
    unit: str
    frequency: Literal["monthly"]
    coverage: Coverage
    observations: list[Observation]
    analysis: Analysis | None = None

    model_config = {"populate_by_name": True}