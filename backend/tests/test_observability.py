"""Observability tests."""

from __future__ import annotations

import logging

import pytest
from httpx import AsyncClient


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
