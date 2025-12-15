# apps/api/crud_olympiad.py
from typing import List, Optional
from sqlmodel import select, Session  # Добавлен Session
from sqlalchemy.exc import IntegrityError
# Убрали get_session, т.к. session теперь параметр
from apps.api.models_olympiad import Olympiad
from apps.api.models.category import Category  # ← важно!
from sqlalchemy import func
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


def _ensure_unique_slug(session: Session, base_slug: str, max_attempts: int = 100) -> str:
    slug = base_slug
    i = 1
    while i < max_attempts:
        if not session.exec(select(Olympiad).where(Olympiad.slug == slug)).first():
            return slug
        slug = f"{base_slug}-{i}"
        i += 1
    raise RuntimeError("Can't generate unique slug")


def create_olympiad(session: Session, obj: Olympiad) -> Olympiad:
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
def list_olympiads(session: Session, limit: int = 100) -> List[Olympiad]:
    return session.exec(select(Olympiad).limit(limit)).all()


def get_olympiad(session: Session, olympiad_id: int) -> Optional[Olympiad]:
    return session.get(Olympiad, olympiad_id)


def list_olympiads_by_category(session: Session, category: str) -> List[Olympiad]:
    # Оставляем для совместимости со старым фронтом (по slug)
    stmt = (
        select(Olympiad)
        .join(Category, Category.id == Olympiad.category_id)
        .where(Category.slug == category)
    )
    return session.exec(stmt).all()


def search_olympiads(session: Session, q: str) -> List[Olympiad]:
    stmt = select(Olympiad).where(Olympiad.title.ilike(f"%{q}%"))
    return session.exec(stmt).all()


# ИСПРАВЛЕННАЯ ВЕРСИЯ функции filter_olympiads
def filter_olympiads(
    session: Session,
    category: Optional[str] = None,
    subjects: List[str] = None,
    has_prize: Optional[bool] = None,
    prize_min: Optional[int] = None,
    deadline_days: Optional[int] = None,
    is_team: Optional[bool] = None,
    search: Optional[str] = None,
    sort: str = "deadline_asc",
) -> List[Olympiad]:
    stmt = select(Olympiad).join(
        Category, Category.id == Olympiad.category_id, isouter=True
    )

    # === Фильтр по категории ===
    if category:
        try:
            # Попробуем как число (id)
            cat_id = int(category)
            stmt = stmt.where(Olympiad.category_id == cat_id)
        except ValueError:
            # Иначе — ищем по slug
            # ВАЖНО: нужно искать в таблице Category по slug
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
        # Используем более надежную проверку для призов
        stmt = stmt.where(
            Olympiad.prize.is_not(None),
            Olympiad.prize.op("~")("\\d+")  # содержит цифры
        )

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

    # ДЕБАГ: посмотрим SQL запрос
    print(f"SQL Query: {stmt}")
    results = session.exec(stmt).all()
    print(f"Found {len(results)} results")
    return results

def get_all_subjects(session: Session) -> List[str]:
    results = session.exec(select(Olympiad.subjects)).all()
    unique = set()
    for item in results:
        if item:
            unique.update(item)
    return sorted(unique)