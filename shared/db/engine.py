# shared/db/engine.py
from sqlmodel import SQLModel, create_engine, Session
from typing import Generator, Optional
from sqlalchemy.engine import Engine
from shared.settings import settings

_engine: Optional[Engine] = None

def get_engine() -> Engine:
    global _engine
    if _engine is None:
        # echo=False чтобы не засорять логи
        _engine = create_engine(settings.DATABASE_URL, echo=False, pool_pre_ping=True)
    return _engine

def get_session() -> Generator[Session, None, None]:
    """
    Dependency для FastAPI: yield-ная сессия SQLModel.
    FastAPI распознаёт функцию с `yield` как generator-dependency и
    корректно управляет жизненным циклом сессии.
    """
    engine = get_engine()
    with Session(engine) as session:
        yield session

def init_db():
    """
    Для MVP: создаём таблицы по metadata.
    Позже — использовать Alembic для миграций.
    """
    engine = get_engine()
    SQLModel.metadata.create_all(engine)
