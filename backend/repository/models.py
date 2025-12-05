from sqlalchemy.orm import Mapped, mapped_column
from repository.base_model import BaseTableModel


class User(BaseTableModel):
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str]
