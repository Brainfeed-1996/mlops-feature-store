"""Tiny demo: insert a few rows into Postgres offline store.

Run with:
  pip install -e .
  python scripts/demo_ingest.py

Requires docker-compose Postgres running on localhost:5432.
"""

import asyncio
from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


from feature_store_api.core.config import settings

DB_URL = settings.database_url


async def main() -> None:
    engine = create_async_engine(DB_URL, echo=False)
    async with engine.begin() as conn:
        now = datetime.now(timezone.utc)
        rows = [
            (123, now, "FR", 28, 3.0),
            (456, now, "DE", 41, 0.0),
        ]
        for r in rows:
            await conn.execute(
                text(
                    """
                    INSERT INTO user_features (user_id, event_ts, country, age, purchases_7d)
                    VALUES (:user_id, :event_ts, :country, :age, :purchases_7d)
                    """
                ),
                {
                    "user_id": r[0],
                    "event_ts": r[1],
                    "country": r[2],
                    "age": r[3],
                    "purchases_7d": r[4],
                },
            )

    await engine.dispose()
    print("Inserted demo rows into offline store.")


if __name__ == "__main__":
    asyncio.run(main())
