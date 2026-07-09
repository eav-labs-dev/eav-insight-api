from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="EAV Insight API", alias="APP_NAME")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=True, alias="DEBUG")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    database_url: str = Field(
        default="postgresql+psycopg://eav:eav_password@localhost:5432/eav_insight",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        alias="CORS_ORIGINS",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Return CORS origins as a clean list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
