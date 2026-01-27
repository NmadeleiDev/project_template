from fastapi import APIRouter, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import AuthResponse, SignInRequest, SignUpRequest
from core.settings import app_settings, jwt_settings
from repository.connection import fastapi_db_dep
from service.auth_service import AuthService

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
    """
    Register a new user account.

    Creates a new user with email and password, then returns a JWT token
    in an HTTP-only cookie for subsequent authenticated requests.

    Args:
        request: Signup request with email and password
        response: FastAPI response object for setting cookies
        db: Database session (injected)

    Returns:
        AuthResponse: Success message

    Raises:
        UserAlreadyExistsException (40001): Email already registered
    """
    # Delegate to service layer
    auth_service = AuthService(db)
    user, token = await auth_service.signup_user(request.email, request.password)

    # Set authentication cookie
    set_auth_cookie(response, token)

    return AuthResponse(message="User created successfully")


@router.post("/signin", response_model=AuthResponse)
async def signin(
    request: SignInRequest,
    response: Response,
    db: AsyncSession = fastapi_db_dep,
) -> AuthResponse:
    """
    Authenticate user and create session.

    Validates user credentials and returns a JWT token in an HTTP-only
    cookie for subsequent authenticated requests.

    Args:
        request: Signin request with email and password
        response: FastAPI response object for setting cookies
        db: Database session (injected)

    Returns:
        AuthResponse: Success message

    Raises:
        InvalidCredentialsException (40101): Invalid email or password
    """
    # Delegate to service layer
    auth_service = AuthService(db)
    user, token = await auth_service.signin_user(request.email, request.password)

    # Set authentication cookie
    set_auth_cookie(response, token)

    return AuthResponse(message="Signed in successfully")


@router.post("/signout", response_model=AuthResponse)
async def signout(response: Response) -> AuthResponse:
    """
    Sign out current user.

    Clears the JWT authentication cookie, effectively logging out the user.

    Args:
        response: FastAPI response object for clearing cookies

    Returns:
        AuthResponse: Success message
    """
    response.delete_cookie(key="access_token")
    return AuthResponse(message="Signed out successfully")
