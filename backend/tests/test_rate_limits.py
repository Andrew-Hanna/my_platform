"""Tests for the login, password reset, and invite rate limits (A1.7, A1.17c)."""

from tests.helpers import DEFAULT_PASSWORD, login, post_with_csrf

WRONG_PASSWORD = "wrong-password-1"


def test_sixth_attempt_is_blocked_even_with_correct_password(client, make_user):
    """A1.7: after 5 failed logins for one email, the next attempt gets 429 even with the right password."""
    make_user(email="ada@example.com")

    for _ in range(5):
        assert login(client, "ada@example.com", WRONG_PASSWORD).status_code == 401

    response = login(client, "ada@example.com", DEFAULT_PASSWORD)

    assert response.status_code == 429


def test_failures_for_one_email_do_not_block_another(client, make_user):
    """A1.7: failed attempts for one email do not count against a different email."""
    make_user(email="ada@example.com")
    make_user(email="bob@example.com")

    for _ in range(5):
        login(client, "ada@example.com", WRONG_PASSWORD)

    response = login(client, "bob@example.com", DEFAULT_PASSWORD)

    assert response.status_code == 200


def test_thirty_failures_from_one_ip_block_that_ip(client, make_user):
    """A1.17c: after 30 failed attempts from one IP (different emails), the next attempt gets 429."""
    make_user(email="ada@example.com")

    for number in range(30):
        response = login(client, f"nobody{number}@example.com", WRONG_PASSWORD)
        assert response.status_code == 401

    response = login(client, "ada@example.com", DEFAULT_PASSWORD)

    assert response.status_code == 429


def test_forgot_password_stops_sending_after_five_per_email(
    client, make_user, email_sender
):
    """A1.17c: the 6th reset request for one email still returns 202 but sends no email."""
    make_user(email="ada@example.com")
    first_body = None

    for number in range(5):
        response = post_with_csrf(
            client, "/auth/password/forgot", json={"email": "ada@example.com"}
        )
        assert response.status_code == 202
        first_body = first_body or response.json()

    assert len(email_sender.outbox) == 5

    sixth = post_with_csrf(
        client, "/auth/password/forgot", json={"email": "ada@example.com"}
    )

    assert sixth.status_code == 202
    assert sixth.json() == first_body
    assert len(email_sender.outbox) == 5


def test_invites_are_limited_to_thirty_per_hour(client, make_user):
    """A1.17c: an instructor can create 30 invites an hour; the 31st gets 429."""
    teacher = make_user(role="instructor", email="teacher@example.com")
    login(client, teacher.email)

    for number in range(30):
        response = post_with_csrf(
            client,
            "/users/invite",
            json={"name": f"Student {number}", "email": f"guest{number}@example.com"},
        )
        assert response.status_code == 201

    response = post_with_csrf(
        client, "/users/invite", json={"name": "Too Many", "email": "extra@example.com"}
    )

    assert response.status_code == 429
