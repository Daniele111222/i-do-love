"""Create database tables for the configured backend database."""

from __future__ import annotations

import asyncio

from app.db_init import create_tables, list_tables


async def main() -> None:
    """Create all known tables and print the resulting table list."""
    await create_tables()
    tables = await list_tables()
    print("Created/verified tables:")
    for table in tables:
        print(f"- {table}")


if __name__ == "__main__":
    asyncio.run(main())
