"""Ingestion service."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from email.utils import parsedate_to_datetime
import xml.etree.ElementTree as ET

import httpx
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import worker_logger
from app.models.article import Article
from app.models.ingest_job import IngestJob
from app.models.source import Source
from app.schemas.ingest import WebhookPayload

DEFAULT_WEBHOOK_SOURCE = "OpenClaw"
ATOM_NAMESPACE = "{http://www.w3.org/2005/Atom}"
DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_RETRY_DELAY_SECONDS = 300
DEFAULT_LOCK_TIMEOUT_SECONDS = 900


@dataclass(frozen=True)
class FeedItem:
    """Parsed feed item."""

    title: str
    content: str
    source_url: str | None = None
    author: str | None = None
    published_at: datetime | None = None


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

    async def get_queue_status(
        self,
        lock_timeout_seconds: int = DEFAULT_LOCK_TIMEOUT_SECONDS,
    ) -> dict[str, int]:
        now = datetime.now(UTC)
        stale_before = now - timedelta(seconds=lock_timeout_seconds)
        result = await self.db.execute(
            select(IngestJob.status, func.count(IngestJob.id)).group_by(IngestJob.status)
        )
        counts = {status: count for status, count in result.all()}
        retry_due_result = await self.db.execute(
            select(func.count(IngestJob.id)).where(
                IngestJob.article_id.is_(None),
                IngestJob.status == "retrying",
                IngestJob.next_retry_at <= now,
            )
        )
        stale_processing_result = await self.db.execute(
            select(func.count(IngestJob.id)).where(
                IngestJob.article_id.is_(None),
                IngestJob.status == "processing",
                IngestJob.locked_at <= stale_before,
            )
        )
        retry_due = retry_due_result.scalar_one()
        stale_processing = stale_processing_result.scalar_one()
        pending = counts.get("pending", 0)
        return {
            "pending": pending,
            "retrying": counts.get("retrying", 0),
            "retry_due": retry_due,
            "processing": counts.get("processing", 0),
            "stale_processing": stale_processing,
            "failed": counts.get("failed", 0),
            "claimable": pending + retry_due + stale_processing,
        }

    async def get_due_feed_jobs(
        self,
        limit: int,
        lock_timeout_seconds: int = DEFAULT_LOCK_TIMEOUT_SECONDS,
    ) -> list[IngestJob]:
        now = datetime.now(UTC)
        result = await self.db.execute(
            self.build_due_feed_jobs_query(
                limit=limit,
                now=now,
                lock_timeout_seconds=lock_timeout_seconds,
                for_update=False,
            )
        )
        return list(result.scalars().all())

    @staticmethod
    def build_due_feed_jobs_query(
        limit: int,
        now: datetime,
        lock_timeout_seconds: int,
        for_update: bool,
    ) -> Select[tuple[IngestJob]]:
        stale_before = now - timedelta(seconds=lock_timeout_seconds)
        query = (
            select(IngestJob)
            .where(
                IngestJob.article_id.is_(None),
                (
                    (IngestJob.status == "pending")
                    | (
                        (IngestJob.status == "retrying")
                        & (IngestJob.next_retry_at <= now)
                    )
                    | (
                        (IngestJob.status == "processing")
                        & (IngestJob.locked_at <= stale_before)
                    )
                ),
            )
            .order_by(IngestJob.created_at.asc(), IngestJob.id.asc())
            .limit(limit)
        )
        if for_update:
            return query.with_for_update(skip_locked=True)
        return query

    async def claim_due_feed_jobs(
        self,
        limit: int,
        lock_timeout_seconds: int = DEFAULT_LOCK_TIMEOUT_SECONDS,
    ) -> list[IngestJob]:
        result = await self.db.execute(
            self.build_due_feed_jobs_query(
                limit=limit,
                now=datetime.now(UTC),
                lock_timeout_seconds=lock_timeout_seconds,
                for_update=self._supports_skip_locked(),
            )
        )
        jobs = list(result.scalars().all())
        now = datetime.now(UTC)
        for job in jobs:
            job.status = "processing"
            job.locked_at = now
        await self.db.commit()
        for job in jobs:
            await self.db.refresh(job)
        return jobs

    def _supports_skip_locked(self) -> bool:
        bind = self.db.get_bind()
        return bind.dialect.name == "postgresql"

    async def process_due_feed_jobs(
        self,
        limit: int,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
        retry_delay_seconds: int = DEFAULT_RETRY_DELAY_SECONDS,
        lock_timeout_seconds: int = DEFAULT_LOCK_TIMEOUT_SECONDS,
    ) -> dict[str, int]:
        jobs = await self.claim_due_feed_jobs(
            limit=limit,
            lock_timeout_seconds=lock_timeout_seconds,
        )
        result = {
            "claimed": len(jobs),
            "succeeded": 0,
            "failed": 0,
            "processed_items": 0,
        }
        for job in jobs:
            processed_items = await self.process_feed_job(
                job.id,
                max_attempts=max_attempts,
                retry_delay_seconds=retry_delay_seconds,
            )
            result["processed_items"] += processed_items
            refreshed_job = await self.db.get(IngestJob, job.id)
            if refreshed_job is not None and refreshed_job.status == "success":
                result["succeeded"] += 1
            else:
                result["failed"] += 1
        worker_logger.info(
            "feed_worker_batch_completed",
            extra={
                "claimed": result["claimed"],
                "succeeded": result["succeeded"],
                "failed": result["failed"],
                "processed_items": result["processed_items"],
            },
        )
        return result

    async def process_feed_job(
        self,
        job_id: int,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
        retry_delay_seconds: int = DEFAULT_RETRY_DELAY_SECONDS,
    ) -> int:
        job = await self.db.get(IngestJob, job_id)
        if job is None:
            raise ValueError("Ingest job was not found")
        if job.source_id is None:
            raise ValueError("Feed ingest job is missing source")

        source = await self.db.get(Source, job.source_id)
        if source is None or source.url is None:
            raise ValueError("Feed ingest job is missing source URL")

        try:
            feed_text = await self._fetch_feed(source.url)
            items = self._parse_feed(feed_text)
            for item in items:
                await self._upsert_feed_article(item=item, source=source)

            job.status = "success"
            job.error_message = None
            job.next_retry_at = None
            job.locked_at = None
            await self.db.commit()
            return len(items)
        except Exception as exc:
            job.attempt_count += 1
            if job.attempt_count >= max_attempts:
                job.status = "failed"
                job.next_retry_at = None
            else:
                job.status = "retrying"
                job.next_retry_at = datetime.now(UTC) + timedelta(seconds=retry_delay_seconds)
            job.locked_at = None
            job.error_message = str(exc)
            await self.db.commit()
            return 0

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

    async def _fetch_feed(self, feed_url: str) -> str:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(feed_url)
            response.raise_for_status()
            return response.text

    def _parse_feed(self, feed_text: str) -> list[FeedItem]:
        root = ET.fromstring(feed_text)
        if root.tag.endswith("rss"):
            return self._parse_rss(root)
        if root.tag == f"{ATOM_NAMESPACE}feed" or root.tag.endswith("feed"):
            return self._parse_atom(root)
        raise ValueError("Unsupported feed format")

    def _parse_rss(self, root: ET.Element) -> list[FeedItem]:
        items: list[FeedItem] = []
        for item in root.findall("./channel/item"):
            title = _child_text(item, "title") or "Untitled"
            content = _child_text(item, "description") or ""
            source_url = _child_text(item, "link")
            author = _child_text(item, "author")
            published_at = _parse_datetime(_child_text(item, "pubDate"))
            items.append(
                FeedItem(
                    title=title,
                    content=content,
                    source_url=source_url,
                    author=author,
                    published_at=published_at,
                )
            )
        return items

    def _parse_atom(self, root: ET.Element) -> list[FeedItem]:
        items: list[FeedItem] = []
        for entry in root.findall(f"{ATOM_NAMESPACE}entry"):
            source_url = None
            link = entry.find(f"{ATOM_NAMESPACE}link")
            if link is not None:
                source_url = link.attrib.get("href")
            author = _child_text(entry, f"{ATOM_NAMESPACE}author/{ATOM_NAMESPACE}name")
            items.append(
                FeedItem(
                    title=_child_text(entry, f"{ATOM_NAMESPACE}title") or "Untitled",
                    content=(
                        _child_text(entry, f"{ATOM_NAMESPACE}summary")
                        or _child_text(entry, f"{ATOM_NAMESPACE}content")
                        or ""
                    ),
                    source_url=source_url,
                    author=author,
                    published_at=_parse_datetime(
                        _child_text(entry, f"{ATOM_NAMESPACE}updated")
                        or _child_text(entry, f"{ATOM_NAMESPACE}published")
                    ),
                )
            )
        return items

    async def _upsert_feed_article(self, item: FeedItem, source: Source) -> Article:
        article: Article | None = None
        if item.source_url is not None:
            result = await self.db.execute(
                select(Article).where(Article.source_url == item.source_url)
            )
            article = result.scalar_one_or_none()

        if article is None:
            article = Article(
                source_id=source.id,
                title=item.title,
                content=item.content,
                source_url=item.source_url,
                author=item.author,
                published_at=item.published_at,
                tags=[],
            )
            self.db.add(article)
            await self.db.flush()
            return article

        article.source_id = source.id
        article.title = item.title
        article.content = item.content
        article.author = item.author
        article.published_at = item.published_at
        await self.db.flush()
        return article


def _child_text(element: ET.Element, path: str) -> str | None:
    child = element.find(path)
    if child is None or child.text is None:
        return None
    value = child.text.strip()
    return value or None


def _parse_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return parsedate_to_datetime(value)
