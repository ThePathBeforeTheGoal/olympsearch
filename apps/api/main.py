from fastapi import FastAPI
from sqlmodel import SQLModel, create_engine, Session
from shared.settings import settings

# Создаём подключение к базе
engine = create_engine(settings.DATABASE_URL, echo=True)

# Создаём все таблицы (пока их нет — просто подключение)
SQLModel.metadata.create_all(engine)

app = FastAPI(title="OlympSearch API", version="0.1.0")


@app.get("/")
async def root():
    return {"message": "OlympSearch работает через Docker + PostgreSQL!", "env": settings.ENVIRONMENT}


@app.get("/health")
async def health():
    # Простая проверка — если дошли сюда, значит база запустилась
    return {"status": "ok", "database": "connected"}