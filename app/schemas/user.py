"""
Схеми для користувачів.
"""
from pydantic import BaseModel, EmailStr
from app.models.user import Role

class UserModel(BaseModel):
    """Схема для реєстрації та логіну."""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """Схема відповіді з даними користувача."""
    id: int
    email: EmailStr
    avatar: str | None
    confirmed: bool
    role: Role

    model_config = {"from_attributes": True}

class TokenModel(BaseModel):
    """Схема для токенів доступу (Access та Refresh)."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RequestEmail(BaseModel):
    """Схема для запиту електронної пошти (наприклад, для скидання пароля)."""
    email: EmailStr

class ResetPassword(BaseModel):
    """Схема для встановлення нового пароля."""
    reset_password_token: str
    new_password: str