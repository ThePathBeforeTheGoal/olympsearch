# apps/api/crud_olympiad.py
from typing import List, Optional
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from shared.db.engine import get_session
from apps.api.models_olympiad import Olympiad
import re
import unicodedata
from datetime import datetime, timedelta
from sqlalchemy import or_, desc, asc

def slugify(value: str, max_length: int = 100) -> str:
    if not value:
        return ""
    value = unicodedata.normalize("NFKC", value)
    value = re.sub(r"[^\w\s-]", "", value, flags=re.U).strip().lower()
    value = re.sub(r"[-\s]+", "-", value)
    return value[:max_length].strip("-")


def _ensure_unique_slug(session, base_slug: str, max_attempts: int = 100) -> str:
    slug = base_slug
    i = 1
    while i < max_attempts:
        stmt = select(Olympiad).where(Olympiad.slug == slug)
        if not session.exec(stmt).first():
            return slug
        slug = f"{base_slug}-{i}"
        i += 1
    raise RuntimeError("Can't generate unique slug")


def create_olympiad(obj: Olympiad) -> Olympiad:
    with get_session() as session:
        # Дедупликация по content_hash
        if obj.content_hash:
            existing = session.exec(
                select(Olympiad).where(Olympiad.content_hash == obj.content_hash)
            ).first()
            if existing:
                return existing

        # Автогенерация slug, если не указан
        if not obj.slug:
            base = slugify(obj.title or "olympiad")
            obj.slug = base or "olympiad"

        # Уникальность
        obj.slug = _ensure_unique_slug(session, obj.slug)

        # Вставка
        try:
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj
        except IntegrityError:
            session.rollback()
            # На случай гонки — ищем по hash ещё раз
            if obj.content_hash:
                existing = session.exec(
                    select(Olympiad).where(Olympiad.content_hash == obj.content_hash)
                ).first()
                if existing:
                    return existing
            raise


# ←←←← Обязательные базовые функции
def list_olympiads(limit: int = 100) -> List[Olympiad]:
    with get_session() as session:
        stmt = select(Olympiad).limit(limit)
        return session.exec(stmt).all()


def get_olympiad(olympiad_id: int) -> Optional[Olympiad]:
    with get_session() as session:
        return session.get(Olympiad, olympiad_id)


# --- Новые функции ---
def list_olympiads_by_category(category: str) -> List[Olympiad]:
    with get_session() as session:
        stmt = select(Olympiad).where(Olympiad.category == category)
        return session.exec(stmt).all()


def search_olympiads(q: str) -> List[Olympiad]:
    with get_session() as session:
        stmt = select(Olympiad).where(Olympiad.title.ilike(f"%{q}%"))
        return session.exec(stmt).all()


def filter_olympiads(
    category: Optional[str] = None,
    subjects: List[str] = None,
    has_prize: Optional[bool] = None,
    prize_min: Optional[int] = None,
    deadline_days: Optional[int] = None,
    is_team: Optional[bool] = None,
    search: Optional[str] = None,
    sort: str = "deadline_asc",
) -> List[Olympiad]:
    with get_session() as session:
        stmt = select(Olympiad)

        # Фильтры
        if category:
            stmt = stmt.where(Olympiad.category == category)

        if subjects:
            conditions = [Olympiad.subjects.contains([s]) for s in subjects]
            stmt = stmt.where(or_(*conditions))

        if has_prize is not None:
            if has_prize:
                stmt = stmt.where(Olympiad.prize.is_not(None), Olympiad.prize != "")
            else:
                stmt = stmt.where(or_(Olympiad.prize.is_(None), Olympiad.prize == ""))

        if prize_min is not None:
            # Ищем числа в строке prize (упрощённо)
            stmt = stmt.where(
                Olympiad.prize.op("~*")(f"\\b({prize_min}|\\d+ ?000)\\b")
            )

        if deadline_days is not None:
            deadline = datetime.utcnow() + timedelta(days=deadline_days)
            stmt = stmt.where(
                Olympiad.registration_deadline <= deadline,
                Olympiad.registration_deadline.is_not(None),
            )

        if is_team is not None:
            stmt = stmt.where(Olympiad.is_team == is_team)

        if search:
            stmt = stmt.where(Olympiad.title.ilike(f"%{search}%"))

        # Сортировка
        if sort == "deadline_asc":
            stmt = stmt.where(Olympiad.registration_deadline.is_not(None)).order_by(
                asc(Olympiad.registration_deadline)
            )
        elif sort == "deadline_desc":
            stmt = stmt.where(Olympiad.registration_deadline.is_not(None)).order_by(
                desc(Olympiad.registration_deadline)
            )
        elif sort == "title":
            stmt = stmt.order_by(asc(Olympiad.title))
        elif sort == "new":
            stmt = stmt.order_by(desc(Olympiad.created_at))

        # Только активные
        stmt = stmt.where(Olympiad.is_active == True)

        return session.exec(stmt).all()


def get_all_subjects() -> List[str]:
    with get_session() as session:
        stmt = select(Olympiad.subjects)
        results = session.exec(stmt).all()

        unique_subjects = set()
        for subj_list in results:
            if subj_list:
                unique_subjects.update(subj_list)

        return sorted(list(unique_subjects))
