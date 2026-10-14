from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, loaded from environment variables and an optional .env file."""

    model_config = SettingsConfigDict(
        env_prefix="NIYAM_",
        env_file=".env",
        extra="ignore",
    )

    app_name: str = "niyam"
    environment: Literal["local", "test", "production"] = "local"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    llm_provider: str = "google_genai"
    llm_model: str | None = None
    embedding_provider: str = "google_genai"
    embedding_model: str | None = None
    google_api_key: SecretStr | None = None
