"""Database initialization helpers."""

from __future__ import annotations

from sqlalchemy import text

from app.database import engine
from app.models import Base


async def create_tables() -> None:
    """Create database tables for all registered SQLAlchemy models."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def list_tables() -> list[str]:
    """Return public table names for PostgreSQL or SQLite test databases."""
    async with engine.connect() as conn:
        dialect = conn.dialect.name
        if dialect == "postgresql":
            result = await conn.execute(
                text(
                    """
                    SELECT tablename
                    FROM pg_catalog.pg_tables
                    WHERE schemaname = 'public'
                    ORDER BY tablename
                    """
                )
            )
        else:
            result = await conn.execute(
                text(
                    """
                    SELECT name
                    FROM sqlite_master
                    WHERE type = 'table'
                    ORDER BY name
                    """
                )
            )
        return [row[0] for row in result]
