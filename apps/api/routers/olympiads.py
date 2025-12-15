# apps/api/routers/olympiads.py — ИСПРАВЛЕНО ПОД НОВЫЙ СТИЛЬ С SESSION
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from sqlmodel import Session
from shared.db.engine import get_session_depends  # ← важно!

from apps.api.models_olympiad import Olympiad
from apps.api.crud_olympiad import (
    create_olympiad,
    list_olympiads,
    get_olympiad,
    list_olympiads_by_category,
    search_olympiads,
    filter_olympiads,
    get_all_subjects,
)

router = APIRouter(prefix="/api/v1/olympiads", tags=["olympiads"])

# 1. ФИЛЬТР — основной и самый сложный
@router.get("/filter", response_model=List[Olympiad])
def filter_olympiads_endpoint(
    category: Optional[str] = Query(None),
    subjects: List[str] = Query(default=[]),
    has_prize: Optional[bool] = Query(None),
    prize_min: Optional[int] = Query(None),
    deadline_days: Optional[int] = Query(None),
    is_team: Optional[bool] = Query(None),
    search: Optional[str] = Query(None, alias="q"),
    sort: Optional[str] = Query("deadline_asc"),
    session: Session = Depends(get_session_depends),
):
    return filter_olympiads(
        session=session,
        category=category,
        subjects=subjects,
        has_prize=has_prize,
        prize_min=prize_min,
        deadline_days=deadline_days,
        is_team=is_team,
        search=search,
        sort=sort,
    )

# 2. Создание (POST)
@router.post("/", response_model=Olympiad)
def create(item: Olympiad, session: Session = Depends(get_session_depends)):
    return create_olympiad(session=session, obj=item)

# 3. Все олимпиады
@router.get("/", response_model=List[Olympiad])
def read_all(limit: int = Query(100, ge=1, le=1000), session: Session = Depends(get_session_depends)):
    return list_olympiads(session=session, limit=limit)

# 4. По категории (старый фронт)
@router.get("/category/{category}", response_model=List[Olympiad])
def read_category(category: str, session: Session = Depends(get_session_depends)):
    return list_olympiads_by_category(session=session, category=category)

# 5. Поиск
@router.get("/search/", response_model=List[Olympiad])
def search(q: str, session: Session = Depends(get_session_depends)):
    return search_olympiads(session=session, q=q)

# 6. Все предметы — вот здесь была ошибка!
@router.get("/subjects", response_model=List[str])
def get_subjects(session: Session = Depends(get_session_depends)):
    return get_all_subjects(session=session)

# 7. Одна олимпиада по ID — в конце, чтобы не конфликтовать с /filter и /subjects
@router.get("/{olympiad_id}", response_model=Olympiad)
def read_one(olympiad_id: int, session: Session = Depends(get_session_depends)):
    obj = get_olympiad(session=session, olympiad_id=olympiad_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Olympiad not found")
    return obj