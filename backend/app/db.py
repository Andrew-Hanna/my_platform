"""Database setup: the declarative base, engine, and session factory. No connection is made at import time."""

from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import cached_settings


class Base(DeclarativeBase):
    """Parent class for all database models."""


def make_engine(database_url: str) -> Engine:
    """Create a database engine for the given URL."""
    return create_engine(database_url, pool_pre_ping=True)


@lru_cache
def get_engine() -> Engine:
    """The application's engine, built from DATABASE_URL on first use."""
    return make_engine(cached_settings().database_url)


@lru_cache
def get_session_factory() -> sessionmaker:
    """Factory for database sessions used by request handlers and the CLI."""
    return sessionmaker(bind=get_engine(), expire_on_commit=False)
