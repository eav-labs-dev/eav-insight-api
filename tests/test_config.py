"""Configuration tests."""

from app.core.config import Settings


def test_sqlalchemy_database_url_keeps_explicit_driver_url() -> None:
    settings = Settings(
        DATABASE_URL="postgresql+psycopg://user:password@localhost:5432/eav_insight"
    )

    assert (
        settings.sqlalchemy_database_url
        == "postgresql+psycopg://user:password@localhost:5432/eav_insight"
    )


def test_sqlalchemy_database_url_normalizes_render_postgres_url() -> None:
    settings = Settings(DATABASE_URL="postgres://user:password@host:5432/eav_insight")

    assert (
        settings.sqlalchemy_database_url
        == "postgresql+psycopg://user:password@host:5432/eav_insight"
    )


def test_sqlalchemy_database_url_normalizes_standard_postgresql_url() -> None:
    settings = Settings(DATABASE_URL="postgresql://user:password@host:5432/eav_insight")

    assert (
        settings.sqlalchemy_database_url
        == "postgresql+psycopg://user:password@host:5432/eav_insight"
    )
