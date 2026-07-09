from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    """Return basic service health information."""
    settings = get_settings()

    return HealthResponse(
        status="ok",
        service=settings.app_name,
        environment=settings.environment,
    )
