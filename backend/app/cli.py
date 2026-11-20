"""Command-line tools. Create the first admin account with: uv run python -m app.cli --email ... --name ..."""

import argparse
import getpass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from app.db import get_session_factory
from app.models import User
from app.security import hash_password
from app.services.auth import MIN_PASSWORD_LENGTH


def create_admin_user(db: DbSession, email: str, name: str, password: str) -> User:
    """Create an active admin. Raises ValueError if the email is taken."""
    if db.scalar(select(User.id).where(User.email == email)) is not None:
        raise ValueError("A user with this email already exists")
    user = User(
        name=name,
        email=email,
        role="admin",
        status="active",
        password_hash=hash_password(password),
        created_at=datetime.now(UTC),
    )
    db.add(user)
    db.commit()
    return user


def main() -> None:
    """Ask for a password (hidden) and create the admin account."""
    parser = argparse.ArgumentParser(description="Create an admin account")
    parser.add_argument("--email", required=True)
    parser.add_argument("--name", required=True)
    args = parser.parse_args()
    password = getpass.getpass("Password: ")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise SystemExit(f"Password must be at least {MIN_PASSWORD_LENGTH} characters")
    db = get_session_factory()()
    try:
        create_admin_user(db, args.email, args.name, password)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    finally:
        db.close()
    print(f"Admin created: {args.email}")


if __name__ == "__main__":
    main()
