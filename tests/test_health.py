"""Health endpoint tests."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_returns_service_metadata() -> None:
    response = client.get("/")

    assert response.status_code == 200
    body = response.json()

    assert body["service"] == "EAV Insight API"
    assert body["status"] == "running"
    assert body["docs"] == "/docs"
    assert body["health"] == "/api/v1/health"


def test_health_check_returns_ok_status() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()

    assert body["status"] == "ok"
    assert body["service"] == "EAV Insight API"
    assert body["environment"] in {"development", "test"}
