# apps/api/crud_olympiad.py
from typing import List, Optional
from sqlmodel import select
from shared.db.engine import get_session
from apps.api.models_olympiad import Olympiad

def create_olympiad(obj: Olympiad) -> Olympiad:
    with get_session() as session:
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

def list_olympiads(limit: int = 100) -> List[Olympiad]:
    with get_session() as session:
        stmt = select(Olympiad).limit(limit)
        return session.exec(stmt).all()

def get_olympiad(olympiad_id: int) -> Optional[Olympiad]:
    with get_session() as session:
        return session.get(Olympiad, olympiad_id)
