"""Health endpoint: GET /api/v1/health per contract."""

from fastapi import APIRouter
from app.schemas.contract import HealthResponse

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint per contract."""
    return HealthResponse()