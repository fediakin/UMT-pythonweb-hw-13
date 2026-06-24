"""
Модуль маршрутизації для автентифікації користувачів.
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.core.database import get_db
from app.core.security import (
    get_password_hash, verify_password, create_access_token, 
    create_refresh_token, SECRET_KEY, ALGORITHM
)
from app.models.user import User
from app.schemas.user import UserModel, UserResponse, TokenModel, RequestEmail, ResetPassword
from app.services.email import send_email, send_reset_password_email
from app.services.auth import oauth2_scheme

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    Реєстрація нового користувача.

    :param body: Дані користувача (email, пароль).
    :param background_tasks: Фонове завдання для відправки листа.
    :param request: Об'єкт запиту для формування посилання.
    :param db: Сесія бази даних.
    :return: Створений користувач.
    """
    stmt = select(User).where(User.email == body.email)
    exist_user = db.scalars(stmt).first()
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    
    new_user = User(email=body.email, password=get_password_hash(body.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    background_tasks.add_task(send_email, new_user.email, str(request.base_url))
    return new_user


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Авторизація користувача (отримання Access та Refresh токенів).

    :param body: Форма з email та паролем.
    :param db: Сесія бази даних.
    :return: Словник з токенами.
    """
    stmt = select(User).where(User.email == body.username)
    user = db.scalars(stmt).first()
    if user is None or not verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")

    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    # Зберігаємо рефреш токен у базі даних
    user.refresh_token = refresh_token
    db.commit()
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh", response_model=TokenModel)
async def refresh_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Оновлення токенів за допомогою Refresh токена.

    :param token: Поточний Refresh токен.
    :param db: Сесія бази даних.
    :return: Нові Access та Refresh токени.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
    stmt = select(User).where(User.email == email)
    user = db.scalars(stmt).first()
    if not user or user.refresh_token != token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        
    new_access_token = create_access_token(data={"sub": user.email})
    new_refresh_token = create_refresh_token(data={"sub": user.email})
    user.refresh_token = new_refresh_token
    db.commit()
    
    return {"access_token": new_access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}


@router.post("/forgot-password")
async def forgot_password(body: RequestEmail, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    Запит на скидання пароля (відправка листа з токеном).
    """
    stmt = select(User).where(User.email == body.email)
    user = db.scalars(stmt).first()
    if user:
        background_tasks.add_task(send_reset_password_email, user.email, str(request.base_url))
    # Повертаємо успіх навіть якщо email не знайдено (з міркувань безпеки)
    return {"message": "Якщо цей email зареєстровано, на нього надіслано посилання для скидання пароля."}


@router.post("/reset-password")
async def reset_password(body: ResetPassword, db: Session = Depends(get_db)):
    """
    Встановлення нового пароля за допомогою токена.
    """
    try:
        payload = jwt.decode(body.reset_password_token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
        
    stmt = select(User).where(User.email == email)
    user = db.scalars(stmt).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
        
    user.password = get_password_hash(body.new_password)
    user.refresh_token = None # Анулюємо старі сесії
    db.commit()
    
    return {"message": "Пароль успішно оновлено."}