from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models import Organization, Report, Tag
from app.schemas.common import PaginationMeta
from app.schemas.report import ReportCreate, ReportListResponse, ReportResponse, ReportUpdate

router = APIRouter(prefix="/reports", tags=["reports"])

DbSession = Annotated[Session, Depends(get_db)]


def _get_report_or_404(db: Session, report_id: str) -> Report:
    report = db.scalar(
        select(Report)
        .options(selectinload(Report.tags))
        .where(Report.id == report_id)
    )
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found.",
        )
    return report


def _ensure_organization_exists(db: Session, organization_id: str) -> Organization:
    organization = db.get(Organization, organization_id)
    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found.",
        )
    return organization


def _load_tags(db: Session, organization_id: str, tag_ids: list[str]) -> list[Tag]:
    if not tag_ids:
        return []

    tags = list(
        db.scalars(
            select(Tag).where(
                Tag.organization_id == organization_id,
                Tag.id.in_(tag_ids),
            )
        )
    )
    if len(tags) != len(set(tag_ids)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more tags were not found for this organization.",
        )
    return tags


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(payload: ReportCreate, db: DbSession) -> Report:
    """Create a report record for an organization."""
    _ensure_organization_exists(db, payload.organization_id)
    tags = _load_tags(db, payload.organization_id, payload.tag_ids)

    report = Report(
        organization_id=payload.organization_id,
        title=payload.title,
        summary=payload.summary,
        status=payload.status,
        source=payload.source,
        reported_at=payload.reported_at,
        tags=tags,
    )

    db.add(report)
    db.commit()
    db.refresh(report)
    return _get_report_or_404(db, report.id)


@router.get("", response_model=ReportListResponse)
def list_reports(
    db: DbSession,
    organization_id: Annotated[str | None, Query()] = None,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    search: Annotated[str | None, Query(min_length=2)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> ReportListResponse:
    """List reports with basic filtering, search, and pagination."""
    filters = []

    if organization_id is not None:
        filters.append(Report.organization_id == organization_id)
    if status_filter is not None:
        filters.append(Report.status == status_filter)
    if search is not None:
        pattern = f"%{search}%"
        filters.append(
            or_(
                Report.title.ilike(pattern),
                Report.summary.ilike(pattern),
                Report.source.ilike(pattern),
            )
        )

    base_query = select(Report).where(*filters)
    total = db.scalar(select(func.count()).select_from(base_query.subquery())) or 0
    reports = list(
        db.scalars(
            base_query.options(selectinload(Report.tags))
            .order_by(Report.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
    )

    return ReportListResponse(
        items=[ReportResponse.model_validate(report) for report in reports],
        pagination=PaginationMeta(total=total, limit=limit, offset=offset),
    )


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(report_id: str, db: DbSession) -> Report:
    """Return a single report by ID."""
    return _get_report_or_404(db, report_id)


@router.patch("/{report_id}", response_model=ReportResponse)
def update_report(report_id: str, payload: ReportUpdate, db: DbSession) -> Report:
    """Update a report record."""
    report = _get_report_or_404(db, report_id)
    update_data = payload.model_dump(exclude_unset=True)

    tag_ids = update_data.pop("tag_ids", None)
    if tag_ids is not None:
        report.tags = _load_tags(db, report.organization_id, tag_ids)

    for field, value in update_data.items():
        setattr(report, field, value)

    db.add(report)
    db.commit()
    db.refresh(report)
    return _get_report_or_404(db, report.id)


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(report_id: str, db: DbSession) -> None:
    """Delete a report record."""
    report = _get_report_or_404(db, report_id)
    db.delete(report)
    db.commit()
