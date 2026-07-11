"""add user password hash

Revision ID: 20260710_0002
Revises: 20260709_0001
Create Date: 2026-07-10 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260710_0002"
down_revision: str | None = "20260709_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add password hash storage to users."""
    op.add_column(
        "users",
        sa.Column(
            "password_hash",
            sa.String(length=255),
            nullable=False,
            server_default="not-configured",
        ),
    )


def downgrade() -> None:
    """Remove password hash storage from users."""
    op.drop_column("users", "password_hash")
