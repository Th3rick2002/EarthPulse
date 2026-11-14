"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routers import catalog_router, series_router
from app.repositories import SQLiteRepository, SQLiteCacheRepository


# Global repository instances (can be swapped for Firestore in production)
repo: SQLiteRepository | None = None
cache_repo: SQLiteCacheRepository | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global repo, cache_repo
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

# Include routers
app.include_router(catalog_router)
app.include_router(series_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "trendscope-api"}


@app.get("/")
async def root():
    """API root with links to documentation."""
    return {
        "name": "TrendScope API",
        "version": "0.1.0",
        "docs": "/docs",
        "endpoints": {
            "variables": "/variables",
            "regions": "/regions",
            "series": "/series",
        },
    }


def get_repository() -> SQLiteRepository:
    """Dependency for repository injection."""
    if repo is None:
        raise RuntimeError("Repository not initialized")
    return repo


def get_cache_repository() -> SQLiteCacheRepository:
    """Dependency for cache repository injection."""
    if cache_repo is None:
        raise RuntimeError("Cache repository not initialized")
    return cache_repo