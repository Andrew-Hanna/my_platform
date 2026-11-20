"""Login, logout, invites, password reset, and CSRF token endpoints."""

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session as DbSession

from app.adapters.email import EmailSender, get_email_sender
from app.config import cached_settings
from app.deps import CSRF_COOKIE, SESSION_COOKIE, csrf_protect, current_user, get_db
from app.schemas import (
    AcceptInviteIn,
    ChangePasswordIn,
    ForgotPasswordIn,
    LoginIn,
    ResetPasswordIn,
)
from app.security import generate_token
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", dependencies=[Depends(csrf_protect)])

SESSION_SECONDS = int(auth_service.SESSION_LIFETIME.total_seconds())
FORGOT_MESSAGE = {"detail": "If that email has an account, a reset link is on its way."}


def _user_json(user) -> dict:
    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role}


def _set_session_cookie(response: Response, raw: str) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        raw,
        max_age=SESSION_SECONDS,
        httponly=True,
        samesite="lax",
        secure=cached_settings().session_cookie_secure,
        path="/",
    )


@router.get("/csrf")
def get_csrf_token(response: Response) -> dict:
    """Set the csrf_token cookie and return the same value for the header."""
    token = generate_token()
    response.set_cookie(
        CSRF_COOKIE,
        token,
        httponly=False,
        samesite="lax",
        secure=cached_settings().session_cookie_secure,
        path="/",
    )
    return {"csrf_token": token}


@router.post("/login")
def login(
    body: LoginIn,
    request: Request,
    response: Response,
    db: DbSession = Depends(get_db),
) -> dict:
    """Check email and password, then start a session cookie."""
    ip = request.client.host if request.client else "unknown"
    user = auth_service.authenticate(db, body.email, body.password, ip)
    raw = auth_service.create_session(db, user)
    _set_session_cookie(response, raw)
    return _user_json(user)


@router.post("/logout", status_code=204)
def logout(request: Request, db: DbSession = Depends(get_db)) -> Response:
    """End the current session and remove its cookie."""
    raw = request.cookies.get(SESSION_COOKIE)
    if raw:
        auth_service.revoke_session(db, raw)
    response = Response(status_code=204)
    response.delete_cookie(SESSION_COOKIE, path="/")
    return response


@router.get("/me")
def me(user=Depends(current_user), db: DbSession = Depends(get_db)) -> dict:
    """The logged-in user's basic details."""
    return _user_json(user)


@router.post("/invites/accept")
def accept_invite(
    body: AcceptInviteIn,
    response: Response,
    db: DbSession = Depends(get_db),
) -> dict:
    """Set a password from an invite link and log the student in."""
    user = auth_service.accept_invite(db, body.token, body.password)
    raw = auth_service.create_session(db, user)
    _set_session_cookie(response, raw)
    return _user_json(user)


@router.post("/password/forgot", status_code=202)
def forgot_password(
    body: ForgotPasswordIn,
    db: DbSession = Depends(get_db),
    sender: EmailSender = Depends(get_email_sender),
) -> dict:
    """Send a reset link if the account exists. The answer is the same either way."""
    auth_service.request_password_reset(
        db, body.email, sender, cached_settings().app_base_url
    )
    return FORGOT_MESSAGE


@router.post("/password/reset")
def reset_password(body: ResetPasswordIn, db: DbSession = Depends(get_db)) -> dict:
    """Set a new password from a reset link. This ends all existing sessions."""
    auth_service.reset_password(db, body.token, body.password)
    return {"detail": "Your password has been changed. Please log in."}


@router.post("/change-password", status_code=204)
def change_password(
    body: ChangePasswordIn,
    user=Depends(current_user),
    db: DbSession = Depends(get_db),
) -> Response:
    """Change the logged-in user's password after checking the current one."""
    auth_service.change_password(db, user, body.current_password, body.new_password)
    return Response(status_code=204)
