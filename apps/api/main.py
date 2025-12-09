# apps/api/main.py
import logging
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from sqlmodel import SQLModel, create_engine
from shared.settings import settings

logger = logging.getLogger("uvicorn.error")

# Импорты моделей (порядок важен)
import apps.api.models.subscription      # Plan
import apps.api.models_olympiad         # Olympiad
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

# === Не вызываем create_all на этапе импорта ===
# (Если вам нужно в dev создать таблицы автоматически — используйте init_db() ниже)
engine = create_engine(settings.DATABASE_URL, echo=False)

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

# Если origin == ["*"], нельзя одновременно включать credentials в безопасном режиме браузера.
allow_credentials = False if allow_origins == ["*"] else True

logger.info("CORS allow_origins: %s allow_credentials: %s", allow_origins, allow_credentials)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
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

# === Запуск для Render / локали ===
def _maybe_init_db():
    # Включите INIT_DB=true в env, если хотите, чтобы при старте создавались таблицы (dev only)
    if os.getenv("INIT_DB", "").lower() in ("1", "true", "yes"):
        logger.info("INIT_DB set — creating database tables (SQLModel.metadata.create_all)...")
        SQLModel.metadata.create_all(engine)

if __name__ == "__main__":
    _maybe_init_db()
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
