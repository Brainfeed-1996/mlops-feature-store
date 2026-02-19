from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import text

from feature_store_api.core.db import engine
from feature_store_api.feature_store.models import FeatureView


async def latest_rows_by_entity(feature_view: FeatureView, limit: int = 1000) -> Sequence[dict]:
    """Fetch latest row per entity from offline store.

    Simplified "latest per entity" query.

    - Postgres: uses DISTINCT ON
    - SQLite: uses ROW_NUMBER() window function

    (Not full point-in-time correctness; good enough for a minimal feature store demo.)
    """

    cols = [feature_view.offline.entity_column, feature_view.offline.timestamp_column] + [
        f.name for f in feature_view.features
    ]
    cols_sql = ", ".join(cols)

    dialect = engine().dialect.name
    if dialect == "postgresql":
        sql = f"""
        SELECT DISTINCT ON ({feature_view.offline.entity_column}) {cols_sql}
        FROM {feature_view.offline.table}
        ORDER BY {feature_view.offline.entity_column}, {feature_view.offline.timestamp_column} DESC
        LIMIT :limit
        """
    else:
        # SQLite (and many others) can do this with a window function.
        sql = f"""
        SELECT {cols_sql}
        FROM (
          SELECT {cols_sql},
                 ROW_NUMBER() OVER (
                   PARTITION BY {feature_view.offline.entity_column}
                   ORDER BY {feature_view.offline.timestamp_column} DESC
                 ) AS rn
          FROM {feature_view.offline.table}
        ) t
        WHERE rn = 1
        LIMIT :limit
        """

    async with engine().connect() as conn:
        res = await conn.execute(text(sql), {"limit": limit})
        rows = [dict(r._mapping) for r in res.fetchall()]
    return rows
