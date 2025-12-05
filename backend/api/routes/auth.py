from fastapi import APIRouter, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.exceptions import InvalidCredentialsException, UserAlreadyExistsException
from api.schemas import AuthResponse, SignInRequest, SignUpRequest
from api.security import create_access_token, get_password_hash, verify_password
from core.settings import app_settings, jwt_settings
from repository.connection import fastapi_db_dep
from repository.models import User

router = APIRouter(prefix="/auth", tags=["Auth"])


def set_auth_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=app_settings.https_enabled,
        samesite="lax",
        max_age=jwt_settings.access_token_expire_minutes * 60,
    )


@router.post(
    "/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED
)
async def signup(
    request: SignUpRequest,
    response: Response,
    db: AsyncSession = fastapi_db_dep,
) -> AuthResponse:
    # Check if user already exists
    existing_user = (
        await db.scalars(select(User).where(User.email == request.email))
    ).one_or_none()

    if existing_user:
        raise UserAlreadyExistsException()

    # Create new user
    hashed_password = get_password_hash(request.password)
    user = User(email=request.email, hashed_password=hashed_password)
    db.add(user)
    await db.flush()
    await db.refresh(user)

    # Create token and set cookie
    token = create_access_token({"sub": str(user.id)})
    set_auth_cookie(response, token)

    return AuthResponse(message="User created successfully")


@router.post("/signin", response_model=AuthResponse)
async def signin(
    request: SignInRequest,
    response: Response,
    db: AsyncSession = fastapi_db_dep,
) -> AuthResponse:
    # Find user
    user = (
        await db.scalars(select(User).where(User.email == request.email))
    ).one_or_none()

    if not user or not verify_password(request.password, user.hashed_password):
        raise InvalidCredentialsException()

    # Create token and set cookie
    token = create_access_token({"sub": str(user.id)})
    set_auth_cookie(response, token)

    return AuthResponse(message="Signed in successfully")


@router.post("/signout", response_model=AuthResponse)
async def signout(response: Response) -> AuthResponse:
    response.delete_cookie(key="access_token")
    return AuthResponse(message="Signed out successfully")
