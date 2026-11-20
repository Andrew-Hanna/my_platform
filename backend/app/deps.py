"""Request dependencies: database session, CSRF check, current user, and role checks."""

import secrets
from collections.abc import Callable, Iterator

from fastapi import Depends, Request
from sqlalchemy.orm import Session as DbSession

from app.db import get_session_factory
from app.errors import DomainError
from app.models import User
from app.services.auth import user_for_session

SESSION_COOKIE = "lms_session"
CSRF_COOKIE = "csrf_token"
CSRF_HEADER = "x-csrf-token"
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


def get_db() -> Iterator[DbSession]:
    """One database session per request, closed afterwards."""
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()


def csrf_protect(request: Request) -> None:
    """Changing requests must echo the csrf_token cookie in the X-CSRF-Token header."""
    if request.method in SAFE_METHODS:
        return
    cookie_value = request.cookies.get(CSRF_COOKIE)
    header_value = request.headers.get(CSRF_HEADER)
    if (
        not cookie_value
        or not header_value
        or not secrets.compare_digest(cookie_value, header_value)
    ):
        raise DomainError(403, "Security check failed. Reload the page and try again.")


def current_user(request: Request, db: DbSession = Depends(get_db)) -> User:
    """The logged-in user, or a 401 error."""
    raw = request.cookies.get(SESSION_COOKIE)
    user = user_for_session(db, raw) if raw else None
    if user is None:
        raise DomainError(401, "Please log in")
    return user


def require_role(*roles: str) -> Callable[..., User]:
    """Build a dependency that allows only the given roles (401 if logged out, 403 if wrong role)."""

    def _check(request: Request, db: DbSession = Depends(get_db)) -> User:
        user = current_user(request, db)
        if user.role not in roles:
            raise DomainError(403, "You do not have permission to do this")
        return user

    return _check
