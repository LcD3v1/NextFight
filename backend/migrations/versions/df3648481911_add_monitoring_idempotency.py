"""add monitoring idempotency.

Revision ID: df3648481911
Revises: 5dd3800faa24
Create Date: 2026-07-12 21:53:23.296683
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "df3648481911"
down_revision: str | None = "5dd3800faa24"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Apply the migration."""
    op.add_column(
        "fight_state_events",
        sa.Column("idempotency_key", sa.String(length=160), nullable=True),
    )
    op.execute(
        "UPDATE fight_state_events "
        "SET idempotency_key = 'legacy:' || id::text "
        "WHERE idempotency_key IS NULL"
    )
    op.alter_column("fight_state_events", "idempotency_key", nullable=False)
    op.create_unique_constraint(
        op.f("uq_fight_state_events_idempotency_key"),
        "fight_state_events",
        ["idempotency_key"],
    )


def downgrade() -> None:
    """Revert the migration."""
    op.drop_constraint(
        op.f("uq_fight_state_events_idempotency_key"),
        "fight_state_events",
        type_="unique",
    )
    op.drop_column("fight_state_events", "idempotency_key")
