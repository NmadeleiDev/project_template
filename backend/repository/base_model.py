import uuid
from sqlalchemy import func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
)
from datetime import datetime
from typing import Self
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.attributes import QueryableAttribute
import logging


class BaseTableModel(DeclarativeBase, AsyncAttrs):
    id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(insert_default=func.now())

    @declared_attr.directive
    def __tablename__(cls) -> str:
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
        TODO: Introduce typing with TypedDict
        https://github.com/pydantic/pydantic/discussions/8093
        """

        filtered_fields = {
            field_name: field_value
            for field_name, field_value in {**value.model_dump(), **kwargs}.items()
            if hasattr(cls, field_name)
            and isinstance(inspect(getattr(cls, field_name, None)), QueryableAttribute)
        }
        obj = cls(
            **filtered_fields,
        )
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
    ):
        new_value_items = new_value.model_dump(exclude_unset=True).items()
        if not new_value_items:
            return self

        cls = type(self)

        for field_name, field_value in new_value_items:
            attribute = getattr(cls, field_name, None)
            if not attribute or not isinstance(inspect(attribute), QueryableAttribute):
                continue
            setattr(self, field_name, field_value)

        session.add(self)
        await session.commit()
        await session.refresh(self)

        return self
