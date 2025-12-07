# apps/api/crud/crud_organizer.py
from sqlmodel import select
from typing import List, Optional
from shared.db.engine import get_session
from apps.api.models.organizer import Organizer
from apps.api.models_olympiad import Olympiad

def list_organizers(limit: int = 100) -> List[Organizer]:
    with get_session() as session:
        return session.exec(select(Organizer).limit(limit)).all()

def get_organizer_by_slug(slug: str) -> Optional[Organizer]:
    with get_session() as session:
        return session.exec(select(Organizer).where(Organizer.slug == slug)).first()

def get_olympiads_for_organizer(slug: str) -> List[Olympiad]:
    with get_session() as session:
        org = session.exec(select(Organizer).where(Organizer.slug == slug)).first()
        if not org:
            return []
        stmt = select(Olympiad).where(Olympiad.organizer_id == org.id, Olympiad.is_active == True)
        return session.exec(stmt).all()
