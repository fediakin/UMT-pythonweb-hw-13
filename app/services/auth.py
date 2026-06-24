"""
Сервіси автентифікації та отримання поточного користувача з використанням Redis.
"""
import json
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import redis.asyncio as redis

from app.core.database import get_db
from app.core.security import SECRET_KEY, ALGORITHM
from app.models.user import User, Role

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
redis_client = redis.from_url("redis://localhost:6379/0", encoding="utf-8", decode_responses=True)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Отримує поточного користувача за JWT токеном.
    Використовує Redis для кешування даних користувача.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 1. Перевіряємо наявність користувача в Redis-кеші
    cached_user = await redis_client.get(f"user:{email}")
    if cached_user:
        user_data = json.loads(cached_user)
        # Відновлюємо об'єкт моделі з кешу
        user = User(
            id=user_data["id"], 
            email=user_data["email"], 
            avatar=user_data["avatar"], 
            confirmed=user_data["confirmed"], 
            role=Role(user_data["role"])
        )
        return user

    # 2. Якщо в кеші немає, шукаємо в базі даних
    stmt = select(User).where(User.email == email)
    user = db.scalars(stmt).first()
    
    if user is None:
        raise credentials_exception
        
    # 3. Зберігаємо користувача в Redis-кеш на 15 хвилин (900 секунд)
    user_dict = {
        "id": user.id,
        "email": user.email,
        "avatar": user.avatar,
        "confirmed": user.confirmed,
        "role": user.role.value
    }
    await redis_client.setex(f"user:{email}", 900, json.dumps(user_dict))
    
    return user