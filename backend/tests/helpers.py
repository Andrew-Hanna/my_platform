"""Small helper functions shared by the account tests.

This file does not import app code at the top. Each helper that needs the app
imports it inside the function, so a missing module fails one test, not the run.
"""

import re
from datetime import UTC, datetime

DEFAULT_PASSWORD = "correct-horse-1"
NEW_PASSWORD = "brand-new-pass-2"


def utc_now():
    """Return the current time in UTC, timezone-aware."""
    return datetime.now(UTC)


def csrf_headers(client):
    """Fetch a CSRF token with GET /auth/csrf and return the header dict to send with POSTs."""
    response = client.get("/auth/csrf")
    return {"X-CSRF-Token": response.json()["csrf_token"]}


def post_with_csrf(client, url, json=None):
    """POST to url with a valid CSRF header (the cookie is set by the GET first)."""
    return client.post(url, json=json, headers=csrf_headers(client))


def login(client, email, password=DEFAULT_PASSWORD):
    """Log in through POST /auth/login and return the response."""
    return post_with_csrf(
        client, "/auth/login", json={"email": email, "password": password}
    )


def user_by_email(db_session, email):
    """Load one User row by email, reading the latest committed data."""
    from app.models import User

    db_session.expire_all()
    return db_session.query(User).filter_by(email=email).one()


def invite_token_from_outbox(sender, index=-1):
    """Pull the raw invite token out of an email link like {base_url}/invite/{token}."""
    body = sender.outbox[index]["body"]
    match = re.search(r"/invite/([A-Za-z0-9_\-]+)", body)
    assert match, f"no /invite/ link in email body: {body!r}"
    return match.group(1)


def reset_token_from_outbox(sender, index=-1):
    """Pull the raw reset token out of a reset email. The token is the longest URL-safe run of 32+ characters."""
    body = sender.outbox[index]["body"]
    candidates = re.findall(r"[A-Za-z0-9_\-]{32,}", body)
    assert candidates, f"no reset token found in email body: {body!r}"
    return max(candidates, key=len)
