"""Environment-backed configuration for the public MCI runtime.

Settings centralize service identity, local catalog locations, and public
feature flags. Values may be supplied by process environment variables or an
uncommitted local ``.env`` file.

Author:
    Prosenjit Banerjee <prosenjit.banerjee@gmail.com>
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    app_name: str = "media-content-intelligence"
    environment: str = "local"
    object_store_path: str = "./data/raw"
    social_media_store_path: str = "./data/restricted/social_media_influencer"

    enable_mock_models: bool = True
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
