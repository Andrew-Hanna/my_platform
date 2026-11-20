"""Staff endpoints for creating student invites and disabling accounts."""

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session as DbSession

from app.adapters.email import EmailSender, get_email_sender
from app.config import cached_settings
from app.deps import csrf_protect, get_db, require_role
from app.models import User
from app.schemas import InviteStudentIn
from app.services import users as users_service

router = APIRouter(prefix="/users", dependencies=[Depends(csrf_protect)])

STAFF = ("instructor", "assistant", "admin")


@router.post("/invite", status_code=201)
def invite_student(
    body: InviteStudentIn,
    caller: User = Depends(require_role(*STAFF)),
    db: DbSession = Depends(get_db),
    sender: EmailSender = Depends(get_email_sender),
) -> dict:
    """Create a student account and email them an invite link."""
    user = users_service.invite_student(
        db, caller, body.name, body.email, sender, cached_settings().app_base_url
    )
    return {"id": user.id, "email": user.email, "status": user.status}


@router.post("/{user_id}/resend-invite")
def resend_invite(
    user_id: int,
    caller: User = Depends(require_role(*STAFF)),
    db: DbSession = Depends(get_db),
    sender: EmailSender = Depends(get_email_sender),
) -> dict:
    """Send a fresh invite and cancel older ones for this user."""
    user = users_service.resend_invite(
        db, user_id, sender, cached_settings().app_base_url
    )
    return {"id": user.id, "status": user.status}


@router.post("/{user_id}/disable", status_code=204)
def disable_user(
    user_id: int,
    caller: User = Depends(require_role("admin")),
    db: DbSession = Depends(get_db),
) -> Response:
    """Block login for an account and end its sessions."""
    users_service.set_account_status(db, user_id, "disabled")
    return Response(status_code=204)


@router.post("/{user_id}/enable", status_code=204)
def enable_user(
    user_id: int,
    caller: User = Depends(require_role("admin")),
    db: DbSession = Depends(get_db),
) -> Response:
    """Allow a disabled account to log in again."""
    users_service.set_account_status(db, user_id, "active")
    return Response(status_code=204)
