"""
Модуль моделі Користувача.
"""
import enum
from sqlalchemy import String, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class Role(enum.Enum):
    """Перелік можливих ролей користувача в системі."""
    admin = "admin"
    user = "user"


class User(Base):
    """SQLAlchemy модель для таблиці користувачів."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar: Mapped[str | None] = mapped_column(String(255), nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.user)
    refresh_token: Mapped[str | None] = mapped_column(String(255), nullable=True)