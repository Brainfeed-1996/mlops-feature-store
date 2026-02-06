from __future__ import annotations

from feature_store_api.feature_store.models import FeatureView
from feature_store_api.feature_store.offline import latest_rows_by_entity
from feature_store_api.feature_store.online import OnlineStore


async def materialize_feature_view(fv: FeatureView, limit: int = 1000) -> int:
    rows = await latest_rows_by_entity(fv, limit=limit)
    online = OnlineStore.instance()
    entity_col = fv.offline.entity_column
    ts_col = fv.offline.timestamp_column

    n = 0
    for r in rows:
        entity_id = str(r[entity_col])
        payload = {k: v for k, v in r.items() if k not in (entity_col, ts_col)}
        await online.write_entity_features(fv, entity_id, payload)
        n += 1
    return n
