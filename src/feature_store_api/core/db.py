from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from feature_store_api.core.config import settings

_engine: AsyncEngine | None = None


def engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        _engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    return _engine
