# apps/api/crud_olympiad.py
from typing import List, Optional
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from shared.db.engine import get_session
from apps.api.models_olympiad import Olympiad
import re
import unicodedata


def slugify(value: str, max_length: int = 100) -> str:
    if not value:
        return ""
    # Нормализуем строку
    value = unicodedata.normalize("NFKC", value)
    # Удаляем всё, что не буквы/цифры/подчёрки/пробел/дефис (Unicode-aware)
    value = re.sub(r"[^\w\s-]", "", value, flags=re.U).strip().lower()
    # Заменяем пробелы и множественные дефисы на один дефис
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
        # 1. Дедупликация по content_hash
        if obj.content_hash:
            existing = session.exec(
                select(Olympiad).where(Olympiad.content_hash == obj.content_hash)
            ).first()
            if existing:
                return existing

        # 2. Автогенерация slug, если не указан
        if not obj.slug:
            base = slugify(obj.title or "olympiad")
            obj.slug = base or "olympiad"

        # 3. Гарантируем уникальность slug
        obj.slug = _ensure_unique_slug(session, obj.slug)

        # 4. Вставляем
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


# ←←←← ЭТИ ДВЕ ФУНКЦИИ ОБЯЗАТЕЛЬНО ДОЛЖНЫ БЫТЬ! ←←←←
def list_olympiads(limit: int = 100) -> List[Olympiad]:
    with get_session() as session:
        stmt = select(Olympiad).limit(limit)
        return session.exec(stmt).all()


def get_olympiad(olympiad_id: int) -> Optional[Olympiad]:
    with get_session() as session:
        return session.get(Olympiad, olympiad_id)