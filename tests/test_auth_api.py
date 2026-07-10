from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import get_db
from app.main import app
from app.models import Base, Organization


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def seed_organization(client: TestClient) -> str:
    db_override = app.dependency_overrides[get_db]
    db = next(db_override())
    try:
        organization = Organization(name="EAV Demo", slug="eav-demo-auth")
        db.add(organization)
        db.commit()
        db.refresh(organization)
        return organization.id
    finally:
        db.close()


def test_register_login_and_read_current_user(client: TestClient) -> None:
    organization_id = seed_organization(client)

    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "organization_id": organization_id,
            "email": "Admin@Example.com",
            "full_name": "Demo Admin",
            "password": "ChangeMe123!",
            "role": "admin",
        },
    )

    assert register_response.status_code == 201
    created_user = register_response.json()
    assert created_user["email"] == "admin@example.com"
    assert created_user["organization_id"] == organization_id
    assert "password_hash" not in created_user

    token_response = client.post(
        "/api/v1/auth/token",
        json={"email": "admin@example.com", "password": "ChangeMe123!"},
    )

    assert token_response.status_code == 200
    access_token = token_response.json()["access_token"]
    assert token_response.json()["token_type"] == "bearer"

    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert me_response.status_code == 200
    assert me_response.json()["email"] == "admin@example.com"


def test_register_rejects_duplicate_email(client: TestClient) -> None:
    organization_id = seed_organization(client)
    payload = {
        "organization_id": organization_id,
        "email": "admin@example.com",
        "full_name": "Demo Admin",
        "password": "ChangeMe123!",
    }

    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    duplicate_response = client.post("/api/v1/auth/register", json=payload)

    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["detail"] == "A user with this email already exists."


def test_login_rejects_invalid_password(client: TestClient) -> None:
    organization_id = seed_organization(client)
    client.post(
        "/api/v1/auth/register",
        json={
            "organization_id": organization_id,
            "email": "admin@example.com",
            "full_name": "Demo Admin",
            "password": "ChangeMe123!",
        },
    )

    response = client.post(
        "/api/v1/auth/token",
        json={"email": "admin@example.com", "password": "WrongPassword123!"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."


def test_me_requires_valid_bearer_token(client: TestClient) -> None:
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials."
