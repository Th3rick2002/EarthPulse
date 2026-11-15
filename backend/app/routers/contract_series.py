"""Series endpoint: GET /api/v1/series per contract."""

from calendar import monthrange
from datetime import date, datetime, timezone
from fastapi import APIRouter, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse
from typing import Annotated
from hashlib import sha256
import asyncio
from copy import deepcopy
import json
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
    ErrorResponse,
    CompareSeriesRequest,
    VariableAvailabilityDTO,
    generate_series_id,
    generate_analysis_id,
)
from app.services.analysis import compute_trend_analysis
from app.services.providers import ProviderError, fetch_monthly_series, get_variable_available_dates
from app.services.series_jobs import get_or_start_series_job, get_series_job

router = APIRouter(prefix="/api/v1", tags=["series"])


@router.get("/availability")
async def get_variable_availability(variable_id: Annotated[str, Query(alias="variableId")]):
    """Return current complete date coverage for a variable's live provider."""
    variable = get_variable(variable_id)
    if variable is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": f"Variable '{variable_id}' not found", "details": {}},
        )
    if variable_id != "precipitation":
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_PARAMS", "message": "Live availability is not exposed for this variable", "details": {}},
        )
    try:
        available_start, available_end = await get_variable_available_dates(variable_id)
    except ProviderError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={"code": exc.code, "message": str(exc), "details": _provider_error_details(exc)},
        ) from exc
    result = VariableAvailabilityDTO(
        variableId=variable_id,
        availableStartDate=available_start,
        availableEndDate=available_end,
    )
    return {"data": result.model_dump(mode="json", by_alias=True)}


async def _validate_provider_coverage(variable_id: str, start_date: date, end_date: date) -> None:
    if variable_id != "precipitation":
        return
    try:
        available_start, available_end = await get_variable_available_dates(variable_id)
    except ProviderError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={"code": exc.code, "message": str(exc), "details": _provider_error_details(exc)},
        ) from exc
    if start_date > available_end or end_date > available_end or start_date < available_start:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_PARAMS",
                "message": "The selected period is outside the provider's available precipitation dates",
                "details": {"availableStartDate": available_start.isoformat(), "availableEndDate": available_end.isoformat()},
            },
        )


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


def _series_cache_key(variable_id: str, bbox: tuple[float, float, float, float], start_date: date, end_date: date) -> str:
    variable = get_variable(variable_id)
    identity = {
        "variableId": variable_id,
        "provider": variable.source.provider,
        "product": variable.source.product,
        "sourceId": variable.source.source_id,
        "bbox": [round(value, 5) for value in bbox],
        "startDate": start_date.isoformat(),
        "endDate": end_date.isoformat(),
    }
    digest = sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
    return f"series:{digest}"


def _validate_period(start_date: date, end_date: date) -> None:
    if start_date > end_date or start_date.day != 1 or end_date.day != monthrange(end_date.year, end_date.month)[1]:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_PARAMS", "message": "Dates must cover inclusive full months", "details": {}},
        )
    month_count = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month + 1
    if not 12 <= month_count <= 600:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_PARAMS", "message": "The selected period must be between 1 and 50 years", "details": {"months": month_count}},
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


ERROR_RESPONSES = {
    400: {"model": ErrorResponse, "description": "Invalid query parameters"},
    404: {"model": ErrorResponse, "description": "Variable or region not found"},
    422: {"model": ErrorResponse, "description": "Parameter validation failed"},
    500: {"model": ErrorResponse, "description": "Internal server error"},
    502: {"model": ErrorResponse, "description": "Provider request failed"},
    503: {"model": ErrorResponse, "description": "Provider unavailable"},
    504: {"model": ErrorResponse, "description": "Provider timeout"},
    202: {"description": "Long-running series query accepted; poll the returned jobId."},
}


