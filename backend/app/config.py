"""Application settings, read from environment variables or a local .env file."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# The .env file lives at the repository root, one level above backend/.
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    """All configuration the backend needs. Secrets come from the environment, never from code."""

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    database_url: str
    app_env: str = "dev"
    # Where the frontend lives; invite and reset links are built from this.
    app_base_url: str = "http://localhost:5173"
    # Turn on in production so the session cookie is sent over HTTPS only.
    session_cookie_secure: bool = False


def get_settings() -> Settings:
    """Return the settings for this process."""
    return Settings()


@lru_cache
def cached_settings() -> Settings:
    """Settings read once per process, for code that runs on every request."""
    return get_settings()
