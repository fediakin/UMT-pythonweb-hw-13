"""
Модуль налаштування підключення до бази даних PostgreSQL.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DB_URL", "sqlite:///./test.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Базовий клас для всіх SQLAlchemy моделей."""
    pass


def get_db():
    """
    Генератор сесій бази даних для залежностей FastAPI.
    
    :yield: Об'єкт сесії SQLAlchemy.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()