"""Authentication and password security helpers."""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from jwt import InvalidTokenError

from app.core.config import get_settings

PASSWORD_HASH_SCHEME = "pbkdf2_sha256"


def get_password_hash(password: str) -> str:
    """Hash a plaintext password using salted PBKDF2-SHA256."""
    settings = get_settings()
    salt = secrets.token_urlsafe(24)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        settings.password_hash_iterations,
    )
    encoded_digest = base64.b64encode(digest).decode("utf-8")
    return (
        f"{PASSWORD_HASH_SCHEME}${settings.password_hash_iterations}"
        f"${salt}${encoded_digest}"
    )


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verify a plaintext password against a stored password hash."""
    try:
        scheme, iterations_raw, salt, encoded_digest = password_hash.split("$", maxsplit=3)
        iterations = int(iterations_raw)
    except ValueError:
        return False

    if scheme != PASSWORD_HASH_SCHEME:
        return False

    expected_digest = base64.b64decode(encoded_digest.encode("utf-8"))
    candidate_digest = hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    )
    return hmac.compare_digest(candidate_digest, expected_digest)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT access token for a user subject."""
    settings = get_settings()
    expires_at = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload: dict[str, Any] = {"sub": subject, "exp": expires_at}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> str | None:
    """Return the token subject when the access token is valid."""
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except InvalidTokenError:
        return None

    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject:
        return None
    return subject
