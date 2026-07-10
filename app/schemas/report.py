from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import PaginationMeta

ReportStatus = Literal["draft", "submitted", "reviewed", "archived"]


class TagSummary(BaseModel):
    """Compact tag representation returned with reports."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str


class ReportCreate(BaseModel):
    """Payload for creating an operational report."""

    organization_id: str
    title: str = Field(min_length=3, max_length=200)
    summary: str | None = None
    status: ReportStatus = "draft"
    source: str | None = Field(default=None, max_length=80)
    reported_at: datetime | None = None
    tag_ids: list[str] = Field(default_factory=list)


class ReportUpdate(BaseModel):
    """Payload for updating an operational report."""

    title: str | None = Field(default=None, min_length=3, max_length=200)
    summary: str | None = None
    status: ReportStatus | None = None
    source: str | None = Field(default=None, max_length=80)
    reported_at: datetime | None = None
    tag_ids: list[str] | None = None


class ReportResponse(BaseModel):
    """Report response model."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    title: str
    summary: str | None
    status: str
    source: str | None
    reported_at: datetime | None
    created_at: datetime
    updated_at: datetime
    tags: list[TagSummary] = Field(default_factory=list)


class ReportListResponse(BaseModel):
    """Paginated report list response."""

    items: list[ReportResponse]
    pagination: PaginationMeta
