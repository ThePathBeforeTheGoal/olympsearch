# apps/api/routers/olympiads.py — ФИНАЛЬНАЯ ВЕРСИЯ (ДЕПЛОЙ ВЗЛЕТИТ)
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
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

# 1. ФИЛЬТР — ПЕРВЫЙ! (чтобы не конфликтовал с /{olympiad_id})
@router.get("/filter", response_model=List[Olympiad])
def filter_olympiads_endpoint(
    category: Optional[str] = Query(None, description="Точное название категории"),
    subjects: List[str] = Query(default=[], description="Предметы (можно несколько)"),
    has_prize: Optional[bool] = Query(None, description="Есть ли приз"),
    prize_min: Optional[int] = Query(None, description="Минимальный приз в рублях"),
    deadline_days: Optional[int] = Query(None, description="Дедлайн через N дней (например 14)"),
    is_team: Optional[bool] = Query(None, description="Командная/индивидуальная"),
    search: Optional[str] = Query(None, alias="q", description="Поиск по названию"),
    sort: Optional[str] = Query(
        "deadline_asc",
        description="Сортировка: deadline_asc | deadline_desc | title | new",
    ),
):
    return filter_olympiads(
        category=category,
        subjects=subjects,
        has_prize=has_prize,
        prize_min=prize_min,
        deadline_days=deadline_days,
        is_team=is_team,
        search=search,
        sort=sort,
    )

# 2. Остальные роуты — в любом порядке
@router.post("/", response_model=Olympiad)
def create(item: Olympiad):
    return create_olympiad(item)

@router.get("/", response_model=List[Olympiad])
def read_all(limit: int = 100):
    return list_olympiads(limit=limit)

@router.get("/category/{category}", response_model=List[Olympiad])
def read_category(category: str):
    return list_olympiads_by_category(category)

@router.get("/search/", response_model=List[Olympiad])
def search(q: str):
    return search_olympiads(q)

@router.get("/subjects", response_model=List[str])
def get_subjects():
    return get_all_subjects()

# 3. ОДИН — ПОСЛЕДНИЙ! (чтобы не ловил /filter)
@router.get("/{olympiad_id}", response_model=Olympiad)
def read_one(olympiad_id: int):
    obj = get_olympiad(olympiad_id)
    if not obj:
        raise HTTPException(404, "Not found")
    return obj