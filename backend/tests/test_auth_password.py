"""Tests for forgot-password, reset-password, and change-password (A1.13, A1.17, A1.17b)."""

from datetime import timedelta

from tests.helpers import (
    DEFAULT_PASSWORD,
    NEW_PASSWORD,
    login,
    post_with_csrf,
    reset_token_from_outbox,
    utc_now,
)

RESET_ERROR = "This reset link is not valid. Request a new one."


def test_forgot_response_is_the_same_for_known_and_unknown_email(client, make_user):
    """A1.13: forgot-password returns 202 with the same body whether or not the email exists."""
    make_user(email="known@example.com")

    known = post_with_csrf(
        client, "/auth/password/forgot", json={"email": "known@example.com"}
    )
    unknown = post_with_csrf(
        client, "/auth/password/forgot", json={"email": "nobody@example.com"}
    )

    assert known.status_code == 202
    assert unknown.status_code == 202
    assert known.json() == unknown.json()


def test_forgot_emails_a_link_only_for_a_known_user(client, make_user, email_sender):
    """A1.13: a reset email goes out for a known address and none for an unknown one."""
    make_user(email="known@example.com")

    post_with_csrf(
        client, "/auth/password/forgot", json={"email": "nobody@example.com"}
    )
    assert email_sender.outbox == []

    post_with_csrf(client, "/auth/password/forgot", json={"email": "known@example.com"})
    assert len(email_sender.outbox) == 1
    assert email_sender.outbox[0]["to"] == "known@example.com"


def test_reset_with_valid_token_changes_the_password(
    make_client, make_user, email_sender
):
    """A1.13: a valid reset token sets the new password; the old one stops working."""
    make_user(email="ada@example.com")
    post_with_csrf(
        make_client(), "/auth/password/forgot", json={"email": "ada@example.com"}
    )
    raw_token = reset_token_from_outbox(email_sender)

    response = post_with_csrf(
        make_client(),
        "/auth/password/reset",
        json={"token": raw_token, "password": NEW_PASSWORD},
    )

    assert response.status_code == 200
    assert login(make_client(), "ada@example.com", DEFAULT_PASSWORD).status_code == 401
    assert login(make_client(), "ada@example.com", NEW_PASSWORD).status_code == 200


def test_reset_token_is_stored_as_hash(
    make_client, make_user, email_sender, db_session
):
    """A1.13: the reset table stores token_hash, never the raw reset token."""
    from app.models import PasswordReset
    from app.security import hash_token

    user = make_user(email="ada@example.com")
    post_with_csrf(
        make_client(), "/auth/password/forgot", json={"email": "ada@example.com"}
    )
    raw_token = reset_token_from_outbox(email_sender)

    row = db_session.query(PasswordReset).filter_by(user_id=user.id).one()
    assert row.token_hash == hash_token(raw_token)
    assert row.token_hash != raw_token


def test_reset_token_lives_one_hour(make_client, make_user, email_sender, db_session):
    """A1.13: a reset token expires one hour after it is created."""
    from app.models import PasswordReset

    user = make_user(email="ada@example.com")
    post_with_csrf(
        make_client(), "/auth/password/forgot", json={"email": "ada@example.com"}
    )

    row = db_session.query(PasswordReset).filter_by(user_id=user.id).one()
    lifetime = row.expires_at - row.created_at
    assert timedelta(minutes=59) <= lifetime <= timedelta(minutes=61)


