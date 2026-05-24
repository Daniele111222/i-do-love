"""Ingestion API tests."""

from __future__ import annotations

import hashlib
import hmac

import pytest
from httpx import AsyncClient

from app.core.config import settings


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
