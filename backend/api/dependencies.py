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
from api.security import decode_access_token
from repository.connection import fastapi_db_dep
from repository.models import User


async def get_current_user(
    request: Request,
    db: AsyncSession = fastapi_db_dep,
) -> User:
    access_token = request.cookies.get("access_token")

    if not access_token:
        raise NotAuthenticatedException()

    payload = decode_access_token(access_token)
    if not payload:
        raise InvalidTokenException()

    user_id = payload.get("sub")
    if not user_id:
        raise InvalidTokenException()

    user = (
        await db.scalars(select(User).where(User.id == UUID(user_id)))
    ).one_or_none()

    if not user:
        raise UserNotFoundException()

    return user


current_user_dep = Annotated[User, Depends(get_current_user)]
