"""API routers."""

from .catalog import router as catalog_router
from .series import router as series_router

__all__ = ["catalog_router", "series_router"]