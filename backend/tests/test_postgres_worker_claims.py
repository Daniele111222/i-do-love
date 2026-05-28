"""PostgreSQL worker claim integration tests."""

from __future__ import annotations

import os

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models import Base
from app.models.ingest_job import IngestJob
from app.models.source import Source
from app.services.ingest_service import IngestService

POSTGRES_TEST_DATABASE_URL = os.getenv("POSTGRES_TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    not POSTGRES_TEST_DATABASE_URL,
    reason="POSTGRES_TEST_DATABASE_URL is not configured",
)


@pytest.mark.asyncio
async def test_postgres_workers_claim_distinct_feed_jobs() -> None:
    """Concurrent PostgreSQL workers claim distinct jobs with SKIP LOCKED."""
    assert POSTGRES_TEST_DATABASE_URL is not None
    engine = create_async_engine(POSTGRES_TEST_DATABASE_URL, pool_pre_ping=True)
    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    try:
        async with session_factory() as setup_session:
            source = Source(name="Postgres Feed", url="https://example.com/feed.xml")
            setup_session.add(source)
            await setup_session.flush()
            setup_session.add_all(
                [
                    IngestJob(source_id=source.id, article_id=None, status="pending"),
                    IngestJob(source_id=source.id, article_id=None, status="pending"),
                ]
            )
            await setup_session.commit()

        first_session = session_factory()
        second_session = session_factory()
        async with first_session, second_session:
            first_claimed = await IngestService(first_session).claim_due_feed_jobs(limit=1)
            second_claimed = await IngestService(second_session).claim_due_feed_jobs(limit=1)

        assert len(first_claimed) == 1
        assert len(second_claimed) == 1
        assert first_claimed[0].id != second_claimed[0].id
    finally:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()
