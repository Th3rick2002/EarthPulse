"""FastAPI application entry point."""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.routers import catalog_router, series_router, health_router
from app.schemas.contract import ErrorResponse, ErrorDetail


# Global repository instances (can be swapped for Firestore in production)
repo = None
cache_repo = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global repo, cache_repo
    from app.repositories import SQLiteRepository, SQLiteCacheRepository
    repo = SQLiteRepository()
    cache_repo = SQLiteCacheRepository()
    yield
    # Cleanup if needed


app = FastAPI(
    title="TrendScope API",
    description="Earth science time series and trend analysis API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vite default
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# Exception handlers for contract-compliant errors
from fastapi import HTTPException

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTPException with contract error format, preserving detail."""
    # If detail is already a dict with contract format, use it
    if isinstance(exc.detail, dict) and "code" in exc.detail:
        error_detail = ErrorDetail(**exc.detail)
    else:
        # Map status code to error code
        code_map = {400: "INVALID_PARAMS", 404: "NOT_FOUND", 422: "VALIDATION_ERROR"}
        code = code_map.get(exc.status_code, "ERROR")
        message = str(exc.detail) if exc.detail else "Request failed"
        error_detail = ErrorDetail(code=code, message=message, details={"path": str(request.url.path)})
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error=error_detail).model_dump(by_alias=True),
    )


@app.exception_handler(Exception)
async def internal_error_handler(request: Request, exc: Exception):
    """Handle 500 errors with contract error format."""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error=ErrorDetail(
                code="INTERNAL_ERROR",
                message="Internal server error",
                details={"path": str(request.url.path)},
            )
        ).model_dump(by_alias=True),
    )


# Include routers (all under /api/v1 via router prefixes)
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