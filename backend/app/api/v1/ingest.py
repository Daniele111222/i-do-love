"""Content ingestion API routes."""

from __future__ import annotations

import hashlib
import hmac

from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.database import get_db
from app.schemas.ingest import (
    FeedIngestResponse,
    IngestQueueStatusResponse,
    IngestStatusResponse,
    WebhookPayload,
    WebhookResponse,
)
from app.services.ingest_service import IngestService

router = APIRouter()


def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify an HMAC-SHA256 webhook signature."""
    expected = hmac.new(
        key=secret.encode(),
        msg=payload,
        digestmod=hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)


@router.post(
    "/webhook",
    response_model=WebhookResponse,
    status_code=status.HTTP_200_OK,
)
async def receive_webhook(
    request: Request,
    payload: WebhookPayload,
    db: Annotated[AsyncSession, Depends(get_db)],
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

    article = await IngestService(db).ingest_webhook(payload)
    return WebhookResponse(
        status="accepted",
        id=article.id,
        message="Content accepted for processing",
    )


@router.post(
    "/feed",
    response_model=FeedIngestResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def ingest_feed(
    feed_url: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    source_name: str | None = None,
) -> FeedIngestResponse:
    """Queue an RSS, Atom, or JSON feed for ingestion."""
    job = await IngestService(db).queue_feed(feed_url=feed_url, source_name=source_name)
    if job.source_id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Feed ingestion job is missing source",
        )
    return FeedIngestResponse(
        status="queued",
        message="Feed ingestion has been queued",
        feed_url=feed_url,
        source_name=source_name,
        source_id=job.source_id,
        job_id=job.id,
    )


@router.get(
    "/status",
    response_model=IngestStatusResponse,
    status_code=status.HTTP_200_OK,
)
async def get_ingest_status(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> IngestStatusResponse:
    """Return content ingestion status and statistics."""
    return IngestStatusResponse(**await IngestService(db).get_status())


@router.get(
    "/queue",
    response_model=IngestQueueStatusResponse,
    status_code=status.HTTP_200_OK,
)
async def get_ingest_queue_status(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> IngestQueueStatusResponse:
    """Return feed worker queue status and backlog statistics."""
    return IngestQueueStatusResponse(**await IngestService(db).get_queue_status())
