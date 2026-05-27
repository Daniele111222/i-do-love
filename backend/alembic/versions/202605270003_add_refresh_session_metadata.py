"""Add refresh token session metadata."""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202605270003"
down_revision: str | None = "202605270002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "refresh_token_sessions",
        sa.Column("ip_address", sa.String(length=45), nullable=True),
    )
    op.add_column(
        "refresh_token_sessions",
        sa.Column("user_agent", sa.String(length=512), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("refresh_token_sessions", "user_agent")
    op.drop_column("refresh_token_sessions", "ip_address")
