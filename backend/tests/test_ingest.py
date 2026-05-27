"""Ingestion API tests."""

from __future__ import annotations

import hashlib
import hmac

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.article import Article
from app.models.ingest_job import IngestJob
from app.models.source import Source


@pytest.mark.asyncio
async def test_webhook_rejects_missing_signature(client: AsyncClient):
    """Webhook requests must include a signature."""
    response = await client.post(
        "/api/v1/ingest/webhook",
        json={"title": "Hello", "content": "World"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_webhook_accepts_valid_signature(client: AsyncClient):
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
