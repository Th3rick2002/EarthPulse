"""Pydantic schemas for API contracts."""

from .catalog import VariableResponse, RegionResponse
from .series import (
    SeriesRequest,
    SeriesResponse,
    Observation,
    Coverage,
    Analysis,
    SourceInfo,
    VariableRef,
    RegionRef,
)

__all__ = [
    "VariableResponse",
    "RegionResponse",
    "SeriesRequest",
    "SeriesResponse",
    "Observation",
    "Coverage",
    "Analysis",
    "SourceInfo",
    "VariableRef",
    "RegionRef",
]