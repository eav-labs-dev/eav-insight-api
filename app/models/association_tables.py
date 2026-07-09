from sqlalchemy import Column, ForeignKey, Table

from app.models.base import Base

report_tags = Table(
    "report_tags",
    Base.metadata,
    Column("report_id", ForeignKey("reports.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)
