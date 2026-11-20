"""Tests for the database models in app/models.py."""

from datetime import timedelta

import pytest

from tests.helpers import (
    csrf_headers,
    invite_token_from_outbox,
    login,
    post_with_csrf,
    utc_now,
)


def test_user_row_stores_role_and_status(db_session):
    """A1.1: a User row keeps its name, email, role and status."""
    from app.models import User

    db_session.add(
        User(
            name="Ada",
            email="ada@example.com",
            role="instructor",
            status="active",
            created_at=utc_now(),
        )
    )
    db_session.commit()

    saved = db_session.query(User).filter_by(email="ada@example.com").one()

    assert saved.name == "Ada"
    assert saved.role == "instructor"
    assert saved.status == "active"
    assert saved.password_hash is None


def test_duplicate_user_email_is_rejected(db_session):
    """A1.1: two users cannot share the same email address."""
    from sqlalchemy.exc import IntegrityError

    from app.models import User

    for name in ("First", "Second"):
        db_session.add(
            User(
                name=name,
                email="same@example.com",
                role="student",
                status="active",
                created_at=utc_now(),
            )
        )

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_session_token_hash_is_unique(db_session, make_user):
    """A1.5: two login sessions cannot share the same token hash."""
    from sqlalchemy.exc import IntegrityError

    from app.models import Session as LoginSession

    user = make_user()
    for _ in range(2):
        db_session.add(
            LoginSession(
                user_id=user.id,
                token_hash="same-hash",
                created_at=utc_now(),
                expires_at=utc_now() + timedelta(days=30),
            )
        )

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_invite_row_stores_hash_never_the_raw_token(
    client, make_user, db_session, email_sender
):
    """A1.9: the invites table keeps token_hash and never the raw token."""
    from app.models import Invite
    from app.security import hash_token

    teacher = make_user(role="instructor", email="teacher@example.com")
    login(client, teacher.email)
    post_with_csrf(
        client, "/users/invite", json={"name": "Sam", "email": "sam@example.com"}
    )

    raw_token = invite_token_from_outbox(email_sender)
    db_session.expire_all()
    invites = db_session.query(Invite).all()

    assert len(invites) == 1
    assert invites[0].token_hash == hash_token(raw_token)
    for column in Invite.__table__.columns:
        stored_value = str(getattr(invites[0], column.name))
        assert raw_token not in stored_value, f"raw token found in column {column.name}"


def test_csrf_header_helper_is_available(client):
    """A1.17a: GET /auth/csrf returns a token that the CSRF helper can send back."""
    headers = csrf_headers(client)

    assert "X-CSRF-Token" in headers
    assert headers["X-CSRF-Token"]
