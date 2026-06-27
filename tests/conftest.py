"""
Конфігурація тестового середовища (Mocks та SQLite in-memory).
"""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# 1. СТРОГО ДО ІМПОРТУ ДОДАТКУ: Мокаємо всі зовнішні сервіси!
# Це гарантує, що тести не впадуть, якщо Docker, Redis або Cloudinary вимкнені.
patch("fastapi_limiter.FastAPILimiter.init", new_callable=AsyncMock).start()
patch("app.services.auth.redis_client.get", new_callable=AsyncMock).start()
patch("app.services.auth.redis_client.setex", new_callable=AsyncMock).start()
patch("app.routers.users.redis_client.setex", new_callable=AsyncMock).start()
patch("app.services.email.FastMail.send_message", new_callable=AsyncMock).start()
patch("app.routers.users.upload_avatar", return_value="http://fake-avatar.com/image.jpg").start()

from app.main import app
from app.core.database import Base, get_db
from app.models.user import User, Role
from app.services.auth import get_current_user

# 2. Налаштування ізольованої бази даних. StaticPool зберігає дані між запитами.
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)

@pytest.fixture(scope="module")
def test_user(session):
    from app.core.security import get_password_hash
    user = User(
        email="test@example.com",
        password=get_password_hash("password123"),
        confirmed=True,
        role=Role.user
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@pytest.fixture(scope="module")
def authorized_client(client, test_user):
    def override_get_current_user():
        return test_user
        
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield client
    app.dependency_overrides = {}