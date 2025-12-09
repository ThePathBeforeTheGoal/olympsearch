# shared/db/engine.py
from sqlmodel import SQLModel, create_engine, Session
from typing import Iterator, Optional
from sqlalchemy.engine import Engine
from contextlib import contextmanager
from shared.settings import settings

_engine: Optional[Engine] = None

def get_engine() -> Engine:
    """
    Возвращает singleton Engine.
    Низкий pool_size и max_overflow=0 — совместимость с PgBouncer/Supabase pooler в Session mode.
    """
    global _engine
    if _engine is None:
        _engine = create_engine(
            settings.DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
            # Важно: уменьшенный пул для PgBouncer в session mode
            pool_size=1,
            max_overflow=0,
        )
    return _engine

@contextmanager
def get_session() -> Iterator[Session]:
    """
    Контекстный менеджер: можно использовать как
        with get_session() as session:
            ...
    Это совместимо с текущими CRUD-утилитами.

    Если вы захотите использовать FastAPI dependency (yield-тип),
    оставим это изменение простым — большинство вызовов используют 'with'.
    """
    engine = get_engine()
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()

def init_db():
    """
    Для локальной разработки: создаёт таблицы по metadata,
    если действительно нужно (не вызывается автоматически в проде).
    """
    engine = get_engine()
    SQLModel.metadata.create_all(engine)