@router.get("/series", response_model=SeriesResponse, responses=ERROR_RESPONSES)
async def get_series(
    variable_id: Annotated[str, Query(alias="variableId")],
    region_id: Annotated[str, Query(alias="regionId")],
    start_date: Annotated[date, Query(alias="startDate")],
    end_date: Annotated[date, Query(alias="endDate")],
    request: Request,
    response: Response,
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
            detail={"code": "NOT_FOUND", "message": f"Variable '{variable_id}' not found", "details": {}}
        )

    # Validate region exists
    region = get_region(region_id)
    if not region:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": f"Region '{region_id}' not found", "details": {}}
        )

    # Validate variable-region combination
    valid, reason = validate_variable_region(variable_id, region_id)
    if not valid:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_PARAMS", "message": reason, "details": {}}
        )

    _validate_period(start_date, end_date)
    await _validate_provider_coverage(variable_id, start_date, end_date)
    cache_repo = request.app.state.cache_repo
    cache_key = _series_cache_key(variable_id, region.bbox, start_date, end_date)
    cached_response = await cache_repo.get_response(cache_key)
    if cached_response is not None:
        response.headers["X-Cache"] = "HIT"
        return cached_response
    response.headers["X-Cache"] = "MISS"

    if variable.source.provider == "planetary-computer":
        query_key = f"{variable_id}:{region_id}:{start_date.isoformat()}:{end_date.isoformat()}"
        job = get_or_start_series_job(
            query_key,
            (variable_id, region_id, start_date, end_date),
            lambda: fetch_monthly_series(variable_id, region_id, start_date, end_date),
        )
        if job.status == "processing":
            return JSONResponse(
                status_code=202,
                headers={"Retry-After": "2"},
                content={"data": {"jobId": job.job_id, "status": job.status}},
            )
        if job.status == "failed":
            _raise_job_error(job.error)
        result = _build_series_response(
            variable_id, region_id, start_date, end_date, job.points or []
        )
        await cache_repo.set_response(cache_key, result.model_dump(mode="json", by_alias=True))
        return result

    try:
        time_series = await fetch_monthly_series(
            variable_id=variable_id,
            region_id=region_id,
            start_date=start_date,
            end_date=end_date,
        )
    except ProviderError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={"code": exc.code, "message": str(exc), "details": _provider_error_details(exc)},
        ) from exc

    result = _build_series_response(
        variable_id, region_id, start_date, end_date, time_series
    )
    await cache_repo.set_response(cache_key, result.model_dump(mode="json", by_alias=True))
    return result


@router.post("/series/compare", responses=ERROR_RESPONSES)
async def compare_areas(body: CompareSeriesRequest, request: Request, response: Response):
    """Fetch and analyze up to four independently drawn map rectangles."""
    variable = get_variable(body.variableId)
    if variable is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": f"Variable '{body.variableId}' not found", "details": {}},
        )
    _validate_period(body.startDate, body.endDate)
    await _validate_provider_coverage(body.variableId, body.startDate, body.endDate)

    cache_repo = request.app.state.cache_repo
    areas = []
    cached_by_id: dict[str, dict | None] = {}
    for area in body.areas:
        bbox = (area.bbox.latMin, area.bbox.latMax, area.bbox.lonMin, area.bbox.lonMax)
        cache_key = _series_cache_key(body.variableId, bbox, body.startDate, body.endDate)
        areas.append((area, bbox, cache_key))
        cached_by_id[area.areaId] = await cache_repo.get_response(cache_key)

    def result_for(area, cached_response):
        payload = deepcopy(cached_response["data"])
        payload["region"]["regionId"] = area.areaId
        payload["region"]["name"] = area.name
        for point in payload["timeSeries"]:
            point["regionId"] = area.areaId
            point["seriesId"] = generate_series_id(body.variableId, area.areaId, date.fromisoformat(point["date"]))
        trend = payload.get("trendAnalysis")
        if trend:
            trend["regionId"] = area.areaId
            trend["analysisId"] = generate_analysis_id(body.variableId, area.areaId, body.startDate, body.endDate)
        return {"areaId": area.areaId, "name": area.name, "series": payload}

    if all(cached_by_id[area.areaId] is not None for area, _, _ in areas):
        response.headers["X-Cache"] = "HIT"
        return {"data": {"results": [result_for(area, cached_by_id[area.areaId]) for area, _, _ in areas]}}

    response.headers["X-Cache"] = "PARTIAL" if any(cached_by_id.values()) else "MISS"
    job_query_key = json.dumps({
        "variableId": body.variableId,
        "startDate": body.startDate.isoformat(),
        "endDate": body.endDate.isoformat(),
        "areas": [
            {"areaId": area.areaId, "bbox": [round(value, 5) for value in bbox]}
            for area, bbox, _ in areas
        ],
    }, sort_keys=True)

    async def fetch_batch():
        semaphore = asyncio.Semaphore(2)

        async def fetch_one(area, bbox, cache_key):
            cached = cached_by_id[area.areaId]
            if cached is not None:
                return result_for(area, cached)
            async with semaphore:
                points = await fetch_monthly_series(
                    body.variableId,
                    area.areaId,
                    body.startDate,
                    body.endDate,
                    region_bbox=bbox,
                )
            region_dto = RegionDTO(
                regionId=area.areaId,
                name=area.name,
                bbox=area.bbox,
                description="Zona rectangular seleccionada en el mapa.",
                type="custom",
            )
            series = _build_series_response(
                body.variableId,
                area.areaId,
                body.startDate,
                body.endDate,
                points,
                region_override=region_dto,
            )
            serialized = series.model_dump(mode="json", by_alias=True)
            await cache_repo.set_response(cache_key, serialized)
            return {"areaId": area.areaId, "name": area.name, "series": serialized["data"]}

        results = await asyncio.gather(*(fetch_one(area, bbox, key) for area, bbox, key in areas))
        return {"data": {"results": results}}

    job = get_or_start_series_job(
        job_query_key,
        ("batch", job_query_key),
        fetch_batch,
    )
    if job.status == "processing":
        return JSONResponse(
            status_code=202,
            headers={"Retry-After": "2"},
            content={"data": {"jobId": job.job_id, "status": job.status}},
        )
    if job.status == "failed":
        _raise_job_error(job.error)
    return JSONResponse(content=job.points)


