from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.report import Report
from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.association_tables import report_tags
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Tag(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A reusable label for categorizing reports."""

    __tablename__ = "tags"
    __table_args__ = (UniqueConstraint("organization_id", "slug", name="uq_tags_org_slug"),)

    organization_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    slug: Mapped[str] = mapped_column(String(80), nullable=False)

    organization: Mapped[Organization] = relationship(back_populates="tags")
    reports: Mapped[list[Report]] = relationship(
        secondary=report_tags,
        back_populates="tags",
    )
