"""Content ingestion API routes."""

from __future__ import annotations

import hashlib
import hmac

from fastapi import APIRouter, Header, HTTPException, Request, status
from pydantic import BaseModel, Field

from app.core.config import settings

router = APIRouter()


def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify an HMAC-SHA256 webhook signature."""
    expected = hmac.new(
        key=secret.encode(),
        msg=payload,
        digestmod=hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)


class WebhookPayload(BaseModel):
    """OpenClaw webhook payload."""

    title: str = Field(..., min_length=1, max_length=500)
    content: str
    source_url: str | None = None
    source_name: str | None = None
    author: str | None = None
    published_at: str | None = None
    tags: list[str] = Field(default_factory=list)


class WebhookResponse(BaseModel):
    """Webhook acknowledgement response."""

    status: str
    id: int | None = None
    message: str


class IngestStatusResponse(BaseModel):
    """Ingestion status response."""

    total_processed: int
    total_success: int
    total_failed: int


@router.post(
    "/webhook",
    response_model=WebhookResponse,
    status_code=status.HTTP_200_OK,
)
async def receive_webhook(
    request: Request,
    payload: WebhookPayload,
    x_signature: str | None = Header(None, alias="X-Signature"),
) -> WebhookResponse:
    """Receive content from OpenClaw."""
    if not x_signature:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Signature header",
        )

    payload_bytes = await request.body()
    if not verify_webhook_signature(payload_bytes, x_signature, settings.WEBHOOK_SECRET):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature",
        )

    return WebhookResponse(
        status="accepted",
        id=None,
        message="Content accepted for processing",
    )


@router.post(
    "/feed",
    status_code=status.HTTP_202_ACCEPTED,
)
async def ingest_feed(
    feed_url: str,
    source_name: str | None = None,
) -> dict[str, str | None]:
    """Queue an RSS, Atom, or JSON feed for ingestion."""
    return {
        "status": "queued",
        "message": "Feed ingestion has been queued",
        "feed_url": feed_url,
        "source_name": source_name,
    }


@router.get(
    "/status",
    response_model=IngestStatusResponse,
    status_code=status.HTTP_200_OK,
)
async def get_ingest_status() -> IngestStatusResponse:
    """Return content ingestion status and statistics."""
    return IngestStatusResponse(
        total_processed=0,
        total_success=0,
        total_failed=0,
    )
