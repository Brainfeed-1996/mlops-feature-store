from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text


@pytest.fixture()
async def _setup_sqlite_schema():
    from feature_store_api.core.db import engine

    async with engine().begin() as conn:
        await conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS user_features (
                  user_id INTEGER NOT NULL,
                  event_ts TEXT NOT NULL,
                  country TEXT,
                  age INTEGER,
                  purchases_7d REAL,
                  PRIMARY KEY (user_id, event_ts)
                );
                """
            )
        )

        await conn.execute(
            text(
                """
                INSERT INTO user_features (user_id, event_ts, country, age, purchases_7d)
                VALUES (:user_id, :event_ts, :country, :age, :purchases_7d)
                """
            ),
            {
                "user_id": 123,
                "event_ts": datetime(2026, 1, 1, tzinfo=timezone.utc).isoformat(),
                "country": "FR",
                "age": 28,
                "purchases_7d": 1.0,
            },
        )
        await conn.execute(
            text(
                """
                INSERT INTO user_features (user_id, event_ts, country, age, purchases_7d)
                VALUES (:user_id, :event_ts, :country, :age, :purchases_7d)
                """
            ),
            {
                "user_id": 123,
                "event_ts": datetime(2026, 2, 1, tzinfo=timezone.utc).isoformat(),
                "country": "FR",
                "age": 29,
                "purchases_7d": 3.0,
            },
        )
        await conn.execute(
            text(
                """
                INSERT INTO user_features (user_id, event_ts, country, age, purchases_7d)
                VALUES (:user_id, :event_ts, :country, :age, :purchases_7d)
                """
            ),
            {
                "user_id": 456,
                "event_ts": datetime(2026, 2, 1, tzinfo=timezone.utc).isoformat(),
                "country": "DE",
                "age": 41,
                "purchases_7d": 0.0,
            },
        )

    yield


def test_materialize_and_get_online(_setup_sqlite_schema):
    from feature_store_api.main import app

    c = TestClient(app)

    r = c.post("/materialize/user_features")
    assert r.status_code == 200
    assert r.json()["rows"] == 2

    r2 = c.get("/online/user_features/123")
    assert r2.status_code == 200
    feats = r2.json()["features"]
    assert feats["age"] == "29"
    assert feats["country"] == "FR"
    assert feats["purchases_7d"] == "3.0"
