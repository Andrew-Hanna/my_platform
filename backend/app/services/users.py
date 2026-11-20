"""Rules for creating, inviting, and disabling accounts. No HTTP code here."""

from datetime import timedelta

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session as DbSession

from app.adapters.email import EmailSender
from app.errors import DomainError
from app.models import Invite, User
from app.services.auth import issue_invite, now, revoke_all_sessions

INVITES_PER_HOUR_PER_CALLER = 30


def invite_student(
    db: DbSession,
    caller: User,
    name: str,
    email: str,
    sender: EmailSender,
    base_url: str,
) -> User:
    """Create a student account in the invited state and send them an invite."""
    since = now() - timedelta(hours=1)
    recent = db.scalar(
        select(func.count(Invite.id)).where(
            Invite.created_by_id == caller.id, Invite.created_at >= since
        )
    )
    if recent >= INVITES_PER_HOUR_PER_CALLER:
        raise DomainError(429, "Too many invites. Try again later.")
    if db.scalar(select(User.id).where(User.email == email)) is not None:
        raise DomainError(409, "A user with this email already exists")
    user = User(
        name=name,
        email=email,
        password_hash=None,
        role="student",
        status="invited",
        created_at=now(),
    )
    db.add(user)
    db.commit()
    issue_invite(db, user, created_by_id=caller.id, sender=sender, base_url=base_url)
    return user


def resend_invite(
    db: DbSession, user_id: int, sender: EmailSender, base_url: str
) -> User:
    """Revoke older invites for an invited user and send a fresh one."""
    user = db.get(User, user_id)
    if user is None:
        raise DomainError(404, "User not found")
    if user.status != "invited":
        raise DomainError(409, "This user has already set a password")
    db.execute(
        update(Invite)
        .where(
            Invite.user_id == user.id,
            Invite.used_at.is_(None),
            Invite.revoked_at.is_(None),
        )
        .values(revoked_at=now())
    )
    db.commit()
    issue_invite(db, user, created_by_id=None, sender=sender, base_url=base_url)
    return user


def set_account_status(db: DbSession, user_id: int, status: str) -> None:
    """Disable or enable an account. Disabling also ends all of the user's sessions."""
    user = db.get(User, user_id)
    if user is None:
        raise DomainError(404, "User not found")
    if status == "disabled":
        user.status = "disabled"
        db.commit()
        revoke_all_sessions(db, user.id)
        return
    if user.status == "disabled":
        user.status = "active"
        db.commit()
