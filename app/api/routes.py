from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.documents import router as documents_router
from app.api.reports import router as reports_router
from app.core.config import get_settings
from app.schemas.health import HealthResponse

router = APIRouter()
router.include_router(auth_router)
router.include_router(reports_router)
router.include_router(documents_router)


@router.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    """Return basic service health information."""
    settings = get_settings()

    return HealthResponse(
        status="ok",
        service=settings.app_name,
        environment=settings.environment,
    )
