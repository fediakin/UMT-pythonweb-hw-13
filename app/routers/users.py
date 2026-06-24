"""
Модуль маршрутизації для роботи з поточним користувачем та ролями.
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from fastapi_limiter.depends import RateLimiter

from app.core.database import get_db
from app.models.user import User, Role
from app.schemas.user import UserResponse
from app.services.auth import get_current_user
from app.services.avatar import upload_avatar

router = APIRouter(prefix="/users", tags=["Users"])


class RoleChecker:
    """Клас-залежність для перевірки ролей користувача."""
    def __init__(self, allowed_roles: list[Role]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="У вас немає прав для виконання цієї операції."
            )
        return user


@router.get("/me", response_model=UserResponse, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Отримує дані поточного авторизованого користувача.
    Встановлено обмеження: 5 запитів на хвилину.
    """
    return current_user


# Змінювати аватар може ТІЛЬКИ адміністратор (Role.admin)
@router.patch("/avatar", response_model=UserResponse)
async def update_avatar(
    file: UploadFile = File(...), 
    current_user: User = Depends(RoleChecker([Role.admin])),
    db: Session = Depends(get_db)
):
    """
    Оновлює аватар користувача (Доступно лише для адміністраторів).

    :param file: Файл зображення.
    :param current_user: Поточний користувач (адміністратор).
    :param db: Сесія бази даних.
    :return: Оновлений об'єкт користувача.
    """
    public_id = f"contacts_app/{current_user.email}"
    avatar_url = upload_avatar(file, public_id)
    
    current_user.avatar = avatar_url
    db.commit()
    db.refresh(current_user)
    
    # Не забуваємо оновити дані і в Redis-кеші!
    from app.services.auth import redis_client
    import json
    user_dict = {
        "id": current_user.id,
        "email": current_user.email,
        "avatar": current_user.avatar,
        "confirmed": current_user.confirmed,
        "role": current_user.role.value
    }
    await redis_client.setex(f"user:{current_user.email}", 900, json.dumps(user_dict))
    
    return current_user