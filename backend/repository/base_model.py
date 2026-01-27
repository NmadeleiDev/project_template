"""
Base model for all database tables.

This module provides the base SQLAlchemy model that all other models inherit from.
It includes common fields (id, created_at) and utility methods for CRUD operations.

Features:
    - Auto-generated UUID primary key
    - Created timestamp
    - Automatic table name generation (PascalCase → snake_case)
    - Async-compatible model attributes
    - Helper methods for create and update operations
"""

import logging
import uuid
from datetime import datetime
from typing import Self

from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
)
from sqlalchemy.orm.attributes import QueryableAttribute


class BaseTableModel(DeclarativeBase, AsyncAttrs):
    """
    Base model for all database tables.

    All SQLAlchemy models should inherit from this class to get common fields
    and functionality.

    Attributes:
        id: UUID primary key (auto-generated)
        created_at: Timestamp of record creation (auto-generated)

    Features:
        - Automatic table name generation from class name
        - Async-compatible attributes via AsyncAttrs
        - Helper methods for creating and updating records
        - Automatic timestamp tracking

    Example:
        class User(BaseTableModel):
            email: Mapped[str] = mapped_column(unique=True)

        # Table name automatically becomes "user"
        # Includes id and created_at fields
    """

    id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, primary_key=True)
    """UUID primary key (automatically generated)."""

    created_at: Mapped[datetime] = mapped_column(insert_default=func.now())
    """Timestamp of record creation (automatically set on insert)."""

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Generate table name from class name.

        Automatically converts PascalCase class name to snake_case table name.

        Example:
            User → user
            BlogPost → blog_post
            UserProfile → user_profile

        Returns:
            snake_case table name
        """
        import re

        # Convert PascalCase to snake_case
        name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", cls.__name__)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()

    @classmethod
    async def post(
        cls,
        session: AsyncSession,
        value: BaseModel,
        **kwargs,
    ) -> Self | None:
        """
        Create new database record from Pydantic model.

        Convenience method to create a model instance from a Pydantic schema,
        automatically filtering to only valid model fields and handling
        database constraints.

        Args:
            session: Async database session
            value: Pydantic model containing data to insert
            **kwargs: Additional fields to override or supplement

        Returns:
            Created model instance if successful, None if constraint violated

        Note:
            - Automatically commits to database
            - Rolls back on IntegrityError (e.g., unique constraint violation)
            - Refreshes instance to get database-generated values
            - Filters out Pydantic fields that don't exist on SQLAlchemy model

        Example:
            from api.schemas import CreateUserRequest

            user_data = CreateUserRequest(email="test@example.com")
            user = await User.post(session, user_data)
            if user:
                print(f"Created user: {user.id}")
            else:
                print("User creation failed (possibly duplicate email)")

        TODO:
            Introduce typing with TypedDict for better type safety
            https://github.com/pydantic/pydantic/discussions/8093
        """
        # Filter to only valid model fields
        filtered_fields = {
            field_name: field_value
            for field_name, field_value in {**value.model_dump(), **kwargs}.items()
            if hasattr(cls, field_name)
            and isinstance(inspect(getattr(cls, field_name, None)), QueryableAttribute)
        }

        # Create model instance
        obj = cls(**filtered_fields)
        session.add(obj)

        try:
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            logging.exception(exc)
            return None

        await session.refresh(obj)
        return obj

    async def patch(
        self,
        session: AsyncSession,
        new_value: BaseModel,
    ) -> Self:
        """
        Update existing database record from Pydantic model.

        Convenience method to update a model instance with data from a Pydantic
        schema, only updating fields that were explicitly set (partial update).

        Args:
            session: Async database session
            new_value: Pydantic model containing fields to update

        Returns:
            Updated model instance (self)

        Note:
            - Only updates fields that were explicitly set (uses exclude_unset=True)
            - Automatically commits to database
            - Refreshes instance to get any database-triggered updates
            - Ignores Pydantic fields that don't exist on SQLAlchemy model
            - Returns self unchanged if no fields to update

        Example:
            from api.schemas import UpdateUserRequest

            user = await get_user(session, user_id)
            update_data = UpdateUserRequest(email="newemail@example.com")
            updated_user = await user.patch(session, update_data)
            print(f"Updated email: {updated_user.email}")

            # Only email was updated, other fields remain unchanged
            # If update_data had no fields set, user returned unchanged

        Usage in service layer:
            async def update_user(self, user_id: str, updates: UpdateUserRequest):
                user = await self.get_user_by_id(user_id)
                if not user:
                    raise UserNotFoundException()
                return await user.patch(self.db, updates)
        """
        # Get only fields that were explicitly set
        new_value_items = new_value.model_dump(exclude_unset=True).items()

        # No fields to update, return unchanged
        if not new_value_items:
            return self

        cls = type(self)

        # Update only valid model attributes
        for field_name, field_value in new_value_items:
            attribute = getattr(cls, field_name, None)
            if not attribute or not isinstance(inspect(attribute), QueryableAttribute):
                continue
            setattr(self, field_name, field_value)

        # Commit changes
        session.add(self)
        await session.commit()
        await session.refresh(self)

        return self