@router.get("/series/jobs/{job_id}", responses=ERROR_RESPONSES)
async def get_series_job_status(job_id: str, request: Request, response: Response):
    """Poll a long-running series query and return the normal series DTO when ready."""
    job = get_series_job(job_id)
    if job is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "Series query job was not found or expired", "details": {}},
        )
    if job.status == "processing":
        return JSONResponse(
            status_code=202,
            headers={"Retry-After": "2"},
            content={"data": {"jobId": job.job_id, "status": job.status}},
        )
    if job.status == "failed":
        _raise_job_error(job.error)

    if isinstance(job.query, tuple) and job.query and job.query[0] == "batch":
        return JSONResponse(content=job.points)

    # The query key is stored on the job so its completed data can be formatted
    # as the exact same DTO returned by the synchronous providers.
    variable_id, region_id, start_date, end_date = job.query
    region = get_region(region_id)
    cache_key = _series_cache_key(variable_id, region.bbox, start_date, end_date)
    cache_repo = request.app.state.cache_repo
    cached_response = await cache_repo.get_response(cache_key)
    if cached_response is not None:
        response.headers["X-Cache"] = "HIT"
        return cached_response
    response.headers["X-Cache"] = "MISS"
    result = _build_series_response(
        variable_id, region_id, start_date, end_date, job.points or []
    )
    await cache_repo.set_response(cache_key, result.model_dump(mode="json", by_alias=True))
    return result


def _raise_job_error(error: Exception | None) -> None:
    if isinstance(error, ProviderError):
        raise HTTPException(
            status_code=error.status_code,
            detail={"code": error.code, "message": str(error), "details": _provider_error_details(error)},
        ) from error
    raise HTTPException(
        status_code=502,
        detail={"code": "PROVIDER_ERROR", "message": "The planetary-computer request failed", "details": {}},
    )


def _provider_error_details(error: ProviderError) -> dict:
    details = {"provider": error.provider}
    if error.upstream_status is not None:
        details["upstreamStatus"] = error.upstream_status
    if error.upstream_message:
        details["upstreamMessage"] = error.upstream_message
    return details


def _build_series_response(variable_id, region_id, start_date, end_date, time_series, region_override: RegionDTO | None = None):
    variable = get_variable(variable_id)
    region = get_region(region_id) if region_override is None else None
    expected_months = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month + 1
    min_years = variable.min_years

    # Convert to contract TimeSeriesPointDTO
    contract_time_series = []
    for point in time_series:
        # point has date, value, quality ("observed"/"interpolated"/"missing")
        # Map provider quality to the canonical contract enum.
        quality_map = {"observed": "ok", "interpolated": "interpolated", "missing": "missing"}
        contract_quality = quality_map.get(point.quality)
        if contract_quality is None:
            raise HTTPException(
                status_code=502,
                detail={
                    "code": "PROVIDER_ERROR",
                    "message": "Provider returned an unsupported quality value",
                    "details": {"quality": point.quality},
                },
            )
        contract_quality: QualityValue
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
    if expected_months < min_years * 12:
        insufficient_reason = f"Time span ({expected_months / 12:.1f} years) less than minimum {min_years} years required for trend analysis"
    elif len(ok_points) < expected_months * 0.5:
        insufficient_reason = f"Insufficient valid observations ({len(ok_points)}/{expected_months}); at least 50% are required"

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
                    slope=analysis_result["slope"],  # Analysis service returns units per calendar year.
                    pValue=analysis_result["p_value"],
                    significant=analysis_result["significant"],
                    interpretation=analysis_result["interpretation"],
                    createdAt=datetime.now(timezone.utc),
                )

    # Build response per contract
    response_data = SeriesResponseData(
        variable=_variable_to_dto(variable),
        region=region_override or _region_to_dto(region),
        timeSeries=contract_time_series,
        trendAnalysis=trend_analysis,
    )

    return SeriesResponse(data=response_data)
