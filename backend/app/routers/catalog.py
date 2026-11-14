"""Catalog endpoints: /variables and /regions."""

from fastapi import APIRouter, HTTPException
from app.data.catalog import (
    list_variables,
    list_regions,
    get_variable,
    get_region,
    VARIABLES,
    REGIONS,
)
from app.schemas.catalog import (
    VariablesListResponse,
    RegionsListResponse,
    VariableResponse,
    RegionResponse,
    VariableSourceResponse,
)

router = APIRouter(prefix="", tags=["catalog"])


def _variable_to_response(var) -> VariableResponse:
    """Convert internal Variable to API response."""
    src = var.source
    return VariableResponse(
        id=var.id,
        name=var.name,
        definition=var.definition,
        category=var.category,
        canonical_unit=var.canonical_unit,
        min_years=var.min_years,
        frequency=var.frequency,
        source=VariableSourceResponse(
            provider=src.provider,
            product=src.product,
            source_id=src.source_id,
            native_unit=src.native_unit,
            scale_factor=src.scale_factor,
            aggregation=src.aggregation,
            resolution=src.resolution,
            access_method=src.access_method,
        ),
        supported_region_ids=var.supported_region_ids,
    )


def _region_to_response(region) -> RegionResponse:
    """Convert internal Region to API response."""
    return RegionResponse(
        id=region.id,
        name=region.name,
        description=region.description,
        type=region.type,
        bbox=region.bbox,
        crs=region.crs,
        supported_variable_ids=region.supported_variable_ids,
    )


@router.get("/variables", response_model=VariablesListResponse)
async def get_variables():
    """List all available variables with metadata."""
    variables = [_variable_to_response(v) for v in list_variables()]
    return VariablesListResponse(variables=variables)


@router.get("/variables/{variable_id}", response_model=VariableResponse)
async def get_variable_by_id(variable_id: str):
    """Get a specific variable by ID."""
    var = get_variable(variable_id)
    if not var:
        raise HTTPException(status_code=404, detail=f"Variable '{variable_id}' not found")
    return _variable_to_response(var)


@router.get("/regions", response_model=RegionsListResponse)
async def get_regions():
    """List all available regions with metadata."""
    regions = [_region_to_response(r) for r in list_regions()]
    return RegionsListResponse(regions=regions)


@router.get("/regions/{region_id}", response_model=RegionResponse)
async def get_region_by_id(region_id: str):
    """Get a specific region by ID."""
    region = get_region(region_id)
    if not region:
        raise HTTPException(status_code=404, detail=f"Region '{region_id}' not found")
    return _region_to_response(region)