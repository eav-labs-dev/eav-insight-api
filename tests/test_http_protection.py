"""HTTP throttling and request-size contract tests."""

import asyncio
from collections.abc import Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.http_protection import HttpProtectionMiddleware
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


def test_limit_resets_after_window() -> None:
    now = [1_000.0]

    async def app(scope: dict[str, Any], receive: Any, send: Any) -> None:
        await receive()
        await send({"type": "http.response.start", "status": 204, "headers": []})
        await send({"type": "http.response.body", "body": b""})

    middleware = HttpProtectionMiddleware(
        app,
        api_limit=1,
        auth_limit=1,
        max_body_bytes=32,
        clock=lambda: now[0],
    )

    async def request() -> int:
        incoming = [{"type": "http.request", "body": b"", "more_body": False}]
        outgoing: list[dict[str, Any]] = []

        async def receive() -> dict[str, Any]:
            return incoming.pop(0)

        async def send(message: dict[str, Any]) -> None:
            outgoing.append(message)

        await middleware(
            {
                "type": "http",
                "method": "GET",
                "path": "/api/v1/reports",
                "headers": [],
                "client": ("203.0.113.10", 50000),
            },
            receive,
            send,
        )
        return outgoing[0]["status"]

    assert asyncio.run(request()) == 204
    assert asyncio.run(request()) == 429
    now[0] += 60
    assert asyncio.run(request()) == 204
