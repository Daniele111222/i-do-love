"""Ingestion schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class WebhookPayload(BaseModel):
    """OpenClaw webhook payload."""

    title: str = Field(..., min_length=1, max_length=500)
    content: str
    source_url: str | None = None
    source_name: str | None = None
    author: str | None = None
    published_at: datetime | None = None
    tags: list[str] = Field(default_factory=list)


class WebhookResponse(BaseModel):
    """Webhook acknowledgement response."""

    status: str
    id: int | None = None
    message: str


class FeedIngestResponse(BaseModel):
    """Feed ingestion queue response."""

    status: str
    message: str
    feed_url: str
    source_name: str | None = None
    source_id: int
    job_id: int


class IngestStatusResponse(BaseModel):
    """Ingestion status response."""

    total_processed: int
    total_success: int
    total_failed: int
