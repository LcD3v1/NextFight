"""add reliable push delivery queue.

Revision ID: 450057107163
Revises: cdafc122160f
Create Date: 2026-07-13 00:01:06.625504
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "450057107163"
down_revision: str | None = "cdafc122160f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Apply the migration."""
    op.add_column(
        "alert_deliveries",
        sa.Column(
            "title", sa.String(length=180), server_default="NextFight", nullable=False
        ),
    )
    op.add_column(
        "alert_deliveries",
        sa.Column("body", sa.String(length=500), server_default="", nullable=False),
    )
    op.add_column(
        "alert_deliveries",
        sa.Column(
            "data",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
    )
    op.add_column(
        "alert_deliveries",
        sa.Column("attempts", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "alert_deliveries",
        sa.Column(
            "next_attempt_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.alter_column(
        "alert_deliveries",
        "attempted_at",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=True,
    )
    op.create_index(
        op.f("ix_alert_deliveries_next_attempt_at"),
        "alert_deliveries",
        ["next_attempt_at"],
        unique=False,
    )
    for column in ("title", "body", "data", "attempts", "next_attempt_at"):
        op.alter_column("alert_deliveries", column, server_default=None)


def downgrade() -> None:
    """Revert the migration."""
    op.drop_index(
        op.f("ix_alert_deliveries_next_attempt_at"),
        table_name="alert_deliveries",
    )
    op.execute(
        "UPDATE alert_deliveries SET attempted_at = created_at "
        "WHERE attempted_at IS NULL"
    )
    op.alter_column(
        "alert_deliveries",
        "attempted_at",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=False,
    )
    op.drop_column("alert_deliveries", "next_attempt_at")
    op.drop_column("alert_deliveries", "attempts")
    op.drop_column("alert_deliveries", "data")
    op.drop_column("alert_deliveries", "body")
    op.drop_column("alert_deliveries", "title")
