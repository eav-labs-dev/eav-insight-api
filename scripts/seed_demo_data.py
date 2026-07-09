"""Seed demo data for local EAV Insight development.

Run after applying migrations:

    alembic upgrade head
    python scripts/seed_demo_data.py
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import Document, Organization, Report, Tag, User


def seed(session: Session) -> None:
    """Create a small demo workspace if it does not already exist."""
    existing_org = session.scalar(
        select(Organization).where(Organization.slug == "demo-operations")
    )

    if existing_org is not None:
        print("Demo data already exists. Skipping seed.")
        return

    organization = Organization(name="Demo Operations Ltd", slug="demo-operations")
    user = User(
        organization=organization,
        email="admin@example.com",
        full_name="Demo Admin",
        role="admin",
    )
    urgent_tag = Tag(organization=organization, name="Urgent", slug="urgent")
    field_tag = Tag(organization=organization, name="Field Report", slug="field-report")
    report = Report(
        organization=organization,
        title="Warehouse Intake Summary",
        summary="Initial demo report for document intake and operational tracking.",
        status="published",
        source="manual-entry",
        tags=[urgent_tag, field_tag],
    )
    document = Document(
        organization=organization,
        report=report,
        filename="warehouse-intake-summary.pdf",
        content_type="application/pdf",
        storage_path="demo/warehouse-intake-summary.pdf",
        size_bytes=245760,
    )

    session.add_all([organization, user, urgent_tag, field_tag, report, document])
    session.commit()
    print("Demo data seeded successfully.")


def main() -> None:
    """Seed demo records using the configured database connection."""
    with SessionLocal() as session:
        seed(session)


if __name__ == "__main__":
    main()
