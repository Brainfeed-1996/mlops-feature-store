from __future__ import annotations

from feature_store_api.core.redis_client import client
from feature_store_api.feature_store.models import FeatureView


class OnlineStore:
    _instance: "OnlineStore | None" = None

    @classmethod
    def instance(cls) -> "OnlineStore":
        if cls._instance is None:
            cls._instance = OnlineStore()
        return cls._instance

    def _key(self, fv: FeatureView, entity_id: str) -> str:
        return f"fv:{fv.name}:entity:{entity_id}"

    async def write_entity_features(self, fv: FeatureView, entity_id: str, features: dict) -> None:
        key = self._key(fv, entity_id)
        await client().hset(key, mapping={k: str(v) for k, v in features.items() if v is not None})

    async def get_entity_features(self, fv: FeatureView, entity_id: str) -> dict | None:
        key = self._key(fv, entity_id)
        data = await client().hgetall(key)
        return data or None
