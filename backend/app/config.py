"""Application configuration using pydantic-settings."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All application settings are loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    # ── Application ────────────────────────────────────────────────────────
    app_env: str = "development"
    debug: bool = False

    # ── Security ───────────────────────────────────────────────────────────
    secret_key: str = "change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # ── PostgreSQL ─────────────────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://vulnuser:vulnpassword@postgres:5432/vulndb"

    # ── Redis ──────────────────────────────────────────────────────────────
    redis_url: str = "redis://redis:6379/0"

    # ── Elasticsearch ──────────────────────────────────────────────────────
    elasticsearch_url: str = "http://elasticsearch:9200"
    elasticsearch_index_vulnerabilities: str = "vulnerabilities"

    # ── Celery ─────────────────────────────────────────────────────────────
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/1"

    # ── External APIs ──────────────────────────────────────────────────────
    nvd_api_key: Optional[str] = None
    github_token: Optional[str] = None


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
