from redis.asyncio import Redis

from feature_store_api.core.config import settings

_client: Redis | None = None


def client() -> Redis:
    global _client
    if _client is None:
        _client = Redis.from_url(settings.redis_url, decode_responses=True)
    return _client
