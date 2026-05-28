"""Feed worker script tests."""

from __future__ import annotations

import pytest

from scripts import run_feed_worker


@pytest.mark.asyncio
async def test_run_once_processes_due_feed_jobs(monkeypatch: pytest.MonkeyPatch) -> None:
    """Worker script delegates one batch to the ingestion service."""

    class FakeSession:
        async def __aenter__(self) -> FakeSession:
            return self

        async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
            return None

    class FakeSessionFactory:
        def __call__(self) -> FakeSession:
            return FakeSession()

    class FakeIngestService:
        def __init__(self, db: FakeSession):
            self.db = db

        async def process_due_feed_jobs(self, limit: int) -> dict[str, int]:
            assert limit == 5
            return {
                "claimed": 1,
                "succeeded": 1,
                "failed": 0,
                "processed_items": 2,
            }

    monkeypatch.setattr(run_feed_worker, "AsyncSessionLocal", FakeSessionFactory())
    monkeypatch.setattr(run_feed_worker, "IngestService", FakeIngestService)

    assert await run_feed_worker.run_once(limit=5) == {
        "claimed": 1,
        "succeeded": 1,
        "failed": 0,
        "processed_items": 2,
    }
