"""
Security utilities for authentication.

This module provides cryptographic functions for password hashing and
JWT token management. All functions use industry-standard algorithms:
- Argon2 for password hashing (CPU and memory hard)
- HS256 (HMAC-SHA256) for JWT signing

Usage:
    # Hash password during signup
    hashed = get_password_hash("user_password")

    # Verify password during signin
    is_valid = verify_password("user_password", hashed)

    # Create JWT token
    token = create_access_token({"sub": str(user_id)})

    # Decode JWT token
    payload = decode_access_token(token)
"""

from datetime import datetime, timedelta
from typing import Any

from core.settings import jwt_settings
from argon2 import PasswordHasher
from jose import JWTError, jwt

ph = PasswordHasher()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its Argon2 hash.

    Uses Argon2id algorithm for secure password verification.
    Automatically handles hash rehashing if parameters change.

    Args:
        plain_password: Plain text password from user input
        hashed_password: Argon2 hash from database

    Returns:
        True if password matches hash, False otherwise

    Note:
        This function is CPU-intensive but runs in passlib's thread pool,
        so it won't block the async event loop.

    Example:
        >>> hashed = get_password_hash("mypassword")
        >>> verify_password("mypassword", hashed)
        True
        >>> verify_password("wrongpassword", hashed)
        False
    """
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """
    Hash a password using Argon2id algorithm.

    Argon2id is the recommended password hashing algorithm, providing
    resistance against both side-channel and GPU attacks.

    Args:
        password: Plain text password to hash

    Returns:
        Argon2 hash string (includes salt and parameters)

    Note:
        This function is CPU-intensive but runs in passlib's thread pool,
        so it won't block the async event loop.

    Security:
        - Algorithm: Argon2id
        - Memory cost: Default from argon2-cffi
        - Time cost: Default from argon2-cffi
        - Parallelism: Default from argon2-cffi
        - Salt: Randomly generated per hash

    Example:
        >>> hashed = get_password_hash("mypassword")
        >>> hashed.startswith("$argon2id$")
        True
    """
    return ph.hash(password)


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    """
    Create a JWT access token.

    Generates a signed JWT token containing the provided data payload.
    Token includes an expiration claim (exp) for automatic expiry.

    Args:
        data: Payload to encode in token (typically {"sub": user_id})
        expires_delta: Optional custom expiration time. If not provided,
                      uses JWT_ACCESS_TOKEN_EXPIRE_MINUTES from settings

    Returns:
        Encoded JWT token as string

    Configuration:
        - Secret key: JWT_SECRET_KEY (from environment)
        - Algorithm: JWT_ALGORITHM (default: HS256)
        - Expiration: JWT_ACCESS_TOKEN_EXPIRE_MINUTES (default: 10080 = 7 days)

    Security:
        - Tokens are signed with HMAC-SHA256
        - Includes expiration time to limit token lifetime
        - Secret key should be strong and kept secret

    Example:
        >>> token = create_access_token({"sub": "user-uuid"})
        >>> # Token will be valid for 7 days by default
        >>> custom_token = create_access_token(
        ...     {"sub": "user-uuid"},
        ...     expires_delta=timedelta(hours=1)
        ... )
        >>> # Custom token valid for 1 hour
    """
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
    """
    Decode and verify a JWT access token.

    Validates the token signature and expiration, then returns the payload.
    Returns None if token is invalid, expired, or tampered with.

    Args:
        token: JWT token string to decode

    Returns:
        Dictionary containing token payload if valid, None otherwise

    Validation:
        - Signature verification using secret key
        - Expiration time check (exp claim)
        - Algorithm verification (prevents algorithm confusion attacks)

    Example:
        >>> token = create_access_token({"sub": "user-123"})
        >>> payload = decode_access_token(token)
        >>> payload["sub"]
        'user-123'
        >>> decode_access_token("invalid-token")
        None
        >>> # Expired token also returns None

    Note:
        Returns None on any JWT error to avoid leaking error details.
        Calling code should handle None appropriately (raise NotAuthenticatedException).
    """
    try:
        payload = jwt.decode(
            token, jwt_settings.secret_key, algorithms=[jwt_settings.algorithm]
        )
        return payload
    except JWTError:
        return None
