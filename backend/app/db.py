"""Database setup: the declarative base and engine factory. No connection is made at import time."""

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Parent class for all database models."""


def make_engine(database_url: str) -> Engine:
    """Create a database engine for the given URL."""
    return create_engine(database_url, pool_pre_ping=True)
