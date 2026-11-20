"""Account rules: login, sessions, invites, and password reset. No HTTP code here."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session as DbSession

from app.adapters.email import EmailSender
from app.errors import DomainError
from app.models import Invite, LoginAttempt, PasswordReset, User
from app.models import Session as LoginSession
from app.security import generate_token, hash_password, hash_token, verify_password

SESSION_LIFETIME = timedelta(days=7)
INVITE_LIFETIME = timedelta(days=3)
RESET_LIFETIME = timedelta(minutes=60)
LIMIT_WINDOW = timedelta(minutes=15)
LOGIN_LIMIT_PER_EMAIL = 5
LOGIN_LIMIT_PER_IP = 30
RESET_LIMIT_PER_HOUR = 5
MIN_PASSWORD_LENGTH = 8

WRONG_LOGIN_MESSAGE = "Email or password is incorrect"
INVITE_ERROR = "This link has expired. Ask your teacher to send a new one."
RESET_ERROR = "This reset link is not valid. Request a new one."


def now() -> datetime:
    """Current time in UTC."""
    return datetime.now(UTC)


def check_password_length(password: str) -> None:
    """Reject passwords shorter than the minimum."""
    if len(password) < MIN_PASSWORD_LENGTH:
        raise DomainError(
            422, f"Password must be at least {MIN_PASSWORD_LENGTH} characters"
        )


def _check_login_limits(db: DbSession, email: str, ip: str) -> None:
    """Block logins after too many recent failures for this email or from this IP."""
    since = now() - LIMIT_WINDOW
    failures_for_email = db.scalar(
        select(func.count(LoginAttempt.id)).where(
            LoginAttempt.email == email, LoginAttempt.failed_at >= since
        )
    )
    failures_from_ip = db.scalar(
        select(func.count(LoginAttempt.id)).where(
            LoginAttempt.ip == ip, LoginAttempt.failed_at >= since
        )
    )
    if (
        failures_for_email >= LOGIN_LIMIT_PER_EMAIL
        or failures_from_ip >= LOGIN_LIMIT_PER_IP
    ):
        raise DomainError(429, "Too many attempts. Try again in 15 minutes.")


def authenticate(db: DbSession, email: str, password: str, ip: str) -> User:
    """Return the user if the login is valid. Otherwise record the failure and raise."""
    _check_login_limits(db, email, ip)
    user = db.scalar(select(User).where(User.email == email))
    valid = (
        user is not None
        and user.status == "active"
        and user.password_hash is not None
        and verify_password(password, user.password_hash)
    )
    if not valid:
        db.add(LoginAttempt(email=email, ip=ip, failed_at=now()))
        db.commit()
        raise DomainError(401, WRONG_LOGIN_MESSAGE)
    return user


def create_session(db: DbSession, user: User) -> str:
    """Start a login session and return the raw cookie value (only its hash is stored)."""
    raw = generate_token()
    created = now()
    db.add(
        LoginSession(
            user_id=user.id,
            token_hash=hash_token(raw),
            created_at=created,
            expires_at=created + SESSION_LIFETIME,
        )
    )
    db.commit()
    return raw


def revoke_session(db: DbSession, raw: str) -> None:
    """End one login session."""
    db.execute(
        update(LoginSession)
        .where(LoginSession.token_hash == hash_token(raw))
        .values(revoked_at=now())
    )
    db.commit()


def revoke_all_sessions(db: DbSession, user_id: int) -> None:
    """End every login session for a user (used on disable and password reset)."""
    db.execute(
        update(LoginSession)
        .where(LoginSession.user_id == user_id, LoginSession.revoked_at.is_(None))
        .values(revoked_at=now())
    )
    db.commit()


def user_for_session(db: DbSession, raw: str) -> User | None:
    """Return the user behind a valid, unexpired, unrevoked session. Disabled users get None."""
    row = db.execute(
        select(LoginSession, User)
        .join(User, User.id == LoginSession.user_id)
        .where(LoginSession.token_hash == hash_token(raw))
    ).first()
    if row is None:
        return None
    session_row, user = row
    if session_row.revoked_at is not None or session_row.expires_at <= now():
        return None
    if user.status != "active":
        return None
    return user


def issue_invite(
    db: DbSession,
    user: User,
    created_by_id: int | None,
    sender: EmailSender,
    base_url: str,
) -> None:
    """Create an invite for a user and email the link. The raw token is only in the email."""
    raw = generate_token()
    created = now()
    db.add(
        Invite(
            user_id=user.id,
            token_hash=hash_token(raw),
            created_by_id=created_by_id,
            created_at=created,
            expires_at=created + INVITE_LIFETIME,
        )
    )
    db.commit()
    sender.send(
        to=user.email,
        subject="Your invitation to the LMS",
        body=f"Set your password here: {base_url}/invite/{raw}\nThis link expires in 3 days.",
    )


def accept_invite(db: DbSession, raw: str, password: str) -> User:
    """Set the password for an invited user and mark the invite used. Accepting also verifies the email."""
    check_password_length(password)
    invite = db.scalar(select(Invite).where(Invite.token_hash == hash_token(raw)))
    if (
        invite is None
        or invite.used_at is not None
        or invite.revoked_at is not None
        or invite.expires_at <= now()
    ):
        raise DomainError(400, INVITE_ERROR)
    user = db.get(User, invite.user_id)
    when = now()
    user.password_hash = hash_password(password)
    user.status = "active"
    user.email_verified_at = when
    invite.used_at = when
    db.commit()
    return user


def request_password_reset(
    db: DbSession, email: str, sender: EmailSender, base_url: str
) -> None:
    """Email a reset link to an active account. Unknown emails and rate-limited requests send nothing."""
    user = db.scalar(select(User).where(User.email == email))
    if user is None or user.status != "active":
        return
    since = now() - timedelta(hours=1)
    recent = db.scalar(
        select(func.count(PasswordReset.id)).where(
            PasswordReset.user_id == user.id, PasswordReset.created_at >= since
        )
    )
    if recent >= RESET_LIMIT_PER_HOUR:
        return
    raw = generate_token()
    created = now()
    db.add(
        PasswordReset(
            user_id=user.id,
            token_hash=hash_token(raw),
            created_at=created,
            expires_at=created + RESET_LIFETIME,
        )
    )
    db.commit()
    sender.send(
        to=user.email,
        subject="Reset your LMS password",
        body=f"Reset your password here: {base_url}/reset-password/{raw}\nThis link expires in 1 hour.",
    )


def reset_password(db: DbSession, raw: str, password: str) -> None:
    """Set a new password from a valid reset link, then end all of that user's sessions."""
    check_password_length(password)
    reset = db.scalar(
        select(PasswordReset).where(PasswordReset.token_hash == hash_token(raw))
    )
    if reset is None or reset.used_at is not None or reset.expires_at <= now():
        raise DomainError(400, RESET_ERROR)
    user = db.get(User, reset.user_id)
    user.password_hash = hash_password(password)
    reset.used_at = now()
    db.commit()
    revoke_all_sessions(db, user.id)


def change_password(db: DbSession, user: User, current: str, new: str) -> None:
    """Change a logged-in user's password after checking the current one."""
    check_password_length(new)
    if user.password_hash is None or not verify_password(current, user.password_hash):
        raise DomainError(400, "Current password is incorrect")
    user.password_hash = hash_password(new)
    db.commit()
