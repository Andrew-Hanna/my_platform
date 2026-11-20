"""Tests for accepting invites and the no-public-sign-up rule (A1.11, A1.17e)."""

from datetime import timedelta

from tests.helpers import NEW_PASSWORD, login, post_with_csrf, user_by_email, utc_now

INVITE_ERROR = "This link has expired. Ask your teacher to send a new one."
ACCEPT_URL = "/auth/invites/accept"


def test_accept_sets_password_marks_active_and_logs_in(
    make_client, make_user, make_invite, db_session
):
    """A1.11: a valid invite sets the password, makes the user active, and logs them in."""
    student = make_user(status="invited", password=None, email="new@example.com")
    raw_token = make_invite(student)
    guest = make_client()

    response = post_with_csrf(
        guest, ACCEPT_URL, json={"token": raw_token, "password": NEW_PASSWORD}
    )

    assert response.status_code == 200
    assert guest.cookies.get("lms_session"), (
        "accepting an invite should set lms_session"
    )
    student = user_by_email(db_session, "new@example.com")
    assert student.status == "active"
    assert student.email_verified_at is not None
    assert login(make_client(), "new@example.com", NEW_PASSWORD).status_code == 200


def test_accepted_invite_cannot_be_used_twice(make_client, make_user, make_invite):
    """A1.11: an invite link works once; the second use gets 400."""
    student = make_user(status="invited", password=None)
    raw_token = make_invite(student)
    guest = make_client()
    body = {"token": raw_token, "password": NEW_PASSWORD}

    first = post_with_csrf(guest, ACCEPT_URL, json=body)
    second = post_with_csrf(guest, ACCEPT_URL, json=body)

    assert first.status_code == 200
    assert second.status_code == 400
    assert second.json()["detail"] == INVITE_ERROR


def test_expired_invite_is_rejected(make_client, make_user, make_invite):
    """A1.11: an invite whose expires_at is in the past gets 400 with a clear message."""
    student = make_user(status="invited", password=None)
    raw_token = make_invite(student, expires_at=utc_now() - timedelta(days=1))

    response = post_with_csrf(
        make_client(), ACCEPT_URL, json={"token": raw_token, "password": NEW_PASSWORD}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == INVITE_ERROR


def test_unknown_invite_token_is_rejected(make_client):
    """A1.11: a token that matches no invite gets the same 400 message."""
    response = post_with_csrf(
        make_client(),
        ACCEPT_URL,
        json={"token": "not-a-real-token", "password": NEW_PASSWORD},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == INVITE_ERROR


def test_short_password_is_rejected_with_422(
    make_client, make_user, make_invite, db_session
):
    """A1.11: a password shorter than 8 characters gets 422 and the user stays invited."""
    student = make_user(status="invited", password=None, email="short@example.com")
    raw_token = make_invite(student)

    response = post_with_csrf(
        make_client(), ACCEPT_URL, json={"token": raw_token, "password": "short"}
    )

    assert response.status_code == 422
    assert user_by_email(db_session, "short@example.com").status == "invited"


def test_post_signup_route_does_not_exist(client):
    """A1.17e: there is no public sign-up route, so POST /auth/signup returns 404 or 405."""
    response = post_with_csrf(
        client,
        "/auth/signup",
        json={"email": "x@example.com", "password": NEW_PASSWORD},
    )

    assert response.status_code in (404, 405)


def test_get_signup_route_does_not_exist(client):
    """A1.17e: GET /auth/signup returns 404."""
    response = client.get("/auth/signup")

    assert response.status_code == 404
