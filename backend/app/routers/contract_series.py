"""Series endpoint: GET /api/v1/series per contract."""

from fastapi import APIRouter, HTTPException, Query, Request
from datetime import date, datetime
from typing import Annotated
import random

from app.data.catalog import (
    get_variable,
    get_region,
    validate_variable_region,
)
from app.schemas.contract import (
    SeriesResponse,
    SeriesResponseData,
    VariableDTO,
    RegionDTO,
    BBoxDTO,
    TimeSeriesPointDTO,
    TrendAnalysisDTO,
    QualityValue,
    generate_series_id,
    generate_analysis_id,
)
from app.services.analysis import compute_trend_analysis
from app.services.providers import fetch_monthly_series

router = APIRouter(prefix="/api/v1", tags=["series"])


def _variable_to_dto(var) -> VariableDTO:
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
    lat_min, lat_max, lon_min, lon_max = region.bbox
    return RegionDTO(
        regionId=region.id,
        name=region.name,
        bbox=BBoxDTO(latMin=lat_min, latMax=lat_max, lonMin=lon_min, lonMax=lon_max),
        description=region.description,
        type=region.type,
    )


def _generate_mock_time_series(
    variable_id: str,
    region_id: str,
    start_date: date,
    end_date: date,
) -> list[TimeSeriesPointDTO]:
    """Generate mock monthly time series per contract (quality: ok/missing/interpolated)."""
    points = []
    current = date(start_date.year, start_date.month, 1)

    base_values = {"ndvi": 0.65, "air_temperature": -10.0, "precipitation": 200.0}
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

        # Mostly "ok", occasionally "interpolated", rarely "missing"
        quality_roll = random.random()
        if quality_roll < 0.95:
            quality: QualityValue = "ok"
            final_value = round(value, 4)
        elif quality_roll < 0.98:
            quality = "interpolated"
            final_value = round(value, 4)
        else:
            quality = "missing"
            final_value = None  # value is null when quality is missing per contract

        points.append(TimeSeriesPointDTO(
            seriesId=generate_series_id(variable_id, region_id, current),
            variableId=variable_id,
            regionId=region_id,
            date=current,
            value=final_value,
            quality=quality,
        ))

        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)

    return points


@router.get("/series", response_model=SeriesResponse)
async def get_series(
    variable_id: Annotated[str, Query(alias="variableId")],
    region_id: Annotated[str, Query(alias="regionId")],
    start_date: Annotated[date, Query(alias="startDate")],
    end_date: Annotated[date, Query(alias="endDate")],
    request: Request,
):
    """
    Get monthly time series with trend analysis per contract.

    Response wrapped in {data: {variable, region, timeSeries, trendAnalysis}}.
    """
    # Validate variable exists
    variable = get_variable(variable_id)
    if not variable:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": f"Variable '{variable_id}' not found", "details": {}, "requestId": "req-001"}
        )

    # Validate region exists
    region = get_region(region_id)
    if not region:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": f"Region '{region_id}' not found", "details": {}, "requestId": "req-002"}
        )

    # Validate variable-region combination
    valid, reason = validate_variable_region(variable_id, region_id)
    if not valid:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_PARAMS", "message": reason, "details": {}, "requestId": "req-003"}
        )

    # Validate date range
    if start_date >= end_date:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_PARAMS", "message": "startDate must be before endDate", "details": {}, "requestId": "req-004"}
        )

    # Check minimum years for analysis
    years_span = (end_date - start_date).days / 365.25
    min_years = variable.min_years

    # Fetch time series (mock for now)
    time_series = await fetch_monthly_series(
        variable_id=variable_id,
        region_id=region_id,
        start_date=start_date,
        end_date=end_date,
    )

    # Convert to contract TimeSeriesPointDTO
    contract_time_series = []
    for point in time_series:
        # point has date, value, quality ("observed"/"interpolated"/"missing")
        # Map quality to contract values
        quality_map = {"observed": "ok", "interpolated": "interpolated", "missing": "missing"}
        contract_quality: QualityValue = quality_map.get(point.quality, "ok")
        contract_value = point.value if contract_quality != "missing" else None
        
        contract_time_series.append(TimeSeriesPointDTO(
            seriesId=generate_series_id(variable_id, region_id, point.date),
            variableId=variable_id,
            regionId=region_id,
            date=point.date,
            value=contract_value,
            quality=contract_quality,
        ))

    # Determine if we have sufficient coverage for trend analysis
    ok_points = [p for p in contract_time_series if p.quality == "ok"]
    insufficient_reason = None
    if years_span < min_years:
        insufficient_reason = f"Time span ({years_span:.1f} years) less than minimum {min_years} years required for trend analysis"
    elif len(ok_points) < min_years * 12 * 0.5:
        insufficient_reason = f"Insufficient valid observations ({len(ok_points)}/{len(contract_time_series)}) for reliable analysis"

    # Compute trend analysis if sufficient coverage
    trend_analysis = None
    if not insufficient_reason and len(ok_points) >= 3:
        values = [p.value for p in ok_points if p.value is not None]
        dates = [p.date for p in ok_points if p.value is not None]
        if len(values) >= 3:
            analysis_result = compute_trend_analysis(
                values=values,
                dates=dates,
                unit=variable.canonical_unit,
                frequency="monthly",
            )
            if analysis_result:
                # Convert slope to per-year (already done in analysis service)
                # Contract expects slope in variable unit per year
                trend_analysis = TrendAnalysisDTO(
                    analysisId=generate_analysis_id(variable_id, region_id, start_date, end_date),
                    variableId=variable_id,
                    regionId=region_id,
                    startDate=start_date,
                    endDate=end_date,
                    slope=analysis_result["slope"] * 12,  # Convert monthly to yearly
                    pValue=analysis_result["p_value"],
                    significant=analysis_result["significant"],
                    interpretation=analysis_result["interpretation"],
                    createdAt=datetime.utcnow(),
                )

    # Build response per contract
    response_data = SeriesResponseData(
        variable=_variable_to_dto(variable),
        region=_region_to_dto(region),
        timeSeries=contract_time_series,
        trendAnalysis=trend_analysis,
    )

    return SeriesResponse(data=response_data)