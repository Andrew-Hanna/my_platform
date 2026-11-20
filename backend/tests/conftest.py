"""Shared pytest setup.

The `app` package lives in backend/app (no src/ folder), so we add the
backend folder to sys.path. This lets `from app.main import app` work
no matter where pytest is started from.

App code is imported inside fixtures and tests, not at the top of this file.
That way a missing module shows up as failing tests, and the rest still run.
"""

import os
import sys
import uuid
from datetime import timedelta
from itertools import count
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parents[1]

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from tests.helpers import DEFAULT_PASSWORD, utc_now

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://lms:change-me@localhost:5432/lms_test",
)

# The app reads DATABASE_URL from its settings, so point it at the test database.
os.environ["DATABASE_URL"] = TEST_DATABASE_URL


@pytest.fixture
def db_schema():
    """Create every table before a test and drop them all after it. Yields the engine."""
    from app import models  # noqa: F401  (importing this registers the tables on Base)
    from app.db import Base, make_engine

    engine = make_engine(TEST_DATABASE_URL)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def db_session(db_schema):
    """A database session for arranging test data and checking rows."""
    from sqlalchemy.orm import Session

    session = Session(db_schema)
    yield session
    session.close()


@pytest.fixture
def email_sender():
    """A fresh console email sender for one test. Its .outbox lists every email sent."""
    from app.adapters.email import ConsoleEmailSender

    return ConsoleEmailSender()


@pytest.fixture
def make_client(db_schema, email_sender):
    """Factory that returns a new TestClient. Each client has its own cookie jar."""
    from fastapi.testclient import TestClient

    from app.adapters.email import get_email_sender
    from app.main import app

    app.dependency_overrides[get_email_sender] = lambda: email_sender
    created = []

    def _make_client():
        test_client = TestClient(app)
        created.append(test_client)
        return test_client

    yield _make_client
    app.dependency_overrides.clear()
    for test_client in created:
        test_client.close()


@pytest.fixture
def client(make_client):
    """A TestClient with its own cookie jar."""
    return make_client()


@pytest.fixture
def make_user(db_session):
    """Insert a User row directly. Pass password=None for a user with no password yet."""
    from app.models import User
    from app.security import hash_password

    counter = count(1)

    def _make_user(
        role="student",
        status="active",
        password=DEFAULT_PASSWORD,
        email=None,
        name="Test Person",
    ):
        number = next(counter)
        user = User(
            name=name,
            email=email or f"person{number}@example.com",
            role=role,
            status=status,
            password_hash=hash_password(password) if password else None,
            created_at=utc_now(),
        )
        db_session.add(user)
        db_session.commit()
        return user

    return _make_user


@pytest.fixture
def make_invite(db_session):
    """Insert an Invite row with a token we know. The factory returns the raw token."""
    from app.models import Invite
    from app.security import hash_token

    def _make_invite(user, expires_at=None, used_at=None, revoked_at=None):
        raw_token = f"invite-{uuid.uuid4().hex}"
        db_session.add(
            Invite(
                user_id=user.id,
                token_hash=hash_token(raw_token),
                created_at=utc_now(),
                expires_at=expires_at or utc_now() + timedelta(days=3),
                used_at=used_at,
                revoked_at=revoked_at,
            )
        )
        db_session.commit()
        return raw_token

    return _make_invite
