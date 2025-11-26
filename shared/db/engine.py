# shared/db/engine.py
from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
from shared.settings import settings

_engine = None

def get_engine():
    global _engine
    if _engine is None:
        # echo=False в контейнере, чтобы не спамить логи
        _engine = create_engine(settings.DATABASE_URL, echo=False, pool_pre_ping=True)
    return _engine

def get_session() -> Generator[Session, None, None]:
    engine = get_engine()
    with Session(engine) as session:
        yield session

def init_db():
    """
    Для MVP: создаём таблицы по metadata.
    Позже использовать Alembic для миграций.
    """
    engine = get_engine()
    SQLModel.metadata.create_all(engine)
