"""Alembic migration tests."""

from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


def test_alembic_upgrade_head_creates_users_table(tmp_path: Path) -> None:
    database_path = tmp_path / "migration-test.db"
    database_url = f"sqlite:///{database_path.as_posix()}"

    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", database_url)

    command.upgrade(config, "head")

    engine = create_engine(database_url)
    try:
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        assert "users" in table_names
        assert "refresh_token_sessions" in table_names
        assert "sources" in table_names
        assert "articles" in table_names
        assert "ingest_jobs" in table_names
        columns = {column["name"] for column in inspector.get_columns("users")}
        session_columns = {
            column["name"] for column in inspector.get_columns("refresh_token_sessions")
        }
        source_columns = {column["name"] for column in inspector.get_columns("sources")}
        article_columns = {column["name"] for column in inspector.get_columns("articles")}
        ingest_job_columns = {
            column["name"] for column in inspector.get_columns("ingest_jobs")
        }
    finally:
        engine.dispose()

    assert {
        "id",
        "email",
        "nickname",
        "hashed_password",
        "is_active",
        "is_superuser",
        "role",
        "created_at",
        "updated_at",
    } <= columns
    assert {
        "id",
        "user_id",
        "token_id",
        "token_hash",
        "expires_at",
        "revoked_at",
        "ip_address",
        "user_agent",
        "created_at",
    } <= session_columns
    assert {"id", "name", "url", "created_at", "updated_at"} <= source_columns
    assert {
        "id",
        "source_id",
        "title",
        "content",
        "source_url",
        "author",
        "published_at",
        "tags",
        "created_at",
        "updated_at",
    } <= article_columns
    assert {
        "id",
        "source_id",
        "article_id",
        "status",
        "error_message",
        "created_at",
        "updated_at",
    } <= ingest_job_columns
