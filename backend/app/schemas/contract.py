"""Pydantic models matching the canonical FE/BE contract.

This module defines the exact DTOs specified in the contract card.
Field names use camelCase via alias to match JSON contract exactly.
"""

from calendar import monthrange

from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from datetime import date, datetime
from typing import Literal, Optional
from uuid import uuid4


# --- Enums and constants ---

QualityValue = Literal["ok", "missing", "interpolated"]
RegionType = Literal["predefined", "custom"]


# --- Request/Response Wrappers ---

class DataWrapper(BaseModel):
    """Generic wrapper for successful responses: {data: ...}."""
    data: dict | list

    model_config = ConfigDict(populate_by_name=True)


class ErrorDetail(BaseModel):
    """Error detail object."""
    code: str
    message: str
    details: dict = Field(default_factory=dict)
    requestId: str = Field(default_factory=lambda: str(uuid4())[:8])

    model_config = ConfigDict(populate_by_name=True)


class ErrorResponse(BaseModel):
    """Standard error envelope: {error: {...}}."""
    error: ErrorDetail

    model_config = ConfigDict(populate_by_name=True)


# --- Entity DTOs ---

class VariableDTO(BaseModel):
    """Variable catalog entry per contract."""
    variableId: str
    name: str
    description: str
    unit: str
    source: str
    category: str
    minYears: int

    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class BBoxDTO(BaseModel):
    """Bounding box as object per contract."""
    latMin: float = Field(ge=-90, le=90)
    latMax: float = Field(ge=-90, le=90)
    lonMin: float = Field(ge=-180, le=180)
    lonMax: float = Field(ge=-180, le=180)

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    @model_validator(mode="after")
    def validate_latitude_order(self):
        if self.latMin >= self.latMax:
            raise ValueError("latMin must be less than latMax")
        return self


class RegionDTO(BaseModel):
    """Region catalog entry per contract."""
    regionId: str
    name: str
    bbox: BBoxDTO
    description: str
    type: RegionType

    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class TimeSeriesPointDTO(BaseModel):
    """Single monthly time series point per contract."""
    seriesId: str
    variableId: str
    regionId: str
    date: date
    value: Optional[float]
    quality: QualityValue

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    @field_validator("date")
    @classmethod
    def date_must_start_month(cls, value: date) -> date:
        if value.day != 1:
            raise ValueError("date must be the first day of the month")
        return value

    @model_validator(mode="after")
    def validate_value_quality(self):
        if (self.quality == "missing") != (self.value is None):
            raise ValueError("value must be null exactly when quality is missing")
        return self


class TrendAnalysisDTO(BaseModel):
    """Trend analysis result per contract."""
    analysisId: str
    variableId: str
    regionId: str
    startDate: date
    endDate: date
    slope: float
    pValue: float = Field(ge=0, le=1)
    significant: bool
    interpretation: str
    createdAt: datetime

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    @model_validator(mode="after")
    def validate_analysis(self):
        if self.startDate.day != 1 or self.endDate.day != monthrange(self.endDate.year, self.endDate.month)[1]:
            raise ValueError("analysis dates must cover inclusive full months")
        if self.startDate > self.endDate:
            raise ValueError("startDate must not be after endDate")
        if self.significant != (self.pValue < 0.05):
            raise ValueError("significant must equal pValue < 0.05")
        return self


class SeriesResponseData(BaseModel):
    """Data payload for GET /api/v1/series."""
    variable: VariableDTO
    region: RegionDTO
    timeSeries: list[TimeSeriesPointDTO]
    trendAnalysis: Optional[TrendAnalysisDTO] = None

    model_config = ConfigDict(populate_by_name=True, extra="forbid")


# --- Response Models ---

class VariablesListResponse(BaseModel):
    """GET /api/v1/variables response."""
    data: list[VariableDTO]

    model_config = ConfigDict(populate_by_name=True)


class RegionsListResponse(BaseModel):
    """GET /api/v1/regions response."""
    data: list[RegionDTO]

    model_config = ConfigDict(populate_by_name=True)


class SeriesResponse(BaseModel):
    """GET /api/v1/series response."""
    data: SeriesResponseData

    model_config = ConfigDict(populate_by_name=True)


class HealthResponse(BaseModel):
    """GET /api/v1/health response."""
    status: str = "ok"
    service: str = "trendscope-api"
    version: str = "0.1.0"

    model_config = ConfigDict(populate_by_name=True)


# --- Helper functions for generating IDs ---

def generate_series_id(variable_id: str, region_id: str, period_start: date) -> str:
    """Generate deterministic seriesId for a time series point."""
    return f"{variable_id}:{region_id}:{period_start.isoformat()}"


def generate_analysis_id(variable_id: str, region_id: str, start_date: date, end_date: date) -> str:
    """Generate deterministic analysisId for a trend analysis."""
    return f"{variable_id}:{region_id}:{start_date.isoformat()}:{end_date.isoformat()}"
