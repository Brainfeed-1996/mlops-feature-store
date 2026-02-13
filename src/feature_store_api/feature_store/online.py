from __future__ import annotations

from dataclasses import dataclass, field

from feature_store_api.core.config import settings
from feature_store_api.core.redis_client import client
from feature_store_api.feature_store.models import FeatureView


class OnlineStore:
    """Online store facade.

    Defaults to Redis when configured, but can fall back to in-memory storage.
    """

    _instance: "OnlineStore | None" = None

    @classmethod
    def instance(cls) -> "OnlineStore":
        if cls._instance is None:
            backend = (settings.online_backend or "redis").lower()
            if backend == "memory" or not settings.redis_url:
                cls._instance = MemoryOnlineStore()
            else:
                cls._instance = RedisOnlineStore()
        return cls._instance

    def _key(self, fv: FeatureView, entity_id: str) -> str:
        return f"fv:{fv.name}:entity:{entity_id}"

    async def write_entity_features(self, fv: FeatureView, entity_id: str, features: dict) -> None:  # pragma: no cover
        raise NotImplementedError

    async def get_entity_features(self, fv: FeatureView, entity_id: str) -> dict | None:  # pragma: no cover
        raise NotImplementedError


class RedisOnlineStore(OnlineStore):
    async def write_entity_features(self, fv: FeatureView, entity_id: str, features: dict) -> None:
        key = self._key(fv, entity_id)
        await client().hset(key, mapping={k: str(v) for k, v in features.items() if v is not None})

    async def get_entity_features(self, fv: FeatureView, entity_id: str) -> dict | None:
        key = self._key(fv, entity_id)
        data = await client().hgetall(key)
        return data or None


@dataclass
class MemoryOnlineStore(OnlineStore):
    _store: dict[str, dict[str, str]] = field(default_factory=dict)

    async def write_entity_features(self, fv: FeatureView, entity_id: str, features: dict) -> None:
        key = self._key(fv, entity_id)
        self._store[key] = {k: str(v) for k, v in features.items() if v is not None}

    async def get_entity_features(self, fv: FeatureView, entity_id: str) -> dict | None:
        key = self._key(fv, entity_id)
        return self._store.get(key)
