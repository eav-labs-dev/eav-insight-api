"""Document routes scoped to the authenticated user's organization."""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import ColumnElement, func, or_, select
from sqlalchemy.orm import Session

from app.api.dependencies import CurrentUser
from app.core.exceptions import not_found
from app.db.session import get_db
from app.models import Document, Report
from app.schemas.common import PaginationMeta
from app.schemas.document import (
    DocumentCreate,
    DocumentListResponse,
    DocumentResponse,
    DocumentUpdate,
)

router = APIRouter(prefix="/documents", tags=["documents"])

DbSession = Annotated[Session, Depends(get_db)]
DocumentSortBy = Literal["created_at", "filename", "content_type", "size_bytes"]
SortOrder = Literal["asc", "desc"]


def _get_document_or_404(db: Session, document_id: str, organization_id: str) -> Document:
    document = db.scalar(
        select(Document).where(
            Document.id == document_id,
            Document.organization_id == organization_id,
        )
    )
    if document is None:
        raise not_found("Document not found.")
    return document


def _ensure_report_belongs_to_organization(
    db: Session,
    report_id: str | None,
    organization_id: str,
) -> None:
    if report_id is None:
        return

    report = db.scalar(
        select(Report).where(
            Report.id == report_id,
            Report.organization_id == organization_id,
        )
    )
    if report is None:
        raise not_found("Report not found.")


def _get_document_sort_column(sort_by: DocumentSortBy) -> ColumnElement[object]:
    sort_columns: dict[str, ColumnElement[object]] = {
        "created_at": Document.created_at,
        "filename": Document.filename,
        "content_type": Document.content_type,
        "size_bytes": Document.size_bytes,
    }
    return sort_columns[sort_by]


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    payload: DocumentCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> Document:
    """Register a document under the authenticated user's organization."""
    _ensure_report_belongs_to_organization(
        db,
        payload.report_id,
        current_user.organization_id,
    )

    document = Document(
        organization_id=current_user.organization_id,
        report_id=payload.report_id,
        filename=payload.filename,
        content_type=payload.content_type,
        storage_path=payload.storage_path,
        size_bytes=payload.size_bytes,
    )

    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.get("", response_model=DocumentListResponse)
def list_documents(
    db: DbSession,
    current_user: CurrentUser,
    report_id: Annotated[str | None, Query()] = None,
    content_type: Annotated[str | None, Query()] = None,
    min_size_bytes: Annotated[int | None, Query(ge=0)] = None,
    max_size_bytes: Annotated[int | None, Query(ge=0)] = None,
    search: Annotated[str | None, Query(min_length=2)] = None,
    sort_by: Annotated[DocumentSortBy, Query()] = "created_at",
    sort_order: Annotated[SortOrder, Query()] = "desc",
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> DocumentListResponse:
    """List searchable, filterable documents for the current user's organization."""
    filters = [Document.organization_id == current_user.organization_id]

    if report_id is not None:
        filters.append(Document.report_id == report_id)
    if content_type is not None:
        filters.append(Document.content_type == content_type)
    if min_size_bytes is not None:
        filters.append(Document.size_bytes >= min_size_bytes)
    if max_size_bytes is not None:
        filters.append(Document.size_bytes <= max_size_bytes)
    if search is not None:
        pattern = f"%{search}%"
        filters.append(
            or_(
                Document.filename.ilike(pattern),
                Document.storage_path.ilike(pattern),
                Document.content_type.ilike(pattern),
            )
        )

    base_query = select(Document).where(*filters)
    total = db.scalar(select(func.count()).select_from(base_query.subquery())) or 0

    sort_column = _get_document_sort_column(sort_by)
    order_expression = sort_column.asc() if sort_order == "asc" else sort_column.desc()
    documents = list(
        db.scalars(
            base_query.order_by(order_expression, Document.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
    )

    return DocumentListResponse(
        items=[DocumentResponse.model_validate(document) for document in documents],
        pagination=PaginationMeta.from_values(
            total=total,
            limit=limit,
            offset=offset,
            count=len(documents),
        ),
    )


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: str, db: DbSession, current_user: CurrentUser) -> Document:
    """Return a single document visible to the authenticated user."""
    return _get_document_or_404(db, document_id, current_user.organization_id)


@router.patch("/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: str,
    payload: DocumentUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> Document:
    """Update a document visible to the authenticated user."""
    document = _get_document_or_404(db, document_id, current_user.organization_id)
    update_data = payload.model_dump(exclude_unset=True)

    if "report_id" in update_data:
        _ensure_report_belongs_to_organization(
            db,
            update_data["report_id"],
            current_user.organization_id,
        )

    for field, value in update_data.items():
        setattr(document, field, value)

    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: str, db: DbSession, current_user: CurrentUser) -> None:
    """Delete a document visible to the authenticated user."""
    document = _get_document_or_404(db, document_id, current_user.organization_id)
    db.delete(document)
    db.commit()
