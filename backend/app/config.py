"""Application settings, read from environment variables or a local .env file."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# The .env file lives at the repository root, one level above backend/.
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    """All configuration the backend needs. Secrets come from the environment, never from code."""

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    database_url: str
    app_env: str = "dev"


def get_settings() -> Settings:
    """Return the settings for this process."""
    return Settings()
