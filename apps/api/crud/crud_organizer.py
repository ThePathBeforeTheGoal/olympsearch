# apps/api/crud/crud_organizer.py
from sqlmodel import select, Session  # ← ДОБАВИТЬ Session
from typing import List, Optional
from apps.api.models.organizer import Organizer
from apps.api.models_olympiad import Olympiad

# Изменить функцию, чтобы она принимала session как параметр
def list_organizers(session: Session, limit: int = 100) -> List[Organizer]:
    return session.exec(select(Organizer).limit(limit)).all()

def get_organizer_by_slug(session: Session, slug: str) -> Optional[Organizer]:
    return session.exec(select(Organizer).where(Organizer.slug == slug)).first()

def get_olympiads_for_organizer(session: Session, slug: str) -> List[Olympiad]:
    org = session.exec(select(Organizer).where(Organizer.slug == slug)).first()
    if not org:
        return []
    stmt = select(Olympiad).where(Olympiad.organizer_id == org.id, Olympiad.is_active == True)
    return session.exec(stmt).all()