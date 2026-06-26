"""
Модуль маршрутизації для роботи з поточним користувачем та ролями.
"""
import json
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from fastapi_limiter.depends import RateLimiter

from app.core.database import get_db
from app.models.user import User, Role
from app.schemas.user import UserResponse
from app.services.auth import get_current_user, redis_client
from app.services.avatar import upload_avatar
from app.repository import users as rep_users

router = APIRouter(prefix="/users", tags=["Users"])

class RoleChecker:
    """Клас-залежність для перевірки ролей користувача."""
    def __init__(self, allowed_roles: list[Role]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="У вас немає прав.")
        return user

@router.get("/me", response_model=UserResponse, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Отримує дані поточного авторизованого користувача."""
    return current_user

@router.patch("/avatar", response_model=UserResponse)
async def update_avatar(file: UploadFile = File(...), current_user: User = Depends(RoleChecker([Role.admin])), db: Session = Depends(get_db)):
    """Оновлює аватар користувача (Доступно лише для адміністраторів)."""
    public_id = f"contacts_app/{current_user.email}"
    avatar_url = upload_avatar(file, public_id)
    
    user = rep_users.update_avatar(db, current_user.email, avatar_url)
    
    user_dict = {
        "id": user.id, "email": user.email, "avatar": user.avatar,
        "confirmed": user.confirmed, "role": user.role.value
    }
    await redis_client.setex(f"user:{user.email}", 900, json.dumps(user_dict))
    return user