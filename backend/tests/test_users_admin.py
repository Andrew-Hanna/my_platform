"""Tests for staff invites, resend, disable/enable, and role checks (A1.6, A1.9, A1.10, A1.12, A1.14)."""

from datetime import timedelta

import pytest

from tests.helpers import (
    DEFAULT_PASSWORD,
    NEW_PASSWORD,
    invite_token_from_outbox,
    login,
    post_with_csrf,
    user_by_email,
)

INVITE_ERROR = "This link has expired. Ask your teacher to send a new one."
WRONG_LOGIN_MESSAGE = "Email or password is incorrect"


@pytest.mark.parametrize("staff_role", ["instructor", "assistant"])
def test_staff_can_invite_a_student(
    client, make_user, db_session, email_sender, staff_role
):
    """A1.10: an instructor or assistant creates a student with status invited and sends one email."""
    staff = make_user(role=staff_role, email="staff@example.com")
    login(client, staff.email)

    response = post_with_csrf(
        client, "/users/invite", json={"name": "Sam", "email": "sam@example.com"}
    )

    assert response.status_code == 201
    sam = user_by_email(db_session, "sam@example.com")
    assert sam.role == "student"
    assert sam.status == "invited"
    assert sam.password_hash is None
    assert len(email_sender.outbox) == 1
    assert email_sender.outbox[0]["to"] == "sam@example.com"
    assert "/invite/" in email_sender.outbox[0]["body"]


def test_student_cannot_invite(client, make_user, db_session):
    """A1.10: a student gets 403 when trying to invite someone, and no user row is created."""
    from app.models import User

    student = make_user(role="student", email="stu@example.com")
    login(client, student.email)

    response = post_with_csrf(
        client, "/users/invite", json={"name": "Sam", "email": "sam@example.com"}
    )

    assert response.status_code == 403
    assert db_session.query(User).filter_by(email="sam@example.com").count() == 0


def test_anonymous_cannot_invite(client):
    """A1.6: an anonymous caller gets 401 on the invite route."""
    response = post_with_csrf(
        client, "/users/invite", json={"name": "Sam", "email": "sam@example.com"}
    )

    assert response.status_code == 401


def test_invite_expires_three_days_after_creation(client, make_user, db_session):
    """A1.9: a new invite is valid for 3 days."""
    from app.models import Invite

    teacher = make_user(role="instructor", email="teacher@example.com")
    login(client, teacher.email)
    post_with_csrf(
        client, "/users/invite", json={"name": "Sam", "email": "sam@example.com"}
    )

    sam = user_by_email(db_session, "sam@example.com")
    invite = db_session.query(Invite).filter_by(user_id=sam.id).one()
    lifetime = invite.expires_at - invite.created_at
    assert (
        timedelta(days=3) - timedelta(minutes=1)
        <= lifetime
        <= timedelta(days=3) + timedelta(minutes=1)
    )


def test_duplicate_invite_email_is_409(client, make_user):
    """A1.10: inviting an email that already exists gets 409."""
    teacher = make_user(role="instructor", email="teacher@example.com")
    make_user(email="sam@example.com")
    login(client, teacher.email)

    response = post_with_csrf(
        client, "/users/invite", json={"name": "Sam", "email": "sam@example.com"}
    )

    assert response.status_code == 409


def test_resend_makes_the_old_link_invalid(
    make_client, client, make_user, db_session, email_sender
):
    """A1.12: after resend, the old invite link gets 400 and the new one works."""
    teacher = make_user(role="instructor", email="teacher@example.com")
    login(client, teacher.email)
    post_with_csrf(
        client, "/users/invite", json={"name": "Sam", "email": "sam@example.com"}
    )
    old_token = invite_token_from_outbox(email_sender)
    sam = user_by_email(db_session, "sam@example.com")

    resend = post_with_csrf(client, f"/users/{sam.id}/resend-invite")
    new_token = invite_token_from_outbox(email_sender)

    assert resend.status_code == 200
    assert new_token != old_token
    guest = make_client()
    old_result = post_with_csrf(
        guest,
        "/auth/invites/accept",
        json={"token": old_token, "password": NEW_PASSWORD},
    )
    new_result = post_with_csrf(
        guest,
        "/auth/invites/accept",
        json={"token": new_token, "password": NEW_PASSWORD},
    )
    assert old_result.status_code == 400
    assert old_result.json()["detail"] == INVITE_ERROR
    assert new_result.status_code == 200


