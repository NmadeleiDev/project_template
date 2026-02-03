"""
Authentication service.

Handles user authentication business logic including signup, signin,
and credential validation.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from service.exceptions import InvalidCredentialsException, UserAlreadyExistsException
from service.security import create_access_token, get_password_hash, verify_password
from repository.models import User
from service.base_service import BaseService


class AuthService(BaseService):
    """
    Authentication service.

    Provides business logic for user authentication operations.
    All methods are async to prevent blocking the event loop.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize auth service.

        Args:
            db: Async database session
        """
        super().__init__(db)

    async def signup_user(self, email: str, password: str) -> tuple[User, str]:
        """
        Register a new user account.

        Business logic:
        1. Check if email is already registered
        2. Hash password using Argon2
        3. Create user record in database
        4. Generate JWT access token

        Args:
            email: User email address (must be unique)
            password: Plain text password (will be hashed)

        Returns:
            Tuple of (User model, JWT token string)

        Raises:
            UserAlreadyExistsException: If email is already registered
        """
        # Check if user already exists
        existing_user = (
            await self.db.scalars(select(User).where(User.email == email))
        ).one_or_none()

        if existing_user:
            raise UserAlreadyExistsException()

        # Hash password - this is CPU-intensive but runs in thread pool
        hashed_password = get_password_hash(password)

        # Create new user
        user = User(email=email, hashed_password=hashed_password)
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)

        # Generate JWT token
        token = create_access_token({"sub": str(user.id)})

        return user, token

    async def signin_user(self, email: str, password: str) -> tuple[User, str]:
        """
        Authenticate existing user.

        Business logic:
        1. Find user by email
        2. Verify password hash
        3. Generate JWT access token

        Args:
            email: User email address
            password: Plain text password to verify

        Returns:
            Tuple of (User model, JWT token string)

        Raises:
            InvalidCredentialsException: If email not found or password incorrect
        """
        # Find user by email
        user = (
            await self.db.scalars(select(User).where(User.email == email))
        ).one_or_none()

        # Verify user exists and password is correct
        # Password verification is CPU-intensive but runs in thread pool
        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsException()

        # Generate JWT token
        token = create_access_token({"sub": str(user.id)})

        return user, token

    async def get_user_by_id(self, user_id: str) -> User | None:
        """
        Find user by UUID.

        Args:
            user_id: User UUID as string

        Returns:
            User model if found, None otherwise
        """
        result = await self.db.scalars(select(User).where(User.id == user_id))
        return result.one_or_none()
