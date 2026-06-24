"""
Головний модуль додатку FastAPI.
Тут налаштовуються CORS, підключення до Redis, та реєструються всі роутери.
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from dotenv import load_dotenv

from app.core.database import engine, Base
from app.routers import auth, users, contacts

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекстний менеджер життєвого циклу додатку.
    Створює таблиці в базі даних та ініціалізує Redis для Rate Limiting.
    """
    Base.metadata.create_all(bind=engine)
    
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    r = await redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(r)
    
    yield

app = FastAPI(
    title="Contacts REST API",
    description="Фінальне домашнє завдання 13: Sphinx, Pytest, Redis, Roles",
    version="1.2.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(contacts.router)

@app.get("/")
def read_root():
    """
    Кореневий ендпоінт перевірки працездатності API.
    """
    return {"message": "Welcome to Contacts API! Visit /docs for Swagger UI"}