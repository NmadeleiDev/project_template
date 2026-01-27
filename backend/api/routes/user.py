from fastapi import APIRouter

from api.dependencies import current_user_dep
from api.schemas import UserResponse
from repository.models import User

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: current_user_dep,
) -> UserResponse:
    """
    Get current authenticated user information.

    Returns the profile information for the currently authenticated user
    based on the JWT token provided in the request cookie.

    Args:
        current_user: Current authenticated user (injected from JWT token)

    Returns:
        UserResponse: User profile with id, email, and created_at

    Raises:
        NotAuthenticatedException (40102): No valid JWT token provided
        InvalidTokenException (40103): JWT token is invalid
        TokenExpiredException (40104): JWT token has expired
        UserNotFoundException (40105): User from token not found in database
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        created_at=current_user.created_at,
    )
