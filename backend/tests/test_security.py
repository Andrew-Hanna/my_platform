"""Tests for password hashing and token helpers in app/security.py."""

import hashlib
import re


def test_password_round_trip():
    """A1.2: a password verifies against the hash made from it."""
    from app.security import hash_password, verify_password

    stored = hash_password("correct-horse-1")

    assert verify_password("correct-horse-1", stored) is True


def test_stored_hash_is_not_the_plain_password():
    """A1.2: the hash never equals or contains the plain password."""
    from app.security import hash_password

    stored = hash_password("correct-horse-1")

    assert stored != "correct-horse-1"
    assert "correct-horse-1" not in stored


def test_wrong_password_does_not_verify():
    """A1.2: a wrong password makes verify_password return False."""
    from app.security import hash_password, verify_password

    stored = hash_password("correct-horse-1")

    assert verify_password("wrong-password-1", stored) is False


def test_same_password_gives_different_hashes():
    """A1.2: hashing uses a random salt, so two hashes of one password differ."""
    from app.security import hash_password

    assert hash_password("correct-horse-1") != hash_password("correct-horse-1")


def test_generate_token_is_long_url_safe_and_unique():
    """A1.9: a generated token is at least 32 URL-safe characters and differs each time."""
    from app.security import generate_token

    first = generate_token()
    second = generate_token()

    assert len(first) >= 32
    assert re.fullmatch(r"[A-Za-z0-9_\-]+", first)
    assert first != second


def test_hash_token_is_sha256_hex():
    """A1.9: hash_token returns the sha256 hex digest of the raw token."""
    from app.security import hash_token

    expected = hashlib.sha256(b"abc").hexdigest()

    assert hash_token("abc") == expected
    assert hash_token("abc") != "abc"
