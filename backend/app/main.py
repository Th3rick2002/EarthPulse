"""FastAPI application entry point."""

import os
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers import catalog_router, health_router, series_router
from app.schemas.contract import ErrorDetail, ErrorResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize application repositories."""
    from app.repositories import SQLiteCacheRepository, SQLiteRepository
    from app.services.providers import close_provider_clients

    app.state.repo = SQLiteRepository()
    app.state.cache_repo = SQLiteCacheRepository()
    try:
        yield
    finally:
        await close_provider_clients()


app = FastAPI(
    title="TrendScope API",
    description="Earth science time series and trend analysis API",
    version="0.1.0",
    lifespan=lifespan,
)

cors_origins = [
    origin.strip().rstrip("/")
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Assign a unique ID to each request and expose it for support logs."""
    request.state.request_id = uuid4().hex
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response


def error_response(
    request: Request,
    status_code: int,
    code: str,
    message: str,
    details: dict | None = None,
) -> JSONResponse:
    error = ErrorDetail(
        code=code,
        message=message,
        details=details or {},
        requestId=request.state.request_id,
    )
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(error=error).model_dump(mode="json", by_alias=True),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Format explicit HTTP errors with the shared envelope."""
    detail = exc.detail if isinstance(exc.detail, dict) else {}
    code_map = {
        400: "INVALID_PARAMS",
        404: "NOT_FOUND",
        422: "VALIDATION_ERROR",
        500: "INTERNAL_ERROR",
        502: "PROVIDER_ERROR",
        503: "PROVIDER_UNAVAILABLE",
        504: "PROVIDER_TIMEOUT",
    }
    return error_response(
        request=request,
        status_code=exc.status_code,
        code=detail.get("code", code_map.get(exc.status_code, "ERROR")),
        message=detail.get("message", str(exc.detail) if exc.detail else "Request failed"),
        details=detail.get("details", {"path": str(request.url.path)}),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Format FastAPI query/path validation errors with the shared envelope."""
    errors = [
        {
            "loc": list(error.get("loc", ())),
            "msg": error.get("msg", "Invalid value"),
            "type": error.get("type", ""),
        }
        for error in exc.errors()
    ]
    return error_response(
        request=request,
        status_code=422,
        code="VALIDATION_ERROR",
        message="Request parameters failed validation",
        details={"errors": errors},
    )


@app.exception_handler(Exception)
async def internal_error_handler(request: Request, exc: Exception):
    """Hide internal details while returning a contract-compliant 500."""
    return error_response(
        request=request,
        status_code=500,
        code="INTERNAL_ERROR",
        message="Internal server error",
        details={"path": str(request.url.path)},
    )


app.include_router(catalog_router)
app.include_router(series_router)
app.include_router(health_router)


@app.get("/")
async def root():
    """API root with links to documentation."""
    return {
        "name": "TrendScope API",
        "version": "0.1.0",
        "docs": "/docs",
        "endpoints": {
            "variables": "/api/v1/variables",
            "regions": "/api/v1/regions",
            "series": "/api/v1/series",
            "health": "/api/v1/health",
        },
    }
