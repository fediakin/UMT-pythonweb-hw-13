"""
Модуль для роботи з базою даних для користувачів (Repository Pattern).
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserModel
from app.core.security import get_password_hash

def get_user_by_email(db: Session, email: str) -> User | None:
    """Отримує користувача за його email."""
    stmt = select(User).where(User.email == email)
    return db.scalars(stmt).first()

def create_user(db: Session, body: UserModel) -> User:
    """Створює нового користувача з хешуванням пароля."""
    new_user = User(email=body.email, password=get_password_hash(body.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def update_token(db: Session, user: User, token: str | None) -> None:
    """Оновлює або видаляє refresh_token користувача."""
    user.refresh_token = token
    db.commit()

def confirm_email(db: Session, email: str) -> None:
    """Позначає email користувача як підтверджений."""
    user = get_user_by_email(db, email)
    if user:
        user.confirmed = True
        db.commit()

def update_avatar(db: Session, email: str, url: str) -> User:
    """Оновлює URL аватара користувача."""
    user = get_user_by_email(db, email)
    user.avatar = url
    db.commit()
    db.refresh(user)
    return user