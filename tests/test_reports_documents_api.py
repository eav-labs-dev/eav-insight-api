from collections.abc import Generator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import get_db
from app.main import app
from app.models import Base, Organization, Tag


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


def seed_organization_and_tag(client: TestClient) -> tuple[str, str]:
    db_override = app.dependency_overrides[get_db]
    db = next(db_override())
    try:
        unique_suffix = str(uuid4())[:8]
        organization = Organization(name="EAV Demo", slug=f"eav-demo-{unique_suffix}")
        tag = Tag(organization=organization, name="Operations", slug="operations")
        db.add_all([organization, tag])
        db.commit()
        db.refresh(organization)
        db.refresh(tag)
        return organization.id, tag.id
    finally:
        db.close()


def test_create_list_update_and_delete_report(client: TestClient) -> None:
    organization_id, tag_id = seed_organization_and_tag(client)

    create_response = client.post(
        "/api/v1/reports",
        json={
            "organization_id": organization_id,
            "title": "Daily Field Operations",
            "summary": "Field report for inspection activity.",
            "status": "submitted",
            "source": "mobile-app",
            "tag_ids": [tag_id],
        },
    )

    assert create_response.status_code == 201
    created_report = create_response.json()
    report_id = created_report["id"]
    assert created_report["title"] == "Daily Field Operations"
    assert created_report["tags"][0]["slug"] == "operations"

    list_response = client.get(
        "/api/v1/reports",
        params={"organization_id": organization_id, "search": "Field"},
    )

    assert list_response.status_code == 200
    report_list = list_response.json()
    assert report_list["pagination"] == {"total": 1, "limit": 20, "offset": 0}
    assert report_list["items"][0]["id"] == report_id

    update_response = client.patch(
        f"/api/v1/reports/{report_id}",
        json={"status": "reviewed", "summary": "Reviewed by operations."},
    )

    assert update_response.status_code == 200
    assert update_response.json()["status"] == "reviewed"
    assert update_response.json()["summary"] == "Reviewed by operations."

    delete_response = client.delete(f"/api/v1/reports/{report_id}")

    assert delete_response.status_code == 204
    assert client.get(f"/api/v1/reports/{report_id}").status_code == 404


def test_create_list_update_and_delete_document(client: TestClient) -> None:
    organization_id, _ = seed_organization_and_tag(client)

    report_response = client.post(
        "/api/v1/reports",
        json={
            "organization_id": organization_id,
            "title": "Safety Inspection",
            "summary": "Inspection report.",
        },
    )
    report_id = report_response.json()["id"]

    create_response = client.post(
        "/api/v1/documents",
        json={
            "organization_id": organization_id,
            "report_id": report_id,
            "filename": "safety-inspection.pdf",
            "content_type": "application/pdf",
            "storage_path": "demo/safety-inspection.pdf",
            "size_bytes": 4096,
        },
    )

    assert create_response.status_code == 201
    created_document = create_response.json()
    document_id = created_document["id"]
    assert created_document["filename"] == "safety-inspection.pdf"
    assert created_document["report_id"] == report_id

    list_response = client.get(
        "/api/v1/documents",
        params={"organization_id": organization_id, "search": "safety"},
    )

    assert list_response.status_code == 200
    document_list = list_response.json()
    assert document_list["pagination"] == {"total": 1, "limit": 20, "offset": 0}
    assert document_list["items"][0]["id"] == document_id

    update_response = client.patch(
        f"/api/v1/documents/{document_id}",
        json={"filename": "updated-safety-inspection.pdf", "size_bytes": 8192},
    )

    assert update_response.status_code == 200
    assert update_response.json()["filename"] == "updated-safety-inspection.pdf"
    assert update_response.json()["size_bytes"] == 8192

    delete_response = client.delete(f"/api/v1/documents/{document_id}")

    assert delete_response.status_code == 204
    assert client.get(f"/api/v1/documents/{document_id}").status_code == 404


def test_document_rejects_report_from_another_organization(client: TestClient) -> None:
    first_organization_id, _ = seed_organization_and_tag(client)
    second_organization_id, _ = seed_organization_and_tag(client)

    report_response = client.post(
        "/api/v1/reports",
        json={
            "organization_id": first_organization_id,
            "title": "First Organization Report",
        },
    )
    report_id = report_response.json()["id"]

    response = client.post(
        "/api/v1/documents",
        json={
            "organization_id": second_organization_id,
            "report_id": report_id,
            "filename": "invalid-link.pdf",
            "content_type": "application/pdf",
            "storage_path": "demo/invalid-link.pdf",
            "size_bytes": 128,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Report does not belong to the selected organization."
