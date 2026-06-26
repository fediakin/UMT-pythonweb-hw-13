"""
Модуль для роботи з базою даних для контактів (Repository Pattern).
"""
from datetime import date
from typing import List
from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from app.models.contact import Contact
from app.models.user import User
from app.schemas.contact import ContactCreate, ContactUpdate


def get_contacts(db: Session, user: User, first_name: str | None = None, last_name: str | None = None, email: str | None = None) -> List[Contact]:
    """Отримує список контактів з бази даних із можливістю фільтрації."""
    stmt = select(Contact).where(Contact.user_id == user.id)
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


def get_contact_by_id(db: Session, contact_id: int, user: User) -> Contact | None:
    """Отримує конкретний контакт за ID."""
    stmt = select(Contact).where(Contact.id == contact_id, Contact.user_id == user.id)
    return db.scalars(stmt).first()


def get_contact_by_email(db: Session, email: str, user: User) -> Contact | None:
    """Отримує контакт за email (для перевірки дублікатів)."""
    stmt = select(Contact).where(Contact.email == email, Contact.user_id == user.id)
    return db.scalars(stmt).first()


def create_contact(db: Session, body: ContactCreate, user: User) -> Contact:
    """Створює новий контакт у базі даних."""
    contact = Contact(**body.model_dump(), user_id=user.id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


def update_contact(db: Session, contact_id: int, body: ContactUpdate, user: User) -> Contact | None:
    """Оновлює існуючий контакт."""
    contact = get_contact_by_id(db, contact_id, user)
    if contact:
        for key, value in body.model_dump().items():
            setattr(contact, key, value)
        db.commit()
        db.refresh(contact)
    return contact


def remove_contact(db: Session, contact_id: int, user: User) -> Contact | None:
    """Видаляє контакт з бази даних."""
    contact = get_contact_by_id(db, contact_id, user)
    if contact:
        db.delete(contact)
        db.commit()
    return contact


def get_upcoming_birthdays(db: Session, user: User) -> List[Contact]:
    """Шукає контакти, у яких день народження в найближчі 7 днів."""
    stmt = select(Contact).where(Contact.user_id == user.id)
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