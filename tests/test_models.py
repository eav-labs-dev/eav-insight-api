from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.models import Base, Document, Organization, Report, Tag, User


def test_core_models_can_be_created_with_relationships() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        organization = Organization(name="EAV Demo", slug="eav-demo")
        user = User(
            organization=organization,
            email="owner@example.com",
            full_name="Demo Owner",
            role="admin",
        )
        tag = Tag(organization=organization, name="Operations", slug="operations")
        report = Report(
            organization=organization,
            title="Daily Operations Report",
            summary="A sample operational report.",
            status="published",
            source="manual-entry",
            tags=[tag],
        )
        document = Document(
            organization=organization,
            report=report,
            filename="daily-operations.pdf",
            content_type="application/pdf",
            storage_path="demo/daily-operations.pdf",
            size_bytes=1024,
        )

        session.add_all([organization, user, tag, report, document])
        session.commit()

        saved_report = session.scalar(
            select(Report).where(Report.title == "Daily Operations Report")
        )

        assert saved_report is not None
        assert saved_report.organization.slug == "eav-demo"
        assert saved_report.documents[0].filename == "daily-operations.pdf"
        assert saved_report.tags[0].slug == "operations"
        assert organization.users[0].email == "owner@example.com"
