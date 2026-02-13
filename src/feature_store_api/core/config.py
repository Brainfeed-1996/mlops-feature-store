from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FEATURE_STORE_", extra="ignore")

    # Offline store (SQLite or Postgres)
    database_url: str = "sqlite+aiosqlite:///./feature_store.db"

    # Online store: set to empty string to disable Redis and use in-memory store.
    redis_url: str = "redis://localhost:6379/0"
    online_backend: str = "redis"  # redis|memory

    registry_path: str = "registry/feature_views.yaml"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
