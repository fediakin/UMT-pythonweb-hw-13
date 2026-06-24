"""
Схеми для контактів.
"""
from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator

class ContactBase(BaseModel):
    """Базова схема контакту."""
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    phone: str = Field(min_length=7, max_length=20)
    birthday: date
    additional_data: Optional[str] = None

    @field_validator("birthday")
    @classmethod
    def validate_age(cls, v):
        """Перевіряє, чи дата народження не є в майбутньому."""
        if v >= date.today():
            raise ValueError("Birthday must be in the past")
        return v

class ContactCreate(ContactBase):
    """Схема для створення контакту."""
    pass

class ContactUpdate(ContactBase):
    """Схема для оновлення контакту."""
    pass

class ContactResponse(ContactBase):
    """Схема відповіді для контакту."""
    id: int
    user_id: int

    model_config = {"from_attributes": True}