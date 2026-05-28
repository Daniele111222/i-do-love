"""Add ingest job retry fields."""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202605270005"
down_revision: str | None = "202605270004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "ingest_jobs",
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "ingest_jobs",
        sa.Column("next_retry_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "ingest_jobs",
        sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True),
    )
    bind = op.get_bind()
    if bind.dialect.name != "sqlite":
        op.alter_column("ingest_jobs", "attempt_count", server_default=None)


def downgrade() -> None:
    op.drop_column("ingest_jobs", "locked_at")
    op.drop_column("ingest_jobs", "next_retry_at")
    op.drop_column("ingest_jobs", "attempt_count")
