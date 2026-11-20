"""Tests for CSRF protection on requests that change data (A1.17a)."""

from tests.helpers import csrf_headers, login


def test_csrf_endpoint_sets_cookie_matching_the_body(client):
    """A1.17a: GET /auth/csrf sets a csrf_token cookie and returns the same value in the body."""
    response = client.get("/auth/csrf")

    assert response.status_code == 200
    token = response.json()["csrf_token"]
    assert token
    assert client.cookies.get("csrf_token") == token


def test_post_without_csrf_cookie_or_header_is_403(client):
    """A1.17a: a POST with no CSRF cookie and no header is rejected with 403."""
    response = client.post(
        "/auth/login", json={"email": "x@example.com", "password": "password-1"}
    )

    assert response.status_code == 403


def test_post_without_csrf_header_is_403(client):
    """A1.17a: a POST that has the CSRF cookie but no X-CSRF-Token header gets 403."""
    csrf_headers(client)

    response = client.post(
        "/auth/login", json={"email": "x@example.com", "password": "password-1"}
    )

    assert response.status_code == 403


def test_post_with_wrong_csrf_header_is_403(client):
    """A1.17a: a POST whose X-CSRF-Token does not match the cookie gets 403."""
    csrf_headers(client)

    response = client.post(
        "/auth/login",
        json={"email": "x@example.com", "password": "password-1"},
        headers={"X-CSRF-Token": "not-the-right-token"},
    )

    assert response.status_code == 403


def test_post_with_correct_csrf_header_is_accepted(client, make_user):
    """A1.17a: a POST with the cookie and the matching header is accepted."""
    make_user(email="ada@example.com")

    response = login(client, "ada@example.com")

    assert response.status_code == 200


def test_logout_without_csrf_header_is_403_and_keeps_the_session(client, make_user):
    """A1.17a: logout without the CSRF header is refused, and the session still works."""
    make_user(email="ada@example.com")
    login(client, "ada@example.com")

    response = client.post("/auth/logout")

    assert response.status_code == 403
    assert client.get("/auth/me").status_code == 200
