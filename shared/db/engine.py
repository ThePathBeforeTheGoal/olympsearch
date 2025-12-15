# shared/db/engine.py - Enhanced version for better logging and clarity
import logging
from typing import Generator
from contextlib import contextmanager
from sqlmodel import create_engine, Session  # Use sqlmodel.Session here
from sqlalchemy.orm import sessionmaker  # sessionmaker is from sqlalchemy
from shared.settings import settings

logger = logging.getLogger(__name__)

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # Set to True for local debugging
    pool_pre_ping=True,
    pool_size=5,  # Increased slightly for better concurrency; adjust based on traffic
    max_overflow=0,
)

# Specify class_=Session (from sqlmodel) to get sessions with .exec
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session,  # This is the key fix: uses sqlmodel.Session
)

def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        logger.exception(f"Database error: {e}")
        session.rollback()
        raise
    finally:
        session.close()

# Alias for FastAPI Depends compatibility
get_session_depends = get_session