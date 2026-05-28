"""Ingestion API tests."""

from __future__ import annotations

import hashlib
import hmac
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.dialects import postgresql
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.article import Article
from app.models.ingest_job import IngestJob
from app.models.source import Source
from app.services.ingest_service import IngestService


@pytest.mark.asyncio
async def test_webhook_rejects_missing_signature(client: AsyncClient) -> None:
    """Webhook requests must include a signature."""
    response = await client.post(
        "/api/v1/ingest/webhook",
        json={"title": "Hello", "content": "World"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_webhook_accepts_valid_signature(client: AsyncClient) -> None:
    """Webhook requests with a valid raw-body signature are accepted."""
    body = b'{"title":"Hello","content":"World"}'
    signature = hmac.new(
        key=settings.WEBHOOK_SECRET.encode(),
        msg=body,
        digestmod=hashlib.sha256,
    ).hexdigest()

    response = await client.post(
        "/api/v1/ingest/webhook",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Signature": f"sha256={signature}",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "accepted"


@pytest.mark.asyncio
async def test_webhook_persists_article_source_and_job(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """A valid webhook stores source, article, and a successful ingest job."""
    body = (
        b'{"title":"Stored","content":"Body","source_url":"https://example.com/a",'
        b'"source_name":"Example","author":"Ada","published_at":"2026-05-27T00:00:00Z",'
        b'"tags":["ai","news"]}'
    )
    signature = hmac.new(
        key=settings.WEBHOOK_SECRET.encode(),
        msg=body,
        digestmod=hashlib.sha256,
    ).hexdigest()

    response = await client.post(
        "/api/v1/ingest/webhook",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Signature": f"sha256={signature}",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "accepted"
    assert data["id"] is not None

    article = await db_session.get(Article, data["id"])
    assert article is not None
    assert article.title == "Stored"
    assert article.source_url == "https://example.com/a"
    assert article.tags == ["ai", "news"]

    source = await db_session.get(Source, article.source_id)
    assert source is not None
    assert source.name == "Example"

    job = (
        await db_session.execute(
            select(IngestJob).where(IngestJob.article_id == article.id)
        )
    ).scalar_one()
    assert job.status == "success"


@pytest.mark.asyncio
async def test_webhook_is_idempotent_by_source_url(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Posting the same source URL updates the article instead of duplicating it."""
    first_body = (
        b'{"title":"Original","content":"Body","source_url":"https://example.com/same",'
        b'"source_name":"Example"}'
    )
    second_body = (
        b'{"title":"Updated","content":"New Body","source_url":"https://example.com/same",'
        b'"source_name":"Example"}'
    )

    first_signature = hmac.new(
        key=settings.WEBHOOK_SECRET.encode(),
        msg=first_body,
        digestmod=hashlib.sha256,
    ).hexdigest()
    second_signature = hmac.new(
        key=settings.WEBHOOK_SECRET.encode(),
        msg=second_body,
        digestmod=hashlib.sha256,
    ).hexdigest()

    first_response = await client.post(
        "/api/v1/ingest/webhook",
        content=first_body,
        headers={"Content-Type": "application/json", "X-Signature": f"sha256={first_signature}"},
    )
    second_response = await client.post(
        "/api/v1/ingest/webhook",
        content=second_body,
        headers={"Content-Type": "application/json", "X-Signature": f"sha256={second_signature}"},
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert second_response.json()["id"] == first_response.json()["id"]

    articles = (
        await db_session.execute(
            select(Article).where(Article.source_url == "https://example.com/same")
        )
    ).scalars().all()
    assert len(articles) == 1
    assert articles[0].title == "Updated"


@pytest.mark.asyncio
async def test_feed_ingestion_creates_pending_job(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Feed ingestion creates a durable pending job for later workers."""
    response = await client.post(
        "/api/v1/ingest/feed",
        params={"feed_url": "https://example.com/feed.xml", "source_name": "Example Feed"},
    )

    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "queued"
    assert data["job_id"] is not None
    assert data["source_id"] is not None
    assert data["feed_url"] == "https://example.com/feed.xml"

    job = await db_session.get(IngestJob, data["job_id"])
    assert job is not None
    assert job.status == "pending"
    assert job.article_id is None

    source = await db_session.get(Source, data["source_id"])
    assert source is not None
    assert source.name == "Example Feed"
    assert source.url == "https://example.com/feed.xml"


@pytest.mark.asyncio
async def test_ingest_status_uses_database_job_counts(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Ingestion status reflects persisted job states."""
    source = Source(name="Status Feed", url="https://example.com/status.xml")
    db_session.add(source)
    await db_session.flush()
    db_session.add_all(
        [
            IngestJob(source_id=source.id, status="success"),
            IngestJob(source_id=source.id, status="failed", error_message="bad feed"),
            IngestJob(source_id=source.id, status="pending"),
        ]
    )
    await db_session.commit()

    response = await client.get("/api/v1/ingest/status")

    assert response.status_code == 200
    assert response.json() == {
        "total_processed": 3,
        "total_success": 1,
        "total_failed": 1,
    }


@pytest.mark.asyncio
async def test_ingest_queue_status_reports_worker_backlog(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Queue status exposes worker backlog and stale processing counts."""
    source = Source(name="Queue Feed", url="https://example.com/queue.xml")
    db_session.add(source)
    await db_session.flush()
    db_session.add_all(
        [
            IngestJob(source_id=source.id, article_id=None, status="pending"),
            IngestJob(
                source_id=source.id,
                article_id=None,
                status="retrying",
                next_retry_at=datetime.now(UTC) - timedelta(seconds=1),
            ),
            IngestJob(
                source_id=source.id,
                article_id=None,
                status="retrying",
                next_retry_at=datetime.now(UTC) + timedelta(minutes=5),
            ),
            IngestJob(
                source_id=source.id,
                article_id=None,
                status="processing",
                locked_at=datetime.now(UTC) - timedelta(minutes=20),
            ),
            IngestJob(
                source_id=source.id,
                article_id=None,
                status="processing",
                locked_at=datetime.now(UTC),
            ),
            IngestJob(source_id=source.id, article_id=None, status="failed"),
        ]
    )
    await db_session.commit()

    response = await client.get("/api/v1/ingest/queue")

    assert response.status_code == 200
    assert response.json() == {
        "pending": 1,
        "retrying": 2,
        "retry_due": 1,
        "processing": 2,
        "stale_processing": 1,
        "failed": 1,
        "claimable": 3,
    }


@pytest.mark.asyncio
async def test_process_feed_job_ingests_rss_items(
    db_session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Feed worker fetches RSS, upserts articles, and marks the job successful."""
    service = IngestService(db_session)
    job = await service.queue_feed(
        feed_url="https://example.com/rss.xml",
        source_name="RSS Source",
    )
    feed_xml = """
    <rss version="2.0">
      <channel>
        <title>Example Feed</title>
        <item>
          <title>First Item</title>
          <link>https://example.com/first</link>
          <description>First body</description>
          <author>author@example.com</author>
          <pubDate>Wed, 27 May 2026 00:00:00 GMT</pubDate>
        </item>
        <item>
          <title>Second Item</title>
          <link>https://example.com/second</link>
          <description>Second body</description>
        </item>
      </channel>
    </rss>
    """

    async def fake_fetch_feed(feed_url: str) -> str:
        assert feed_url == "https://example.com/rss.xml"
        return feed_xml

    monkeypatch.setattr(service, "_fetch_feed", fake_fetch_feed)

    processed = await service.process_feed_job(job.id)

    assert processed == 2
    refreshed_job = await db_session.get(IngestJob, job.id)
    assert refreshed_job is not None
    assert refreshed_job.status == "success"
    assert refreshed_job.error_message is None

    articles = (
        await db_session.execute(select(Article).order_by(Article.source_url))
    ).scalars().all()
    assert [article.title for article in articles] == ["First Item", "Second Item"]
    assert articles[0].content == "First body"
    assert articles[0].source_url == "https://example.com/first"


@pytest.mark.asyncio
async def test_process_feed_job_marks_failed_when_fetch_fails(
    db_session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Feed worker records failures on the job for retry/inspection."""
    service = IngestService(db_session)
    job = await service.queue_feed(
        feed_url="https://example.com/broken.xml",
        source_name="Broken Feed",
    )

    async def fake_fetch_feed(feed_url: str) -> str:
        raise RuntimeError("network down")

    monkeypatch.setattr(service, "_fetch_feed", fake_fetch_feed)

    processed = await service.process_feed_job(job.id)

    assert processed == 0
    refreshed_job = await db_session.get(IngestJob, job.id)
    assert refreshed_job is not None
    assert refreshed_job.status == "retrying"
    assert refreshed_job.attempt_count == 1
    assert refreshed_job.error_message == "network down"
    assert refreshed_job.next_retry_at is not None
    assert refreshed_job.next_retry_at > datetime.now(UTC)


@pytest.mark.asyncio
async def test_process_feed_job_marks_failed_after_max_attempts(
    db_session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Feed worker stops retrying after the maximum number of attempts."""
    service = IngestService(db_session)
    job = await service.queue_feed(
        feed_url="https://example.com/exhausted.xml",
        source_name="Exhausted Feed",
    )
    job.attempt_count = 2
    await db_session.commit()

    async def fake_fetch_feed(feed_url: str) -> str:
        raise RuntimeError("still down")

    monkeypatch.setattr(service, "_fetch_feed", fake_fetch_feed)

    processed = await service.process_feed_job(job.id, max_attempts=3)

    assert processed == 0
    refreshed_job = await db_session.get(IngestJob, job.id)
    assert refreshed_job is not None
    assert refreshed_job.status == "failed"
    assert refreshed_job.attempt_count == 3
    assert refreshed_job.error_message == "still down"
    assert refreshed_job.next_retry_at is None


@pytest.mark.asyncio
async def test_get_due_feed_jobs_returns_pending_and_due_retry_jobs(
    db_session: AsyncSession,
) -> None:
    """Worker scheduling can claim pending and due retry jobs only."""
    service = IngestService(db_session)
    pending = await service.queue_feed("https://example.com/pending.xml", "Pending")
    retry_due = await service.queue_feed("https://example.com/retry-due.xml", "Retry Due")
    retry_due.status = "retrying"
    retry_due.next_retry_at = datetime.now(UTC) - timedelta(seconds=1)
    retry_later = await service.queue_feed("https://example.com/retry-later.xml", "Retry Later")
    retry_later.status = "retrying"
    retry_later.next_retry_at = datetime.now(UTC) + timedelta(minutes=5)
    await db_session.commit()

    jobs = await service.get_due_feed_jobs(limit=10)

    assert [job.id for job in jobs] == [pending.id, retry_due.id]


@pytest.mark.asyncio
async def test_claim_due_feed_jobs_marks_jobs_processing(
    db_session: AsyncSession,
) -> None:
    """Worker claims move due jobs to processing so other workers skip them."""
    service = IngestService(db_session)
    pending = await service.queue_feed("https://example.com/pending.xml", "Pending")
    retry_due = await service.queue_feed("https://example.com/retry-due.xml", "Retry Due")
    retry_due.status = "retrying"
    retry_due.next_retry_at = datetime.now(UTC) - timedelta(seconds=1)
    await db_session.commit()

    claimed = await service.claim_due_feed_jobs(limit=10)

    assert [job.id for job in claimed] == [pending.id, retry_due.id]
    assert all(job.status == "processing" for job in claimed)
    assert all(job.locked_at is not None for job in claimed)
    assert await service.get_due_feed_jobs(limit=10) == []


@pytest.mark.asyncio
async def test_get_due_feed_jobs_returns_stale_processing_jobs(
    db_session: AsyncSession,
) -> None:
    """Worker scheduling can recover jobs abandoned by a crashed worker."""
    service = IngestService(db_session)
    stale = await service.queue_feed("https://example.com/stale.xml", "Stale")
    stale.status = "processing"
    stale.locked_at = datetime.now(UTC) - timedelta(minutes=20)
    active = await service.queue_feed("https://example.com/active.xml", "Active")
    active.status = "processing"
    active.locked_at = datetime.now(UTC)
    await db_session.commit()

    jobs = await service.get_due_feed_jobs(limit=10, lock_timeout_seconds=300)

    assert [job.id for job in jobs] == [stale.id]


def test_claim_due_feed_jobs_query_uses_postgresql_skip_locked() -> None:
    """PostgreSQL workers must skip rows already locked by another worker."""
    query = IngestService.build_due_feed_jobs_query(
        limit=10,
        now=datetime(2026, 5, 28, tzinfo=UTC),
        lock_timeout_seconds=300,
        for_update=True,
    )

    sql = str(
        query.compile(
            dialect=postgresql.dialect(),  # type: ignore[no-untyped-call]
            compile_kwargs={"literal_binds": True},
        )
    )

    assert "FOR UPDATE SKIP LOCKED" in sql


@pytest.mark.asyncio
async def test_process_due_feed_jobs_processes_pending_and_due_retry_jobs(
    db_session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Feed worker batch runner processes only due jobs and reports counts."""
    service = IngestService(db_session)
    pending = await service.queue_feed("https://example.com/pending.xml", "Pending")
    retry_due = await service.queue_feed("https://example.com/retry-due.xml", "Retry Due")
    retry_due.status = "retrying"
    retry_due.next_retry_at = datetime.now(UTC) - timedelta(seconds=1)
    retry_later = await service.queue_feed("https://example.com/retry-later.xml", "Retry Later")
    retry_later.status = "retrying"
    retry_later.next_retry_at = datetime.now(UTC) + timedelta(minutes=5)
    await db_session.commit()

    async def fake_fetch_feed(feed_url: str) -> str:
        return f"""
        <rss version="2.0">
          <channel>
            <title>{feed_url}</title>
            <item>
              <title>{feed_url}</title>
              <link>{feed_url}/article</link>
              <description>Body</description>
            </item>
          </channel>
        </rss>
        """

    monkeypatch.setattr(service, "_fetch_feed", fake_fetch_feed)

    result = await service.process_due_feed_jobs(limit=10)

    assert result == {
        "claimed": 2,
        "succeeded": 2,
        "failed": 0,
        "processed_items": 2,
    }
    refreshed_pending = await db_session.get(IngestJob, pending.id)
    refreshed_retry_due = await db_session.get(IngestJob, retry_due.id)
    refreshed_retry_later = await db_session.get(IngestJob, retry_later.id)
    assert refreshed_pending is not None
    assert refreshed_retry_due is not None
    assert refreshed_retry_later is not None
    assert refreshed_pending.status == "success"
    assert refreshed_pending.locked_at is None
    assert refreshed_retry_due.status == "success"
    assert refreshed_retry_due.locked_at is None
    assert refreshed_retry_later.status == "retrying"


@pytest.mark.asyncio
async def test_process_due_feed_jobs_reports_retrying_failures(
    db_session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Feed worker batch runner reports failed attempts even when they will retry."""
    service = IngestService(db_session)
    job = await service.queue_feed("https://example.com/broken.xml", "Broken")

    async def fake_fetch_feed(feed_url: str) -> str:
        raise RuntimeError("network down")

    monkeypatch.setattr(service, "_fetch_feed", fake_fetch_feed)

    result = await service.process_due_feed_jobs(limit=10)

    assert result == {
        "claimed": 1,
        "succeeded": 0,
        "failed": 1,
        "processed_items": 0,
    }
    refreshed_job = await db_session.get(IngestJob, job.id)
    assert refreshed_job is not None
    assert refreshed_job.status == "retrying"
    assert refreshed_job.attempt_count == 1
