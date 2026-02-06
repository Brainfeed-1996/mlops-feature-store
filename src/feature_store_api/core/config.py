from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FEATURE_STORE_", extra="ignore")

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/feature_store"
    redis_url: str = "redis://localhost:6379/0"
    registry_path: str = "registry/feature_views.yaml"


settings = Settings()
