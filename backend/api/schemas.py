import uuid
from datetime import datetime

from api.base_schema import BaseSchema


# Auth schemas
class SignUpRequest(BaseSchema):
    email: str
    password: str


class SignInRequest(BaseSchema):
    email: str
    password: str


class AuthResponse(BaseSchema):
    message: str


# User schemas
class UserResponse(BaseSchema):
    id: uuid.UUID
    email: str
    created_at: datetime
