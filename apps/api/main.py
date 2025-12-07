# apps/api/main.py
import os
from fastapi import FastAPI
from sqlmodel import SQLModel, create_engine
from shared.settings import settings
from apps.api.routers import olympiads
from fastapi.middleware.cors import CORSMiddleware
# apps/api/main.py — добавь эти импорты
import apps.api.models_olympiad
import apps.api.models.category
import apps.api.models.organizer
import apps.api.models.subscription
import apps.api.models.favorite
import apps.api.models.reminder
# В main.py добавь:
# Роутеры
from apps.api.routers import (
    olympiads,
    categories,
    favorites,
    reminders,
    webhooks,
    subscriptions,
    organizers,
)

# Создаём подключение к базе
engine = create_engine(settings.DATABASE_URL, echo=True)

# Создаём все таблицы (если их ещё нет)
SQLModel.metadata.create_all(engine)

app = FastAPI(
    title="OlympSearch API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# === CORS ===
_allowed = os.getenv("ALLOWED_ORIGINS", "").strip()
if _allowed:
    allow_origins = [s.strip() for s in _allowed.split(",") if s.strip()]
else:
    # Дефолт для локальной разработки
    allow_origins = [
        "http://localhost:3000",
        "https://olympsearch-frontend.vercel.app",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,  # ← ИСПРАВЛЕНО: используем переменную окружения
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Роутеры ===
app.include_router(olympiads.router)
app.include_router(categories.router)
app.include_router(favorites.router)
app.include_router(reminders.router)
app.include_router(webhooks.router)
app.include_router(subscriptions.router)
app.include_router(organizers.router)

# === Корневые эндпоинты ===
@app.get("/")
async def root():
    return {
        "message": "OlympSearch API — работает!",
        "version": "1.0.0",
        "env": settings.ENVIRONMENT,
    }

@app.get("/health")
async def health():
    return {"status": "ok", "database": "connected"}