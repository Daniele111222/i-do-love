"""Create ingestion tables."""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202605270004"
down_revision: str | None = "202605270003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "sources",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name=op.f("uq_sources_name")),
        sa.UniqueConstraint("url", name=op.f("uq_sources_url")),
    )
    op.create_index(op.f("ix_sources_name"), "sources", ["name"], unique=False)

    op.create_table(
        "articles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("source_url", sa.String(length=2048), nullable=True),
        sa.Column("author", sa.String(length=255), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_url", name=op.f("uq_articles_source_url")),
    )
    op.create_index(op.f("ix_articles_source_id"), "articles", ["source_id"], unique=False)
    op.create_index(op.f("ix_articles_source_url"), "articles", ["source_url"], unique=True)

    op.create_table(
        "ingest_jobs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column("article_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_ingest_jobs_article_id"),
        "ingest_jobs",
        ["article_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ingest_jobs_source_id"),
        "ingest_jobs",
        ["source_id"],
        unique=False,
    )
    op.create_index(op.f("ix_ingest_jobs_status"), "ingest_jobs", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_ingest_jobs_status"), table_name="ingest_jobs")
    op.drop_index(op.f("ix_ingest_jobs_source_id"), table_name="ingest_jobs")
    op.drop_index(op.f("ix_ingest_jobs_article_id"), table_name="ingest_jobs")
    op.drop_table("ingest_jobs")
    op.drop_index(op.f("ix_articles_source_url"), table_name="articles")
    op.drop_index(op.f("ix_articles_source_id"), table_name="articles")
    op.drop_table("articles")
    op.drop_index(op.f("ix_sources_name"), table_name="sources")
    op.drop_table("sources")
