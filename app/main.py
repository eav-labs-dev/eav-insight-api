from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app.core.config import get_settings


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

    app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
