from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Document, Organization, Report
from app.schemas.common import PaginationMeta
from app.schemas.document import (
    DocumentCreate,
    DocumentListResponse,
    DocumentResponse,
    DocumentUpdate,
)

router = APIRouter(prefix="/documents", tags=["documents"])

DbSession = Annotated[Session, Depends(get_db)]


def _get_document_or_404(db: Session, document_id: str) -> Document:
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )
    return document


def _ensure_organization_exists(db: Session, organization_id: str) -> Organization:
    organization = db.get(Organization, organization_id)
    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found.",
        )
    return organization


def _ensure_report_belongs_to_organization(
    db: Session,
    report_id: str | None,
    organization_id: str,
) -> None:
    if report_id is None:
        return

    report = db.get(Report, report_id)
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found.",
        )
    if report.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Report does not belong to the selected organization.",
        )


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(payload: DocumentCreate, db: DbSession) -> Document:
    """Register a document record."""
    _ensure_organization_exists(db, payload.organization_id)
    _ensure_report_belongs_to_organization(db, payload.report_id, payload.organization_id)

    document = Document(
        organization_id=payload.organization_id,
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
    organization_id: Annotated[str | None, Query()] = None,
    report_id: Annotated[str | None, Query()] = None,
    content_type: Annotated[str | None, Query()] = None,
    search: Annotated[str | None, Query(min_length=2)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> DocumentListResponse:
    """List documents with basic filtering, search, and pagination."""
    filters = []

    if organization_id is not None:
        filters.append(Document.organization_id == organization_id)
    if report_id is not None:
        filters.append(Document.report_id == report_id)
    if content_type is not None:
        filters.append(Document.content_type == content_type)
    if search is not None:
        pattern = f"%{search}%"
        filters.append(
            or_(
                Document.filename.ilike(pattern),
                Document.storage_path.ilike(pattern),
            )
        )

    base_query = select(Document).where(*filters)
    total = db.scalar(select(func.count()).select_from(base_query.subquery())) or 0
    documents = list(
        db.scalars(
            base_query.order_by(Document.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
    )

    return DocumentListResponse(
        items=[DocumentResponse.model_validate(document) for document in documents],
        pagination=PaginationMeta(total=total, limit=limit, offset=offset),
    )


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: str, db: DbSession) -> Document:
    """Return a single document by ID."""
    return _get_document_or_404(db, document_id)


@router.patch("/{document_id}", response_model=DocumentResponse)
def update_document(document_id: str, payload: DocumentUpdate, db: DbSession) -> Document:
    """Update a document record."""
    document = _get_document_or_404(db, document_id)
    update_data = payload.model_dump(exclude_unset=True)

    if "report_id" in update_data:
        _ensure_report_belongs_to_organization(
            db,
            update_data["report_id"],
            document.organization_id,
        )

    for field, value in update_data.items():
        setattr(document, field, value)

    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: str, db: DbSession) -> None:
    """Delete a document record."""
    document = _get_document_or_404(db, document_id)
    db.delete(document)
    db.commit()
