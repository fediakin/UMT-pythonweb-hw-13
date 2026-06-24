"""
Модуль маршрутизації для роботи з контактами.
"""
from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.contact import Contact
from app.models.user import User
from app.schemas.contact import ContactCreate, ContactResponse, ContactUpdate
from app.services.auth import get_current_user

router = APIRouter(prefix="/contacts", tags=["Contacts"])

@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(contact_data: ContactCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Створює новий контакт для поточного користувача.
    """
    stmt = select(Contact).where(Contact.email == contact_data.email, Contact.user_id == current_user.id)
    if db.scalars(stmt).first():
        raise HTTPException(status_code=409, detail="Contact with this email already exists")

    new_contact = Contact(**contact_data.model_dump(), user_id=current_user.id)
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact

@router.get("/", response_model=List[ContactResponse])
def get_contacts(
    first_name: str | None = Query(default=None),
    last_name: str | None = Query(default=None),
    email: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Повертає список контактів поточного користувача з можливістю фільтрації.
    """
    stmt = select(Contact).where(Contact.user_id == current_user.id)

    filters = []
    if first_name:
        filters.append(Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        filters.append(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        filters.append(Contact.email.ilike(f"%{email}%"))

    if filters:
        stmt = stmt.where(or_(*filters))

    return db.scalars(stmt).all()

@router.get("/birthdays", response_model=List[ContactResponse])
def get_upcoming_birthdays(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Повертає контакти, у яких день народження припадає на найближчі 7 днів.
    """
    stmt = select(Contact).where(Contact.user_id == current_user.id)
    all_contacts = db.scalars(stmt).all()
    today = date.today()
    upcoming = []

    for contact in all_contacts:
        try:
            bday_this_year = contact.birthday.replace(year=today.year)
        except ValueError:
            bday_this_year = date(today.year, 3, 1)

        if bday_this_year < today:
            try:
                bday_this_year = contact.birthday.replace(year=today.year + 1)
            except ValueError:
                bday_this_year = date(today.year + 1, 3, 1)

        if 0 <= (bday_this_year - today).days <= 7:
            upcoming.append(contact)

    return upcoming

@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact(contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Отримує контакт за його ID.
    """
    stmt = select(Contact).where(Contact.id == contact_id, Contact.user_id == current_user.id)
    contact = db.scalars(stmt).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(contact_id: int, contact_data: ContactUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Оновлює існуючий контакт за його ID.
    """
    stmt = select(Contact).where(Contact.id == contact_id, Contact.user_id == current_user.id)
    contact = db.scalars(stmt).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    for key, value in contact_data.model_dump().items():
        setattr(contact, key, value)

    db.commit()
    db.refresh(contact)
    return contact

@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Видаляє контакт за його ID.
    """
    stmt = select(Contact).where(Contact.id == contact_id, Contact.user_id == current_user.id)
    contact = db.scalars(stmt).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    db.delete(contact)
    db.commit()