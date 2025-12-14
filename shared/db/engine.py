# shared/db/engine.py - САМАЯ ПРОСТАЯ РАБОЧАЯ ВЕРСИЯ
from sqlmodel import create_engine, Session
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from typing import Iterator, Generator
from shared.settings import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=1,
    max_overflow=0,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# Алиас для совместимости
get_session_depends = get_session