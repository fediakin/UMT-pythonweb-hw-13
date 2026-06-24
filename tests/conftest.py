import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.services.auth import get_current_user
from app.models.user import User, Role

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def session():
    """Фікстура для створення чистої тестової бази даних."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def client(session):
    """Фікстура для тестового клієнта FastAPI із заміненою БД."""
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture(scope="module")
def test_user(session):
    """Створює тестового користувача."""
    user = User(
        email="test@example.com",
        password="hashed_password",
        confirmed=True,
        role=Role.user
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(scope="module")
def authorized_client(client, test_user):
    """Клієнт із заглушкою авторизації (без реального Redis)."""
    def override_get_current_user():
        return test_user
        
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield client
    app.dependency_overrides = {}