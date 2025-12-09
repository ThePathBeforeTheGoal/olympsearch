# apps/api/main.py — РАБОЧИЙ ПОД ТВОЮ СТРУКТУРУ
import logging
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from sqlmodel import SQLModel, create_engine
from shared.settings import settings

# ВАЖНО: ПРАВИЛЬНЫЙ ПОРЯДОК ДЛЯ ТВОИХ ФАЙЛОВ
# 1. Сначала subscription — там Plan
# 2. Потом models_olympiad — там Olympiad
# 3. Потом всё остальное
logger = logging.getLogger("uvicorn.error")
import apps.api.models.subscription      # ← ПЕРВЕРХ! Содержит Plan
import apps.api.models_olympiad         # ← ВТОРОЙ! Содержит Olympiad
import apps.api.models.category
import apps.api.models.organizer
import apps.api.models.favorite
import apps.api.models.reminder

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

# === База ===
engine = create_engine(settings.DATABASE_URL, echo=False)
SQLModel.metadata.create_all(engine)

# === Приложение ===
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
    allow_origins = ["*"]  # временно — разрешить все источники для отладки

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
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

# === Запуск для Render ===
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))
    uvicorn.run("apps.api.main:app", host="0.0.0.0", port=port, log_level="info")

# === Эндпоинты ===
@app.get("/")
async def root():
    return {"message": "OlympSearch API — работает!", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "ok", "database": "connected"}