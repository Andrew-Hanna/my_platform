"""Tests for the create-admin function in app/cli.py (A1.3). The getpass prompt is not tested."""

import pytest
from sqlalchemy.orm import Session


def test_create_admin_user_makes_an_active_admin(db_session, db_schema):
    """A1.3: create_admin_user saves an admin account with status active."""
    from app.cli import create_admin_user
    from app.models import User

    create_admin_user(
        db_session, email="boss@example.com", name="Boss", password="admin-pass-123"
    )

    with Session(db_schema) as fresh_session:
        saved = fresh_session.query(User).filter_by(email="boss@example.com").one()
        assert saved.name == "Boss"
        assert saved.role == "admin"
        assert saved.status == "active"


def test_create_admin_user_stores_a_hash_not_the_password(db_session):
    """A1.3: the admin password is stored as a hash that verifies with the same password."""
    from app.cli import create_admin_user
    from app.security import verify_password

    user = create_admin_user(
        db_session, email="boss@example.com", name="Boss", password="admin-pass-123"
    )

    assert user.password_hash != "admin-pass-123"
    assert verify_password("admin-pass-123", user.password_hash) is True


def test_create_admin_user_rejects_duplicate_email(db_session):
    """A1.3: a second admin with the same email raises ValueError."""
    from app.cli import create_admin_user

    create_admin_user(
        db_session, email="boss@example.com", name="Boss", password="admin-pass-123"
    )

    with pytest.raises(ValueError):
        create_admin_user(
            db_session,
            email="boss@example.com",
            name="Other",
            password="another-pass-1",
        )
