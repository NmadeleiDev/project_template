from fastapi import APIRouter

from api.dependencies import current_user_dep
from api.schemas import UserResponse
from repository.models import User

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: current_user_dep,
) -> UserResponse:
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        created_at=current_user.created_at,
    )
