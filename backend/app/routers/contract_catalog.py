"""Catalog endpoints: GET /api/v1/variables and GET /api/v1/regions per contract."""

from fastapi import APIRouter, HTTPException
from app.data.catalog import list_variables, list_regions, get_variable, get_region, REGIONS, VARIABLES
from app.schemas.contract import (
    VariablesListResponse,
    RegionsListResponse,
    VariableDTO,
    RegionDTO,
    BBoxDTO,
    ErrorResponse,
)

router = APIRouter(prefix="/api/v1", tags=["catalog"])
INTERNAL_ERROR_RESPONSE = {
    500: {"model": ErrorResponse, "description": "Internal server error"}
}


def _variable_to_dto(var) -> VariableDTO:
    """Convert internal Variable to contract VariableDTO."""
    # Map internal source to contract source string
    src = var.source
    source_str = f"{src.provider}:{src.product}:{src.source_id}"
    
    return VariableDTO(
        variableId=var.id,
        name=var.name,
        description=var.definition,
        unit=var.canonical_unit,
        source=source_str,
        category=var.category,
        minYears=var.min_years,
    )


def _region_to_dto(region) -> RegionDTO:
    """Convert internal Region to contract RegionDTO."""
    lat_min, lat_max, lon_min, lon_max = region.bbox
    return RegionDTO(
        regionId=region.id,
        name=region.name,
        bbox=BBoxDTO(
            latMin=lat_min,
            latMax=lat_max,
            lonMin=lon_min,
            lonMax=lon_max,
        ),
        description=region.description,
        type=region.type,
    )


@router.get("/variables", response_model=VariablesListResponse, responses=INTERNAL_ERROR_RESPONSE)
async def get_variables():
    """List all available variables with metadata per contract."""
    variables = [_variable_to_dto(v) for v in list_variables()]
    return VariablesListResponse(data=variables)


@router.get("/regions", response_model=RegionsListResponse, responses=INTERNAL_ERROR_RESPONSE)
async def get_regions():
    """List all available regions with metadata per contract."""
    regions = [_region_to_dto(r) for r in list_regions()]
    return RegionsListResponse(data=regions)
