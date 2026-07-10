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


def seed_organization_and_auth(client: TestClient) -> tuple[str, str, dict[str, str]]:
    db_override = app.dependency_overrides[get_db]
    db = next(db_override())
    try:
        unique_suffix = str(uuid4())[:8]
        organization = Organization(name="EAV Demo", slug=f"eav-demo-{unique_suffix}")
        tag = Tag(
            organization=organization,
            name="Operations",
            slug=f"operations-{unique_suffix}",
        )
        db.add_all([organization, tag])
        db.commit()
        db.refresh(organization)
        db.refresh(tag)
        organization_id = organization.id
        tag_id = tag.id
    finally:
        db.close()

    password = "ChangeMe123!"
    email = f"admin-{uuid4().hex[:8]}@example.com"
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "organization_id": organization_id,
            "email": email,
            "full_name": "Demo Admin",
            "password": password,
            "role": "admin",
        },
    )
    assert register_response.status_code == 201

    token_response = client.post(
        "/api/v1/auth/token",
        json={"email": email, "password": password},
    )
    assert token_response.status_code == 200
    access_token = token_response.json()["access_token"]

    return organization_id, tag_id, {"Authorization": f"Bearer {access_token}"}


def assert_pagination(
    body: dict[str, object],
    *,
    total: int,
    limit: int,
    offset: int,
    count: int,
) -> None:
    pagination = body["pagination"]
    assert pagination["total"] == total
    assert pagination["limit"] == limit
    assert pagination["offset"] == offset
    assert pagination["count"] == count
    assert pagination["has_next"] is (offset + count < total)
    assert pagination["has_previous"] is (offset > 0)


def test_report_endpoints_require_authentication(client: TestClient) -> None:
    assert client.get("/api/v1/reports").status_code == 401
    assert client.post("/api/v1/reports", json={"title": "Unauthenticated"}).status_code == 401


def test_document_endpoints_require_authentication(client: TestClient) -> None:
    assert client.get("/api/v1/documents").status_code == 401
    assert client.post(
        "/api/v1/documents",
        json={
            "filename": "unauthenticated.pdf",
            "content_type": "application/pdf",
            "storage_path": "demo/unauthenticated.pdf",
        },
    ).status_code == 401


