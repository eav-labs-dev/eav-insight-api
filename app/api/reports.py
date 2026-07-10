"""Report routes scoped to the authenticated user's organization."""

from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import ColumnElement, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.api.dependencies import CurrentUser
from app.db.session import get_db
from app.models import Report, Tag
from app.schemas.common import PaginationMeta
from app.schemas.report import ReportCreate, ReportListResponse, ReportResponse, ReportUpdate

router = APIRouter(prefix="/reports", tags=["reports"])

DbSession = Annotated[Session, Depends(get_db)]
ReportSortBy = Literal["created_at", "reported_at", "title", "status"]
SortOrder = Literal["asc", "desc"]


def _get_report_or_404(db: Session, report_id: str, organization_id: str) -> Report:
    report = db.scalar(
        select(Report)
        .options(selectinload(Report.tags))
        .where(
            Report.id == report_id,
            Report.organization_id == organization_id,
        )
    )
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found.",
        )
    return report


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


def _get_report_sort_column(sort_by: ReportSortBy) -> ColumnElement[object]:
    sort_columns: dict[str, ColumnElement[object]] = {
        "created_at": Report.created_at,
        "reported_at": Report.reported_at,
        "title": Report.title,
        "status": Report.status,
    }
    return sort_columns[sort_by]


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(
    payload: ReportCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> Report:
    """Create a report record under the authenticated user's organization."""
    tags = _load_tags(db, current_user.organization_id, payload.tag_ids)

    report = Report(
        organization_id=current_user.organization_id,
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
    return _get_report_or_404(db, report.id, current_user.organization_id)


@router.get("", response_model=ReportListResponse)
def list_reports(
    db: DbSession,
    current_user: CurrentUser,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    source: Annotated[str | None, Query(max_length=80)] = None,
    tag_id: Annotated[str | None, Query()] = None,
    reported_from: Annotated[datetime | None, Query()] = None,
    reported_to: Annotated[datetime | None, Query()] = None,
    search: Annotated[str | None, Query(min_length=2)] = None,
    sort_by: Annotated[ReportSortBy, Query()] = "created_at",
    sort_order: Annotated[SortOrder, Query()] = "desc",
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> ReportListResponse:
    """List searchable, filterable reports for the current user's organization."""
    filters = [Report.organization_id == current_user.organization_id]

    if status_filter is not None:
        filters.append(Report.status == status_filter)
    if source is not None:
        filters.append(Report.source == source)
    if tag_id is not None:
        filters.append(Report.tags.any(Tag.id == tag_id))
    if reported_from is not None:
        filters.append(Report.reported_at >= reported_from)
    if reported_to is not None:
        filters.append(Report.reported_at <= reported_to)
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

    sort_column = _get_report_sort_column(sort_by)
    order_expression = sort_column.asc() if sort_order == "asc" else sort_column.desc()
    reports = list(
        db.scalars(
            base_query.options(selectinload(Report.tags))
            .order_by(order_expression, Report.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
    )

    return ReportListResponse(
        items=[ReportResponse.model_validate(report) for report in reports],
        pagination=PaginationMeta.from_values(
            total=total,
            limit=limit,
            offset=offset,
            count=len(reports),
        ),
    )


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(report_id: str, db: DbSession, current_user: CurrentUser) -> Report:
    """Return a single report visible to the authenticated user."""
    return _get_report_or_404(db, report_id, current_user.organization_id)


@router.patch("/{report_id}", response_model=ReportResponse)
def update_report(
    report_id: str,
    payload: ReportUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> Report:
    """Update a report record visible to the authenticated user."""
    report = _get_report_or_404(db, report_id, current_user.organization_id)
    update_data = payload.model_dump(exclude_unset=True)

    tag_ids = update_data.pop("tag_ids", None)
    if tag_ids is not None:
        report.tags = _load_tags(db, current_user.organization_id, tag_ids)

    for field, value in update_data.items():
        setattr(report, field, value)

    db.add(report)
    db.commit()
    db.refresh(report)
    return _get_report_or_404(db, report.id, current_user.organization_id)


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(report_id: str, db: DbSession, current_user: CurrentUser) -> None:
    """Delete a report visible to the authenticated user."""
    report = _get_report_or_404(db, report_id, current_user.organization_id)
    db.delete(report)
    db.commit()
