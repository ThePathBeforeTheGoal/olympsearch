# apps/api/crud_olympiad.py
from typing import List, Optional
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from shared.db.engine import get_session
from apps.api.models_olympiad import Olympiad
import re
import unicodedata

def slugify(value: str, max_length: int = 100) -> str:
    """
    Простая функция slugify: транслитерация/нормализация + replace non-alnum -> -
    """
    if not value:
        return ""
    # нормализуем unicode
    value = unicodedata.normalize("NFKD", value)
    # оставляем латиницу и цифры, заменяем пробелы на -
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    value = re.sub(r"[-\s]+", "-", value)
    return value[:max_length].strip("-")

def _ensure_unique_slug(session, base_slug: str, max_attempts: int = 100) -> str:
    slug = base_slug
    i = 1
    while True:
        stmt = select(Olympiad).where(Olympiad.slug == slug)
        exists = session.exec(stmt).first()
        if not exists:
            return slug
        slug = f"{base_slug}-{i}"
        i += 1
        if i > max_attempts:
            raise RuntimeError("Can't find unique slug")

def create_olympiad(obj: Olympiad) -> Olympiad:
    """
    Behaviour:
    - if content_hash exists -> return existing (dedupe)
    - else generate slug if needed and ensure uniqueness, then insert
    """
    with get_session() as session:
        # 1) dedupe by content_hash
        if getattr(obj, "content_hash", None):
            stmt = select(Olympiad).where(Olympiad.content_hash == obj.content_hash)
            existing = session.exec(stmt).first()
            if existing:
                return existing

        # 2) ensure slug present
        if not getattr(obj, "slug", None):
            base = slugify(getattr(obj, "title", "") or "item")
            obj.slug = base[:500]  # respect your model limit

        # 3) make slug unique (in-transaction check)
        obj.slug = _ensure_unique_slug(session, obj.slug)

        # 4) try insert (handle rare race via IntegrityError)
        try:
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj
        except IntegrityError:
            session.rollback()
            # race condition — someone else might have inserted same slug or content_hash
            # try to find by content_hash first
            if getattr(obj, "content_hash", None):
                stmt = select(Olympiad).where(Olympiad.content_hash == obj.content_hash)
                existing = session.exec(stmt).first()
                if existing:
                    return existing
            # otherwise try to make a new unique slug and retry a few times
            for attempt in range(1, 6):
                base = slugify(obj.slug.split("-")[0])
                new_slug = f"{base}-{attempt}"
                obj.slug = new_slug
                try:
                    session.add(obj)
                    session.commit()
                    session.refresh(obj)
                    return obj
                except IntegrityError:
                    session.rollback()
                    continue
            raise