def test_resend_revokes_the_older_unused_invite(
    client, make_user, db_session, email_sender
):
    """A1.12: resend sets revoked_at on the older unused invite row."""
    from app.models import Invite

    teacher = make_user(role="instructor", email="teacher@example.com")
    login(client, teacher.email)
    post_with_csrf(
        client, "/users/invite", json={"name": "Sam", "email": "sam@example.com"}
    )
    sam = user_by_email(db_session, "sam@example.com")

    post_with_csrf(client, f"/users/{sam.id}/resend-invite")

    invites = (
        db_session.query(Invite).filter_by(user_id=sam.id).order_by(Invite.id).all()
    )
    assert len(invites) == 2
    assert invites[0].revoked_at is not None
    assert invites[1].revoked_at is None
    assert len(email_sender.outbox) == 2


def test_resend_is_refused_for_an_active_user(client, make_user):
    """A1.12: resend-invite works only for status invited; an active user gets 409."""
    teacher = make_user(role="instructor", email="teacher@example.com")
    active = make_user(role="student", status="active", email="ada@example.com")
    login(client, teacher.email)

    response = post_with_csrf(client, f"/users/{active.id}/resend-invite")

    assert response.status_code == 409


def test_student_gets_403_on_admin_only_disable_route(client, make_user):
    """A1.6: a student gets 403 on POST /users/{id}/disable, which is admin only."""
    student = make_user(role="student", email="stu@example.com")
    target = make_user(role="student", email="other@example.com")
    login(client, student.email)

    response = post_with_csrf(client, f"/users/{target.id}/disable")

    assert response.status_code == 403


def test_instructor_gets_403_on_admin_only_disable_route(client, make_user):
    """A1.6: an instructor is also refused on the admin-only disable route."""
    instructor = make_user(role="instructor", email="teacher@example.com")
    target = make_user(role="student", email="other@example.com")
    login(client, instructor.email)

    response = post_with_csrf(client, f"/users/{target.id}/disable")

    assert response.status_code == 403


def test_anonymous_gets_401_on_admin_only_disable_route(client, make_user):
    """A1.6: an anonymous caller gets 401 on the admin-only disable route."""
    target = make_user(role="student", email="other@example.com")

    response = post_with_csrf(client, f"/users/{target.id}/disable")

    assert response.status_code == 401


def test_disabled_user_cannot_log_in(make_client, make_user):
    """A1.14: a disabled user gets the generic 401 on login."""
    admin = make_user(role="admin", email="admin@example.com")
    student = make_user(role="student", email="stu@example.com")
    admin_client = make_client()
    login(admin_client, admin.email)
    assert (
        post_with_csrf(admin_client, f"/users/{student.id}/disable").status_code == 204
    )

    response = login(make_client(), student.email, DEFAULT_PASSWORD)

    assert response.status_code == 401
    assert response.json()["detail"] == WRONG_LOGIN_MESSAGE


def test_disable_ends_the_users_existing_session(make_client, make_user, db_session):
    """A1.14: disabling a user revokes their sessions, so an old cookie gets 401."""
    admin = make_user(role="admin", email="admin@example.com")
    student = make_user(role="student", email="stu@example.com")
    student_client = make_client()
    admin_client = make_client()
    login(student_client, student.email)
    login(admin_client, admin.email)

    response = post_with_csrf(admin_client, f"/users/{student.id}/disable")

    assert response.status_code == 204
    assert user_by_email(db_session, "stu@example.com").status == "disabled"
    assert student_client.get("/auth/me").status_code == 401


def test_enable_restores_login(make_client, make_user):
    """A1.14: after enable, a previously disabled user can log in again."""
    admin = make_user(role="admin", email="admin@example.com")
    student = make_user(role="student", email="stu@example.com")
    admin_client = make_client()
    login(admin_client, admin.email)
    post_with_csrf(admin_client, f"/users/{student.id}/disable")

    response = post_with_csrf(admin_client, f"/users/{student.id}/enable")

    assert response.status_code == 204
    assert login(make_client(), student.email).status_code == 200
