# apps/api/crud_olympiad.py
from typing import List, Optional
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from shared.db.engine import get_session
from apps.api.models_olympiad import Olympiad
from apps.api.models.category import Category  # ← важно!
import re
import unicodedata
from datetime import datetime, timedelta
from sqlalchemy import or_, desc, asc, and_


def slugify(value: str, max_length: int = 100) -> str:
    if not value:
        return ""
    value = unicodedata.normalize("NFKC", value)
    value = re.sub(r"[^\w\s-]", "", value, flags=re.U).strip().lower()
    value = re.sub(r"[-\s]+", "-", value)
    return value[:max_length].rstrip("-")


def _ensure_unique_slug(session, base_slug: str, max_attempts: int = 100) -> str:
    slug = base_slug
    i = 1
    while i < max_attempts:
        if not session.exec(select(Olympiad).where(Olympiad.slug == slug)).first():
            return slug
        slug = f"{base_slug}-{i}"
        i += 1
    raise RuntimeError("Can't generate unique slug")


def create_olympiad(obj: Olympiad) -> Olympiad:
    with get_session() as session:
        # Дедупликация по hash
        if obj.content_hash:
            existing = session.exec(
                select(Olympiad).where(Olympiad.content_hash == obj.content_hash)
            ).first()
            if existing:
                return existing

        # Генерация slug
        if not obj.slug:
            obj.slug = slugify(obj.title or "olympiad") or "olympiad"
        obj.slug = _ensure_unique_slug(session, obj.slug)

        try:
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj
        except IntegrityError:
            session.rollback()
            if obj.content_hash:
                existing = session.exec(
                    select(Olympiad).where(Olympiad.content_hash == obj.content_hash)
                ).first()
                if existing:
                    return existing
            raise


# Базовые функции
def list_olympiads(limit: int = 100) -> List[Olympiad]:
    with get_session() as session:
        return session.exec(select(Olympiad).limit(limit)).all()


def get_olympiad(olympiad_id: int) -> Optional[Olympiad]:
    with get_session() as session:
        return session.get(Olympiad, olympiad_id)


def list_olympiads_by_category(category: str) -> List[Olympiad]:
    # Оставляем для совместимости со старым фронтом (по slug)
    with get_session() as session:
        stmt = (
            select(Olympiad)
            .join(Category, Category.id == Olympiad.category_id)
            .where(Category.slug == category)
        )
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
        stmt = select(Olympiad).join(
            Category, Category.id == Olympiad.category_id, isouter=True
        )

        # === Фильтр по категории (поддерживаем и id, и slug) ===
        if category:
            try:
                # Попробуем как число (id)
                cat_id = int(category)
                stmt = stmt.where(Olympiad.category_id == cat_id)
            except ValueError:
                # Иначе — ищем по slug
                stmt = stmt.where(Category.slug == category)

        # Остальные фильтры
        if subjects:
            conditions = [Olympiad.subjects.contains([s]) for s in subjects]
            stmt = stmt.where(or_(*conditions))

        if has_prize is not None:
            if has_prize:
                stmt = stmt.where(Olympiad.prize.is_not(None), Olympiad.prize != "")
            else:
                stmt = stmt.where(or_(Olympiad.prize.is_(None), Olympiad.prize == ""))

        if prize_min is not None:
            stmt = stmt.where(Olympiad.prize.op("~*")(f"\\b({prize_min}|\\d+ ?000)\\b"))

        if deadline_days is not None:
            deadline = datetime.utcnow() + timedelta(days=deadline_days)
            stmt = stmt.where(
                Olympiad.registration_deadline.is_not(None),
                Olympiad.registration_deadline <= deadline,
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

        stmt = stmt.where(Olympiad.is_active == True)

        return session.exec(stmt).all()


def get_all_subjects() -> List[str]:
    with get_session() as session:
        results = session.exec(select(Olympiad.subjects)).all()
        unique = set()
        for item in results:
            if item:
                unique.update(item)
        return sorted(unique)