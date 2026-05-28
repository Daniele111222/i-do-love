"""Observability tests."""

from __future__ import annotations

import logging

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.ingest_service import IngestService


@pytest.mark.asyncio
async def test_request_log_contains_request_id(
    client: AsyncClient,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO, logger="app.request")

    response = await client.get("/api/v1/health", headers={"X-Request-ID": "req-log-test"})

    assert response.status_code == 200
    assert any(
        record.name == "app.request"
        and record.message == "request_completed"
        and getattr(record, "request_id", None) == "req-log-test"
        and getattr(record, "method", None) == "GET"
        and getattr(record, "path", None) == "/api/v1/health"
        and getattr(record, "status_code", None) == 200
        for record in caplog.records
    )


@pytest.mark.asyncio
async def test_feed_worker_batch_log_contains_batch_counts(
    db_session: AsyncSession,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO, logger="app.worker")
    service = IngestService(db_session)

    await service.process_due_feed_jobs(limit=10)

    assert any(
        record.name == "app.worker"
        and record.message == "feed_worker_batch_completed"
        and getattr(record, "claimed", None) == 0
        and getattr(record, "succeeded", None) == 0
        and getattr(record, "failed", None) == 0
        and getattr(record, "processed_items", None) == 0
        for record in caplog.records
    )


@pytest.mark.asyncio
async def test_feed_worker_batch_log_counts_failed_attempts(
    db_session: AsyncSession,
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    caplog.set_level(logging.INFO, logger="app.worker")
    service = IngestService(db_session)
    await service.queue_feed("https://example.com/broken.xml", "Broken")

    async def fake_fetch_feed(feed_url: str) -> str:
        raise RuntimeError("network down")

    monkeypatch.setattr(service, "_fetch_feed", fake_fetch_feed)

    await service.process_due_feed_jobs(limit=10)

    assert any(
        record.name == "app.worker"
        and record.message == "feed_worker_batch_completed"
        and getattr(record, "claimed", None) == 1
        and getattr(record, "succeeded", None) == 0
        and getattr(record, "failed", None) == 1
        and getattr(record, "processed_items", None) == 0
        for record in caplog.records
    )
