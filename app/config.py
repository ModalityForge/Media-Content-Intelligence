"""Environment-backed configuration for the public MCI runtime.

Settings centralize service identity, local catalog locations, optional
integration endpoints, and feature flags. Values may be supplied by process
environment variables or an uncommitted local ``.env`` file.

Author:
    Prosenjit Banerjee <prosenjit.banerjee@gmail.com>
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    app_name: str = "media-content-intelligence-mci-v2"
    environment: str = "local"
    openai_api_key: str = ""

    vector_db_url: str = "http://localhost:6333"
    metadata_db_url: str = "sqlite:///mci.db"
    redis_url: str = "redis://localhost:6379/0"
    object_store_path: str = "./data/raw"
    social_media_store_path: str = "./data/restricted/social_media_influencer"

    enable_mock_models: bool = True
    enable_langfuse: bool = False

    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
