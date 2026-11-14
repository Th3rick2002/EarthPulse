"""Series endpoint: GET /series."""

from fastapi import APIRouter, HTTPException, Query, Depends
from datetime import date, timedelta
from typing import Annotated
import random

from app.data.catalog import (
    get_variable,
    get_region,
    validate_variable_region,
    VARIABLES,
    REGIONS,
)
from app.schemas.series import (
    SeriesRequest,
    SeriesResponse,
    Observation,
    Coverage,
    SourceInfo,
    Analysis,
    VariableRef,
    RegionRef,
)
from app.services.analysis import compute_trend_analysis
from app.services.providers import fetch_monthly_series

router = APIRouter(prefix="", tags=["series"])


def _variable_to_ref(var) -> VariableRef:
    """Convert internal Variable to SeriesResponse reference."""
    src = var.source
    return VariableRef(
        id=var.id,
        name=var.name,
        definition=var.definition,
        category=var.category,
        canonical_unit=var.canonical_unit,
        min_years=var.min_years,
        frequency=var.frequency,
        source={
            "provider": src.provider,
            "product": src.product,
            "source_id": src.source_id,
            "native_unit": src.native_unit,
            "scale_factor": src.scale_factor,
            "aggregation": src.aggregation,
            "resolution": src.resolution,
            "access_method": src.access_method,
        },
        supported_region_ids=var.supported_region_ids,
    )


def _region_to_ref(region) -> RegionRef:
    """Convert internal Region to SeriesResponse reference."""
    return RegionRef(
        id=region.id,
        name=region.name,
        description=region.description,
        type=region.type,
        bbox=region.bbox,
        crs=region.crs,
        supported_variable_ids=region.supported_variable_ids,
    )


def _generate_mock_observations(
    var_id: str,
    region_id: str,
    start_date: date,
    end_date: date,
    source_provider: str,
) -> list[Observation]:
    """Generate mock monthly observations for development/testing."""
    observations = []
    current = date(start_date.year, start_date.month, 1)

    # Base values by variable
    base_values = {
        "ndvi": 0.65,
        "air_temperature": -10.0,
        "precipitation": 200.0,
    }
    base = base_values.get(var_id, 0.0)

    # Seasonal variation
    seasonal = {
        "ndvi": lambda m: 0.1 * (1 if m in [3, 4, 5] else -0.5 if m in [9, 10, 11] else 0),
        "air_temperature": lambda m: 15 * (1 if m in [6, 7, 8] else -1 if m in [12, 1, 2] else 0),
        "precipitation": lambda m: 100 if m in [12, 1, 2, 3] else -50,
    }
    seasonal_fn = seasonal.get(var_id, lambda m: 0)

    while current <= end_date:
        # Add trend + seasonality + noise
        year_frac = (current.year - start_date.year) + (current.month - 1) / 12
        trend = 0.002 * year_frac * base  # Small trend
        value = base + trend + seasonal_fn(current.month) + random.uniform(-0.05 * abs(base), 0.05 * abs(base))

        # Ensure reasonable bounds
        if var_id == "ndvi":
            value = max(-1.0, min(1.0, value))
        elif var_id == "precipitation":
            value = max(0.0, value)

        observations.append(Observation(
            date=current,
            value=round(value, 4),
            quality="observed",
        ))

        # Next month
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)

    return observations


@router.get("/series", response_model=SeriesResponse)
async def get_series(
    variable_id: Annotated[str, Query(alias="variableId")],
    region_id: Annotated[str, Query(alias="regionId")],
    start_date: Annotated[date, Query(alias="startDate")],
    end_date: Annotated[date, Query(alias="endDate")],
):
    """
    Get monthly time series with trend analysis for a variable/region.

    Returns observations, coverage assessment, and Mann-Kendall trend analysis.
    If coverage < 5 years or insufficient observations, analysis is omitted with reason.
    """
    # Validate variable exists
    variable = get_variable(variable_id)
    if not variable:
        raise HTTPException(
            status_code=404,
            detail=f"Variable '{variable_id}' not found in catalog"
        )

    # Validate region exists
    region = get_region(region_id)
    if not region:
        raise HTTPException(
            status_code=404,
            detail=f"Region '{region_id}' not found in catalog"
        )

    # Validate variable-region combination
    valid, reason = validate_variable_region(variable_id, region_id)
    if not valid:
        raise HTTPException(status_code=400, detail=reason)

    # Validate date range
    if start_date >= end_date:
        raise HTTPException(status_code=400, detail="startDate must be before endDate")

    # Check minimum years for analysis
    years_span = (end_date - start_date).days / 365.25
    min_years = variable.min_years

    # Fetch observations (mock for now, will integrate real providers)
    observations = await fetch_monthly_series(
        variable_id=variable_id,
        region_id=region_id,
        start_date=start_date,
        end_date=end_date,
    )

    # Compute coverage
    expected_months = int((end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)) + 1
    valid_obs = sum(1 for o in observations if o.quality == "observed")
    coverage_ratio = valid_obs / expected_months if expected_months > 0 else 0.0

    insufficient_reason = None
    if years_span < min_years:
        insufficient_reason = f"Time span ({years_span:.1f} years) less than minimum {min_years} years required for trend analysis"
    elif valid_obs < min_years * 12 * 0.5:  # At least 50% of expected monthly obs
        insufficient_reason = f"Insufficient valid observations ({valid_obs}/{expected_months}) for reliable analysis"

    coverage = Coverage(
        start=start_date,
        end=end_date,
        validObservations=valid_obs,
        expectedObservations=expected_months,
        coverageRatio=round(coverage_ratio, 3),
        insufficientReason=insufficient_reason,
    )

    # Compute analysis if sufficient coverage
    analysis = None
    if not insufficient_reason and valid_obs >= 3:  # Minimum for Mann-Kendall
        values = [o.value for o in observations if o.quality == "observed"]
        analysis_result = compute_trend_analysis(
            values=values,
            dates=[o.period_start for o in observations if o.quality == "observed"],
            unit=variable.canonical_unit,
            frequency="monthly",
        )
        if analysis_result:
            analysis = Analysis(
                method=analysis_result["method"],
                slope=analysis_result["slope"],
                slopeUnit=analysis_result["slope_unit"],
                pValue=analysis_result["p_value"],
                significant=analysis_result["significant"],
                nObservations=analysis_result["n_observations"],
                interpretation=analysis_result["interpretation"],
                periodStart=start_date,
                periodEnd=end_date,
            )

    # Build response
    src = variable.source
    return SeriesResponse(
        variable=_variable_to_ref(variable),
        region=_region_to_ref(region),
        source=SourceInfo(
            provider=src.provider,
            product=src.product,
            sourceId=src.source_id,
        ),
        unit=variable.canonical_unit,
        frequency="monthly",
        coverage=coverage,
        observations=observations,
        analysis=analysis,
    )