"""Tests for login, logout, and the current-user endpoint (A1.4, A1.5)."""

from tests.helpers import login, post_with_csrf

WRONG_LOGIN_MESSAGE = "Email or password is incorrect"


def test_correct_login_sets_http_only_session_cookie(client, make_user):
    """A1.4: a correct login returns the user and sets an HTTP-only lms_session cookie."""
    make_user(name="Ada", email="ada@example.com", role="student")

    response = login(client, "ada@example.com")

    assert response.status_code == 200
    body = response.json()
    assert body["id"]
    assert body["name"] == "Ada"
    assert body["email"] == "ada@example.com"
    assert body["role"] == "student"
    cookies = [
        h
        for h in response.headers.get_list("set-cookie")
        if h.startswith("lms_session=")
    ]
    assert cookies, "lms_session cookie was not set"
    assert "httponly" in cookies[0].lower()


def test_wrong_password_gives_generic_message(client, make_user):
    """A1.4: a wrong password gets 401 with the generic message."""
    make_user(email="ada@example.com")

    response = login(client, "ada@example.com", "wrong-password-1")

    assert response.status_code == 401
    assert response.json()["detail"] == WRONG_LOGIN_MESSAGE


def test_unknown_email_gives_the_same_generic_message(client):
    """A1.4: an unknown email gets the same 401 message as a wrong password."""
    response = login(client, "nobody@example.com", "wrong-password-1")

    assert response.status_code == 401
    assert response.json()["detail"] == WRONG_LOGIN_MESSAGE


def test_invited_user_without_password_cannot_log_in(client, make_user):
    """A1.10: a user with status invited and no password gets the generic 401."""
    make_user(email="invited@example.com", status="invited", password=None)

    response = login(client, "invited@example.com", "any-password-1")

    assert response.status_code == 401
    assert response.json()["detail"] == WRONG_LOGIN_MESSAGE


def test_logout_ends_the_session(client, make_user):
    """A1.5: after logout the old cookie no longer works on /auth/me."""
    make_user(email="ada@example.com")
    login(client, "ada@example.com")
    old_cookie = client.cookies.get("lms_session")

    response = post_with_csrf(client, "/auth/logout")

    assert response.status_code == 204
    assert client.cookies.get("lms_session") is None
    client.cookies.set("lms_session", old_cookie)
    assert client.get("/auth/me").status_code == 401


def test_logout_marks_session_revoked_in_database(client, make_user, db_session):
    """A1.5: logout sets revoked_at on the session row."""
    from app.models import Session as LoginSession
    from app.security import hash_token

    make_user(email="ada@example.com")
    login(client, "ada@example.com")
    raw_cookie = client.cookies.get("lms_session")

    post_with_csrf(client, "/auth/logout")

    row = (
        db_session.query(LoginSession)
        .filter_by(token_hash=hash_token(raw_cookie))
        .one()
    )
    assert row.revoked_at is not None


def test_session_table_stores_hash_not_cookie_value(client, make_user, db_session):
    """A1.5: the session table stores a hash of the cookie, never the cookie itself."""
    from app.models import Session as LoginSession
    from app.security import hash_token

    make_user(email="ada@example.com")
    login(client, "ada@example.com")
    raw_cookie = client.cookies.get("lms_session")

    rows = db_session.query(LoginSession).all()

    assert len(rows) == 1
    assert rows[0].token_hash == hash_token(raw_cookie)
    assert rows[0].token_hash != raw_cookie


def test_me_returns_the_logged_in_user(client, make_user):
    """A1.4: GET /auth/me returns id, name, email and role when logged in."""
    make_user(name="Ada", email="ada@example.com", role="instructor")
    login(client, "ada@example.com")

    response = client.get("/auth/me")

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Ada"
    assert body["email"] == "ada@example.com"
    assert body["role"] == "instructor"
    assert "id" in body


def test_me_without_login_is_401(client):
    """A1.4: GET /auth/me returns 401 when nobody is logged in."""
    response = client.get("/auth/me")

    assert response.status_code == 401
