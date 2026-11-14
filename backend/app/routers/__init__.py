"""API routers - Contract version."""

from .contract_catalog import router as catalog_router
from .contract_series import router as series_router
from .health import router as health_router

__all__ = ["catalog_router", "series_router", "health_router"]