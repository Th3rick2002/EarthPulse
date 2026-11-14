"""Pydantic schemas for API contracts - Contract version."""

from .contract import (
    VariableDTO,
    RegionDTO,
    BBoxDTO,
    TimeSeriesPointDTO,
    TrendAnalysisDTO,
    VariablesListResponse,
    RegionsListResponse,
    SeriesResponse,
    SeriesResponseData,
    HealthResponse,
    ErrorResponse,
    ErrorDetail,
    QualityValue,
    RegionType,
    generate_series_id,
    generate_analysis_id,
)

__all__ = [
    "VariableDTO",
    "RegionDTO",
    "BBoxDTO",
    "TimeSeriesPointDTO",
    "TrendAnalysisDTO",
    "VariablesListResponse",
    "RegionsListResponse",
    "SeriesResponse",
    "SeriesResponseData",
    "HealthResponse",
    "ErrorResponse",
    "ErrorDetail",
    "QualityValue",
    "RegionType",
    "generate_series_id",
    "generate_analysis_id",
]