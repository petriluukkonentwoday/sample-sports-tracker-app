"""Application configuration using pydantic-settings."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "Sports Tracker API"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: Literal["development", "staging", "production"] = "development"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str = "sqlite+aiosqlite:///./sports_tracker.db"

    # Authentication
    secret_key: str = "CHANGE_THIS_IN_PRODUCTION"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # OAuth providers (optional)
    google_client_id: str = ""
    google_client_secret: str = ""

    # Firebase (for push notifications)
    firebase_credentials_path: str = ""

    # CORS
    cors_origins: list[str] = ["*"]


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
