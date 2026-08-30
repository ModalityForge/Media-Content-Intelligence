"""Application configuration using pydantic-settings."""

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

    enable_mock_models: bool = True
    enable_langfuse: bool = False

    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()