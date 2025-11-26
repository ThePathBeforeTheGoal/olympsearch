# shared/db/engine.py
from sqlmodel import SQLModel, create_engine, Session
from typing import Generator, Iterator
from shared.settings import settings
from contextlib import contextmanager

_engine = None

def get_engine():
    global _engine
    if _engine is None:
        # echo=False чтобы не засорять логи
        _engine = create_engine(settings.DATABASE_URL, echo=False, pool_pre_ping=True)
    return _engine

@contextmanager
def get_session() -> Iterator[Session]:
    """
    Контекстный менеджер для сессий SQLAlchemy / SQLModel.
    Использование:
        with get_session() as session:
            ...
    """
    engine = get_engine()
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()

def init_db():
    """
    Для MVP: создаём таблицы по metadata.
    Позже использовать Alembic для миграций.
    """
    engine = get_engine()
    SQLModel.metadata.create_all(engine)
