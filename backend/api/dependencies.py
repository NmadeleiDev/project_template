"""
FastAPI dependency injection functions.

This module provides reusable dependencies for route handlers,
primarily for authentication and authorization.

Dependencies:
    get_current_user: Extract and validate current authenticated user from JWT
    current_user_dep: Type-annotated dependency for route handlers

Usage:
    @router.get("/protected")
    async def protected_route(current_user: current_user_dep):
        return {"user_id": current_user.id}
"""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.exceptions import (
    InvalidTokenException,
    NotAuthenticatedException,
    UserNotFoundException,
)
from service.security import decode_access_token
from repository.connection import fastapi_db_dep
from repository.models import User


async def get_current_user(
    request: Request,
    db: AsyncSession = fastapi_db_dep,
) -> User:
    """
    Get currently authenticated user from JWT token.

    Extracts JWT token from HTTP-only cookie, validates it, and loads
    the corresponding user from the database. Used as FastAPI dependency
    to protect routes that require authentication.

    Args:
        request: FastAPI request object containing cookies
        db: Database session (injected dependency)

    Returns:
        User model instance for authenticated user

    Raises:
        NotAuthenticatedException (40102): No JWT token in cookie
        InvalidTokenException (40103): JWT token invalid or malformed
        UserNotFoundException (40105): User ID from token not in database

    Authentication Flow:
        1. Extract "access_token" from request cookies
        2. Decode and validate JWT token
        3. Extract user ID from token payload ("sub" claim)
        4. Query database for user with that ID
        5. Return user model if found

    Example:
        @router.get("/profile")
        async def get_profile(current_user: User = Depends(get_current_user)):
            return {"email": current_user.email}

        # Or use the annotated dependency:
        @router.get("/profile")
        async def get_profile(current_user: current_user_dep):
            return {"email": current_user.email}

    Security Notes:
        - JWT token stored in HTTP-only cookie (not accessible to JavaScript)
        - Token includes expiration time
        - User is loaded fresh from database on each request
        - Invalid tokens result in 401 Unauthorized response
    """
    # Extract JWT from cookie
    access_token = request.cookies.get("access_token")

    if not access_token:
        raise NotAuthenticatedException()

    # Decode and validate JWT
    payload = decode_access_token(access_token)
    if not payload:
        raise InvalidTokenException()

    # Extract user ID from token
    user_id = payload.get("sub")
    if not user_id:
        raise InvalidTokenException()

    # Load user from database
    user = (
        await db.scalars(select(User).where(User.id == UUID(user_id)))
    ).one_or_none()

    if not user:
        raise UserNotFoundException()

    return user


# Type-annotated dependency for cleaner route signatures
current_user_dep = Annotated[User, Depends(get_current_user)]
"""
Type-annotated dependency for current authenticated user.

Use this in route handler signatures for cleaner code:

Example:
    @router.get("/me")
    async def get_me(current_user: current_user_dep):
        return current_user

Instead of:
    @router.get("/me")
    async def get_me(current_user: User = Depends(get_current_user)):
        return current_user
"""
