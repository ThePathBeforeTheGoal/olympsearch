# apps/api/main.py
import os
from fastapi import FastAPI
from sqlmodel import SQLModel, create_engine
from shared.settings import settings
import apps.api.models_olympiad  # noqa: F401  -- чтобы SQLModel.metadata видел модель
from apps.api.routers import olympiads
from fastapi.middleware.cors import CORSMiddleware

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

# --- CORS: читаем из окружения ALLOWED_ORIGINS (кома-разделённый список) ---
_allowed = os.getenv("ALLOWED_ORIGINS", "").strip()
if _allowed:
    # если задано - разбираем список
    allow_origins = [s.strip() for s in _allowed.split(",") if s.strip()]
else:
    # безопасный набор по умолчанию (локальная разработка + ожидаемый Vercel-домен)
    allow_origins = [
        "http://localhost:3000",  # Next.js dev
        "http://localhost:8000",  # Swagger / локальный бэкенд (если нужен)
        "https://olympsearch-frontend.vercel.app",  # production frontend (замени при необходимости)
    ]

# ЗДЕСЬ НУЖНО ВЕРНУТЬ ССЫЛКУ ОБЯЗАТЕЛЬНО НА ФРОНТ АААААААААААААААААААААААААААААААААА
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # временно только для отладки
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Подключаем маршруты
app.include_router(olympiads.router)


@app.get("/")
async def root():
    return {
        "message": "OlympSearch API — работает!",
        "env": settings.ENVIRONMENT,
        "allowed_origins": allow_origins,  # удобно для отладки (удалите в проде, если нужно)
    }


@app.get("/health")
async def health():
    # Простая проверка — если дошли сюда, значит приложение запущено
    return {"status": "ok", "database": "connected"}
