"""
Модуль маршрутизації для роботи з контактами.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.contact import ContactCreate, ContactResponse, ContactUpdate
from app.services.auth import get_current_user
from app.repository import contacts as rep_contacts

router = APIRouter(prefix="/contacts", tags=["Contacts"])

@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(contact_data: ContactCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Створює новий контакт для поточного користувача."""
    contact = rep_contacts.get_contact_by_email(db, contact_data.email, current_user)
    if contact:
        raise HTTPException(status_code=409, detail="Contact with this email already exists")
    return rep_contacts.create_contact(db, contact_data, current_user)

@router.get("/", response_model=List[ContactResponse])
def get_contacts(
    first_name: str | None = Query(default=None),
    last_name: str | None = Query(default=None),
    email: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Повертає список контактів поточного користувача з можливістю фільтрації."""
    return rep_contacts.get_contacts(db, current_user, first_name, last_name, email)

@router.get("/birthdays", response_model=List[ContactResponse])
def get_upcoming_birthdays(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Повертає контакти, у яких день народження припадає на найближчі 7 днів."""
    return rep_contacts.get_upcoming_birthdays(db, current_user)

@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact(contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Отримує контакт за його ID."""
    contact = rep_contacts.get_contact_by_id(db, contact_id, current_user)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(contact_id: int, contact_data: ContactUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Оновлює існуючий контакт за його ID."""
    contact = rep_contacts.update_contact(db, contact_id, contact_data, current_user)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Видаляє контакт за його ID."""
    contact = rep_contacts.remove_contact(db, contact_id, current_user)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact