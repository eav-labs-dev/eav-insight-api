from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import PaginationMeta


class DocumentCreate(BaseModel):
    """Payload for registering a document record."""

    organization_id: str
    report_id: str | None = None
    filename: str = Field(min_length=1, max_length=255)
    content_type: str = Field(min_length=3, max_length=120)
    storage_path: str = Field(min_length=1, max_length=500)
    size_bytes: int = Field(default=0, ge=0)


class DocumentUpdate(BaseModel):
    """Payload for updating a document record."""

    report_id: str | None = None
    filename: str | None = Field(default=None, min_length=1, max_length=255)
    content_type: str | None = Field(default=None, min_length=3, max_length=120)
    storage_path: str | None = Field(default=None, min_length=1, max_length=500)
    size_bytes: int | None = Field(default=None, ge=0)


class DocumentResponse(BaseModel):
    """Document response model."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    report_id: str | None
    filename: str
    content_type: str
    storage_path: str
    size_bytes: int
    created_at: datetime
    updated_at: datetime


class DocumentListResponse(BaseModel):
    """Paginated document list response."""

    items: list[DocumentResponse]
    pagination: PaginationMeta
