# shared/db/engine.py - САМАЯ ПРОСТАЯ РАБОЧАЯ ВЕРСИЯ
from sqlmodel import create_engine, Session
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from typing import Iterator
from shared.settings import settings

# Создаем движок
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=1,
    max_overflow=0,
)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ОДНА универсальная функция
@contextmanager
def get_session() -> Iterator[Session]:
    """
    Работает и как контекстный менеджер (with get_session() as session:)
    и как генератор для Depends (через @contextmanager декоратор)
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()