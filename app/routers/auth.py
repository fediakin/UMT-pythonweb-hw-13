"""
Модуль маршрутизації для автентифікації користувачів.
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm
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
from app.repository import users as rep_users

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """Реєстрація нового користувача."""
    exist_user = rep_users.get_user_by_email(db, body.email)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    
    new_user = rep_users.create_user(db, body)
    background_tasks.add_task(send_email, new_user.email, str(request.base_url))
    return new_user

@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Авторизація користувача."""
    user = rep_users.get_user_by_email(db, body.username)
    if user is None or not verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")

    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    rep_users.update_token(db, user, refresh_token)
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/refresh", response_model=TokenModel)
async def refresh_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Оновлення токенів за допомогою Refresh токена."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
    user = rep_users.get_user_by_email(db, email)
    if not user or user.refresh_token != token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        
    new_access_token = create_access_token(data={"sub": user.email})
    new_refresh_token = create_refresh_token(data={"sub": user.email})
    rep_users.update_token(db, user, new_refresh_token)
    
    return {"access_token": new_access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}

@router.post("/forgot-password")
async def forgot_password(body: RequestEmail, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """Запит на скидання пароля."""
    user = rep_users.get_user_by_email(db, body.email)
    if user:
        background_tasks.add_task(send_reset_password_email, user.email, str(request.base_url))
    return {"message": "Якщо цей email зареєстровано, на нього надіслано посилання для скидання пароля."}

@router.post("/reset-password")
async def reset_password(body: ResetPassword, db: Session = Depends(get_db)):
    """Встановлення нового пароля за допомогою токена."""
    try:
        payload = jwt.decode(body.reset_password_token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
        
    user = rep_users.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
        
    user.password = get_password_hash(body.new_password)
    rep_users.update_token(db, user, None)
    
    return {"message": "Пароль успішно оновлено."}