def test_expired_reset_token_is_rejected(
    make_client, make_user, email_sender, db_session
):
    """A1.13: a reset token whose expires_at is in the past gets 400."""
    from app.models import PasswordReset

    user = make_user(email="ada@example.com")
    post_with_csrf(
        make_client(), "/auth/password/forgot", json={"email": "ada@example.com"}
    )
    raw_token = reset_token_from_outbox(email_sender)
    row = db_session.query(PasswordReset).filter_by(user_id=user.id).one()
    row.expires_at = utc_now() - timedelta(minutes=1)
    db_session.commit()

    response = post_with_csrf(
        make_client(),
        "/auth/password/reset",
        json={"token": raw_token, "password": NEW_PASSWORD},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == RESET_ERROR


def test_reset_token_works_only_once(make_client, make_user, email_sender):
    """A1.13: a reset token is single-use; the second reset gets 400."""
    make_user(email="ada@example.com")
    post_with_csrf(
        make_client(), "/auth/password/forgot", json={"email": "ada@example.com"}
    )
    raw_token = reset_token_from_outbox(email_sender)
    body = {"token": raw_token, "password": NEW_PASSWORD}

    first = post_with_csrf(make_client(), "/auth/password/reset", json=body)
    second = post_with_csrf(make_client(), "/auth/password/reset", json=body)

    assert first.status_code == 200
    assert second.status_code == 400
    assert second.json()["detail"] == RESET_ERROR


def test_unknown_reset_token_is_rejected(make_client):
    """A1.13: a reset token that matches nothing gets 400 with the reset message."""
    response = post_with_csrf(
        make_client(),
        "/auth/password/reset",
        json={"token": "not-a-real-token", "password": NEW_PASSWORD},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == RESET_ERROR


def test_reset_password_must_be_at_least_8_characters(
    make_client, make_user, email_sender
):
    """A1.13: a new password shorter than 8 characters gets 422."""
    make_user(email="ada@example.com")
    post_with_csrf(
        make_client(), "/auth/password/forgot", json={"email": "ada@example.com"}
    )
    raw_token = reset_token_from_outbox(email_sender)

    response = post_with_csrf(
        make_client(),
        "/auth/password/reset",
        json={"token": raw_token, "password": "short"},
    )

    assert response.status_code == 422


def test_reset_ends_all_existing_sessions(make_client, make_user, email_sender):
    """A1.17b: after a password reset, a cookie from before the reset gets 401."""
    make_user(email="ada@example.com")
    logged_in = make_client()
    login(logged_in, "ada@example.com")
    old_cookie = logged_in.cookies.get("lms_session")
    post_with_csrf(
        make_client(), "/auth/password/forgot", json={"email": "ada@example.com"}
    )
    raw_token = reset_token_from_outbox(email_sender)
    post_with_csrf(
        make_client(),
        "/auth/password/reset",
        json={"token": raw_token, "password": NEW_PASSWORD},
    )

    logged_in.cookies.set("lms_session", old_cookie)

    assert logged_in.get("/auth/me").status_code == 401


def test_change_password_with_correct_current_password(client, make_client, make_user):
    """A1.17: a logged-in user with the right current password can change it."""
    make_user(email="ada@example.com")
    login(client, "ada@example.com")

    response = post_with_csrf(
        client,
        "/auth/change-password",
        json={"current_password": DEFAULT_PASSWORD, "new_password": NEW_PASSWORD},
    )

    assert response.status_code == 204
    assert login(make_client(), "ada@example.com", NEW_PASSWORD).status_code == 200
    assert login(make_client(), "ada@example.com", DEFAULT_PASSWORD).status_code == 401


def test_change_password_with_wrong_current_password_is_400(client, make_user):
    """A1.17: a wrong current password gets 400 and the password is not changed."""
    make_user(email="ada@example.com")
    login(client, "ada@example.com")

    response = post_with_csrf(
        client,
        "/auth/change-password",
        json={"current_password": "wrong-password-1", "new_password": NEW_PASSWORD},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Current password is incorrect"


def test_change_password_needs_a_logged_in_user(client):
    """A1.17: change-password returns 401 when nobody is logged in."""
    response = post_with_csrf(
        client,
        "/auth/change-password",
        json={"current_password": DEFAULT_PASSWORD, "new_password": NEW_PASSWORD},
    )

    assert response.status_code == 401
