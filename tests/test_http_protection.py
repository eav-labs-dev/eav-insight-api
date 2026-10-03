"""HTTP throttling and request-size contract tests."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import create_app


@pytest.fixture
def protected_client(monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    monkeypatch.setenv("AUTH_RATE_LIMIT_PER_MINUTE", "1")
    monkeypatch.setenv("API_RATE_LIMIT_PER_MINUTE", "1")
    monkeypatch.setenv("MAX_REQUEST_BODY_BYTES", "32")
    get_settings.cache_clear()
    with TestClient(create_app()) as client:
        yield client
    get_settings.cache_clear()


def test_auth_limit_returns_stable_429(protected_client: TestClient) -> None:
    first = protected_client.post("/api/v1/auth/token", json={})
    response = protected_client.post("/api/v1/auth/token", json={})

    assert first.status_code == 422
    assert response.status_code == 429
    assert response.headers["x-ratelimit-limit"] == "1"
    assert response.headers["x-ratelimit-remaining"] == "0"
    assert int(response.headers["retry-after"]) > 0
    assert response.json()["error"]["code"] == "rate_limit_exceeded"


def test_health_endpoint_is_exempt(protected_client: TestClient) -> None:
    assert protected_client.get("/api/v1/health").status_code == 200
    assert protected_client.get("/api/v1/health").status_code == 200


def test_oversized_body_returns_stable_413(protected_client: TestClient) -> None:
    response = protected_client.post(
        "/api/v1/auth/token",
        content=b"x" * 33,
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 413
    assert response.json()["error"]["code"] == "request_too_large"
