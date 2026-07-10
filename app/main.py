"""Application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.documents import router as documents_router
from app.api.reports import router as reports_router
from app.core.config import get_settings
from app.core.error_handlers import register_exception_handlers
from app.schemas.health import HealthResponse


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description=(
            "Backend API for document intake, operational reporting, "
            "and searchable business records."
        ),
        version="0.1.0",
    )

    register_exception_handlers(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/", include_in_schema=False)
    async def root() -> dict[str, str]:
        return {
            "service": settings.app_name,
            "status": "running",
            "docs": "/docs",
            "health": f"{settings.api_v1_prefix}/health",
        }

    @app.get(
        f"{settings.api_v1_prefix}/health",
        response_model=HealthResponse,
        tags=["health"],
    )
    async def health_check() -> HealthResponse:
        """Return basic service health information."""
        return HealthResponse(
            status="ok",
            service=settings.app_name,
            environment=settings.environment,
        )

    app.include_router(auth_router, prefix=settings.api_v1_prefix)
    app.include_router(reports_router, prefix=settings.api_v1_prefix)
    app.include_router(documents_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
