from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import text

from feature_store_api.core.db import engine
from feature_store_api.feature_store.models import FeatureView


def _parse_ts(v: Any) -> Any:
    if isinstance(v, datetime):
        return v
    if isinstance(v, str):
        # accept ISO-8601
        return datetime.fromisoformat(v.replace("Z", "+00:00"))
    return v


async def ingest_rows(feature_view: FeatureView, rows: list[dict[str, Any]]) -> int:
    """Insert rows into the offline store table for a feature view.

    Expects dicts containing:
      - entity column
      - timestamp column
      - each feature column

    This intentionally uses raw SQL for clarity in a minimal reference project.
    """

    entity_col = feature_view.offline.entity_column
    ts_col = feature_view.offline.timestamp_column
    feature_cols = [f.name for f in feature_view.features]

    expected = [entity_col, ts_col] + feature_cols

    cols_sql = ", ".join(expected)
    values_sql = ", ".join([f":{c}" for c in expected])

    sql = text(
        f"""
        INSERT INTO {feature_view.offline.table} ({cols_sql})
        VALUES ({values_sql})
        """
    )

    n = 0
    async with engine().begin() as conn:
        for r in rows:
            payload = {c: r.get(c) for c in expected}
            payload[ts_col] = _parse_ts(payload[ts_col])
            await conn.execute(sql, payload)
            n += 1
    return n
