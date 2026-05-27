"""Ingestion service."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article
from app.models.ingest_job import IngestJob
from app.models.source import Source
from app.schemas.ingest import WebhookPayload

DEFAULT_WEBHOOK_SOURCE = "OpenClaw"


class IngestService:
    """Business logic for content ingestion."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def ingest_webhook(self, payload: WebhookPayload) -> Article:
        source = await self._get_or_create_source(payload)
        article = await self._upsert_article(payload=payload, source=source)

        self.db.add(
            IngestJob(
                source_id=source.id,
                article_id=article.id,
                status="success",
            )
        )
        await self.db.commit()
        await self.db.refresh(article)
        return article

    async def queue_feed(self, feed_url: str, source_name: str | None = None) -> IngestJob:
        source = await self._get_or_create_feed_source(feed_url=feed_url, source_name=source_name)
        job = IngestJob(source_id=source.id, article_id=None, status="pending")
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def get_status(self) -> dict[str, int]:
        result = await self.db.execute(
            select(IngestJob.status, func.count(IngestJob.id)).group_by(IngestJob.status)
        )
        counts = {status: count for status, count in result.all()}
        return {
            "total_processed": sum(counts.values()),
            "total_success": counts.get("success", 0),
            "total_failed": counts.get("failed", 0),
        }

    async def _get_or_create_source(self, payload: WebhookPayload) -> Source:
        name = payload.source_name or DEFAULT_WEBHOOK_SOURCE
        result = await self.db.execute(select(Source).where(Source.name == name))
        source = result.scalar_one_or_none()
        if source is not None:
            return source

        source = Source(name=name, url=payload.source_url)
        self.db.add(source)
        await self.db.flush()
        return source

    async def _get_or_create_feed_source(
        self,
        feed_url: str,
        source_name: str | None = None,
    ) -> Source:
        result = await self.db.execute(select(Source).where(Source.url == feed_url))
        source = result.scalar_one_or_none()
        if source is not None:
            return source

        source = Source(name=source_name or feed_url, url=feed_url)
        self.db.add(source)
        await self.db.flush()
        return source

    async def _upsert_article(self, payload: WebhookPayload, source: Source) -> Article:
        article: Article | None = None
        if payload.source_url is not None:
            result = await self.db.execute(
                select(Article).where(Article.source_url == payload.source_url)
            )
            article = result.scalar_one_or_none()

        if article is None:
            article = Article(
                source_id=source.id,
                title=payload.title,
                content=payload.content,
                source_url=payload.source_url,
                author=payload.author,
                published_at=payload.published_at,
                tags=payload.tags,
            )
            self.db.add(article)
            await self.db.flush()
            return article

        article.source_id = source.id
        article.title = payload.title
        article.content = payload.content
        article.author = payload.author
        article.published_at = payload.published_at
        article.tags = payload.tags
        await self.db.flush()
        return article
