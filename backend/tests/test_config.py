"""Task S0.5: the Settings class reads DATABASE_URL from environment variables."""

import pytest
from pydantic import ValidationError

from app.config import Settings


def test_database_url_comes_from_environment(monkeypatch):
    """Task S0.5: DATABASE_URL set in the environment is loaded into Settings."""
    fake_url = "postgresql://user:pass@db.example.test:5432/testdb"
    monkeypatch.setenv("DATABASE_URL", fake_url)

    settings = Settings()

    assert settings.database_url == fake_url


def test_missing_database_url_raises_error(monkeypatch):
    """Task S0.5: with no DATABASE_URL and no .env file, Settings must fail.

    This proves there is no default database URL containing credentials.
    """
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)