def test_create_list_update_and_delete_report(client: TestClient) -> None:
    organization_id, tag_id, headers = seed_organization_and_auth(client)

    create_response = client.post(
        "/api/v1/reports",
        headers=headers,
        json={
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
    assert created_report["organization_id"] == organization_id
    assert created_report["title"] == "Daily Field Operations"
    assert created_report["tags"][0]["id"] == tag_id

    list_response = client.get(
        "/api/v1/reports",
        headers=headers,
        params={"search": "Field"},
    )

    assert list_response.status_code == 200
    report_list = list_response.json()
    assert_pagination(report_list, total=1, limit=20, offset=0, count=1)
    assert report_list["items"][0]["id"] == report_id

    update_response = client.patch(
        f"/api/v1/reports/{report_id}",
        headers=headers,
        json={"status": "reviewed", "summary": "Reviewed by operations."},
    )

    assert update_response.status_code == 200
    assert update_response.json()["status"] == "reviewed"
    assert update_response.json()["summary"] == "Reviewed by operations."

    delete_response = client.delete(f"/api/v1/reports/{report_id}", headers=headers)

    assert delete_response.status_code == 204
    assert client.get(f"/api/v1/reports/{report_id}", headers=headers).status_code == 404


def test_create_list_update_and_delete_document(client: TestClient) -> None:
    organization_id, _, headers = seed_organization_and_auth(client)

    report_response = client.post(
        "/api/v1/reports",
        headers=headers,
        json={
            "title": "Safety Inspection",
            "summary": "Inspection report.",
        },
    )
    assert report_response.status_code == 201
    report_id = report_response.json()["id"]

    create_response = client.post(
        "/api/v1/documents",
        headers=headers,
        json={
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
    assert created_document["organization_id"] == organization_id
    assert created_document["filename"] == "safety-inspection.pdf"
    assert created_document["report_id"] == report_id

    list_response = client.get(
        "/api/v1/documents",
        headers=headers,
        params={"search": "safety"},
    )

    assert list_response.status_code == 200
    document_list = list_response.json()
    assert_pagination(document_list, total=1, limit=20, offset=0, count=1)
    assert document_list["items"][0]["id"] == document_id

    update_response = client.patch(
        f"/api/v1/documents/{document_id}",
        headers=headers,
        json={"filename": "updated-safety-inspection.pdf", "size_bytes": 8192},
    )

    assert update_response.status_code == 200
    assert update_response.json()["filename"] == "updated-safety-inspection.pdf"
    assert update_response.json()["size_bytes"] == 8192

    delete_response = client.delete(f"/api/v1/documents/{document_id}", headers=headers)

    assert delete_response.status_code == 204
    assert client.get(f"/api/v1/documents/{document_id}", headers=headers).status_code == 404


def test_report_search_filter_sort_and_pagination(client: TestClient) -> None:
    _, tag_id, headers = seed_organization_and_auth(client)

    reports = [
        {
            "title": "Inventory Follow Up",
            "summary": "Mobile field team checked warehouse inventory.",
            "status": "submitted",
            "source": "mobile-app",
            "reported_at": "2026-07-01T09:00:00",
            "tag_ids": [tag_id],
        },
        {
            "title": "Safety Audit",
            "summary": "Manual inspection review.",
            "status": "reviewed",
            "source": "manual-entry",
            "reported_at": "2026-07-02T09:00:00",
        },
        {
            "title": "Inventory Archive",
            "summary": "Archived inventory note from web intake.",
            "status": "submitted",
            "source": "web-form",
            "reported_at": "2026-07-03T09:00:00",
        },
    ]

    for report in reports:
        response = client.post("/api/v1/reports", headers=headers, json=report)
        assert response.status_code == 201

    filtered_response = client.get(
        "/api/v1/reports",
        headers=headers,
        params={
            "search": "inventory",
            "status": "submitted",
            "source": "mobile-app",
            "tag_id": tag_id,
            "reported_from": "2026-07-01T00:00:00",
            "reported_to": "2026-07-02T00:00:00",
        },
    )

    assert filtered_response.status_code == 200
    filtered_body = filtered_response.json()
    assert_pagination(filtered_body, total=1, limit=20, offset=0, count=1)
    assert filtered_body["items"][0]["title"] == "Inventory Follow Up"

    paginated_response = client.get(
        "/api/v1/reports",
        headers=headers,
        params={"sort_by": "title", "sort_order": "asc", "limit": 2, "offset": 0},
    )

    assert paginated_response.status_code == 200
    paginated_body = paginated_response.json()
    assert [item["title"] for item in paginated_body["items"]] == [
        "Inventory Archive",
        "Inventory Follow Up",
    ]
    assert_pagination(paginated_body, total=3, limit=2, offset=0, count=2)
    assert paginated_body["pagination"]["has_next"] is True
    assert paginated_body["pagination"]["next_offset"] == 2


def test_document_search_filter_sort_and_pagination(client: TestClient) -> None:
    _, _, headers = seed_organization_and_auth(client)

    report_response = client.post(
        "/api/v1/reports",
        headers=headers,
        json={"title": "Document Intake Batch"},
    )
    assert report_response.status_code == 201
    report_id = report_response.json()["id"]

    documents = [
        {
            "report_id": report_id,
            "filename": "field-summary.pdf",
            "content_type": "application/pdf",
            "storage_path": "demo/field-summary.pdf",
            "size_bytes": 2048,
        },
        {
            "report_id": report_id,
            "filename": "invoice.csv",
            "content_type": "text/csv",
            "storage_path": "demo/invoice.csv",
            "size_bytes": 512,
        },
        {
            "report_id": report_id,
            "filename": "inspection-photo.jpg",
            "content_type": "image/jpeg",
            "storage_path": "demo/inspection-photo.jpg",
            "size_bytes": 8192,
        },
    ]

    for document in documents:
        response = client.post("/api/v1/documents", headers=headers, json=document)
        assert response.status_code == 201

    filtered_response = client.get(
        "/api/v1/documents",
        headers=headers,
        params={
            "report_id": report_id,
            "content_type": "application/pdf",
            "min_size_bytes": 1024,
            "max_size_bytes": 4096,
            "search": "field",
        },
    )

    assert filtered_response.status_code == 200
    filtered_body = filtered_response.json()
    assert_pagination(filtered_body, total=1, limit=20, offset=0, count=1)
    assert filtered_body["items"][0]["filename"] == "field-summary.pdf"

    sorted_response = client.get(
        "/api/v1/documents",
        headers=headers,
        params={"sort_by": "size_bytes", "sort_order": "asc", "limit": 2},
    )

    assert sorted_response.status_code == 200
    sorted_body = sorted_response.json()
    assert [item["filename"] for item in sorted_body["items"]] == [
        "invoice.csv",
        "field-summary.pdf",
    ]
    assert_pagination(sorted_body, total=3, limit=2, offset=0, count=2)
    assert sorted_body["pagination"]["has_next"] is True


def test_users_cannot_read_reports_from_other_organizations(client: TestClient) -> None:
    _, _, first_headers = seed_organization_and_auth(client)
    _, _, second_headers = seed_organization_and_auth(client)

    create_response = client.post(
        "/api/v1/reports",
        headers=first_headers,
        json={"title": "Private Operations Report"},
    )
    assert create_response.status_code == 201
    report_id = create_response.json()["id"]

    cross_org_response = client.get(f"/api/v1/reports/{report_id}", headers=second_headers)
    assert cross_org_response.status_code == 404
    assert cross_org_response.json()["detail"] == "Report not found."

    second_list_response = client.get("/api/v1/reports", headers=second_headers)
    assert second_list_response.status_code == 200
    assert second_list_response.json()["pagination"]["total"] == 0


def test_document_rejects_report_from_another_organization(client: TestClient) -> None:
    _, _, first_headers = seed_organization_and_auth(client)
    _, _, second_headers = seed_organization_and_auth(client)

    report_response = client.post(
        "/api/v1/reports",
        headers=first_headers,
        json={"title": "First Organization Report"},
    )
    assert report_response.status_code == 201
    report_id = report_response.json()["id"]

    response = client.post(
        "/api/v1/documents",
        headers=second_headers,
        json={
            "report_id": report_id,
            "filename": "invalid-link.pdf",
            "content_type": "application/pdf",
            "storage_path": "demo/invalid-link.pdf",
            "size_bytes": 128,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Report not found."
