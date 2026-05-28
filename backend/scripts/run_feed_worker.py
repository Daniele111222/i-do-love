"""Run one feed ingestion worker batch."""

from __future__ import annotations

import argparse
import asyncio

from app.database import AsyncSessionLocal
from app.services.ingest_service import IngestService


async def run_once(limit: int) -> dict[str, int]:
    """Process one batch of due feed jobs."""
    async with AsyncSessionLocal() as db:
        return await IngestService(db).process_due_feed_jobs(limit=limit)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Process one batch of due feed ingest jobs.")
    parser.add_argument("--limit", type=int, default=10, help="Maximum jobs to process in one batch.")
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    result = await run_once(limit=args.limit)
    print(
        "Feed worker batch: "
        f"claimed={result['claimed']} "
        f"succeeded={result['succeeded']} "
        f"failed={result['failed']} "
        f"processed_items={result['processed_items']}"
    )


if __name__ == "__main__":
    asyncio.run(main())
