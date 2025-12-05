"""Security utilities for authentication."""

from datetime import datetime, timedelta
from typing import Any

from core.settings import jwt_settings
from argon2 import PasswordHasher
from jose import JWTError, jwt

ph = PasswordHasher()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Hash a password using Argon2."""
    return ph.hash(password)


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=jwt_settings.access_token_expire_minutes
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, jwt_settings.secret_key, algorithm=jwt_settings.algorithm
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decode and verify a JWT access token."""
    try:
        payload = jwt.decode(
            token, jwt_settings.secret_key, algorithms=[jwt_settings.algorithm]
        )
        return payload
    except JWTError:
        return None
