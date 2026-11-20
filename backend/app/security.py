"""Password hashing and secure random tokens. Raw tokens are never stored; only their SHA-256 hash is."""

import hashlib
import hmac
import os
import secrets

# scrypt cost settings: memory-hard, from the Python standard library (no extra dependency).
_SCRYPT_N = 2**14
_SCRYPT_R = 8
_SCRYPT_P = 1
_KEY_LENGTH = 32


def hash_password(password: str) -> str:
    """Return a salted scrypt hash in the form scrypt$N$r$p$salt$key."""
    salt = os.urandom(16)
    key = hashlib.scrypt(
        password.encode(),
        salt=salt,
        n=_SCRYPT_N,
        r=_SCRYPT_R,
        p=_SCRYPT_P,
        dklen=_KEY_LENGTH,
    )
    return f"scrypt${_SCRYPT_N}${_SCRYPT_R}${_SCRYPT_P}${salt.hex()}${key.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    """Check a password against a stored hash. Returns False for any malformed hash."""
    try:
        _, n, r, p, salt_hex, key_hex = password_hash.split("$")
        key = hashlib.scrypt(
            password.encode(),
            salt=bytes.fromhex(salt_hex),
            n=int(n),
            r=int(r),
            p=int(p),
            dklen=len(bytes.fromhex(key_hex)),
        )
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(key, bytes.fromhex(key_hex))


def generate_token() -> str:
    """A long random URL-safe string, used for session cookies, invites, and reset links."""
    return secrets.token_urlsafe(32)


def hash_token(raw: str) -> str:
    """SHA-256 hex digest of a raw token. This is what the database stores."""
    return hashlib.sha256(raw.encode()).hexdigest()
