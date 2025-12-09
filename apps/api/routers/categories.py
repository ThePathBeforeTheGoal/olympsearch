# apps/api/routers/categories.py
from fastapi import APIRouter, Depends
from sqlmodel import select, Session
from typing import List
from shared.db.engine import get_session_depends  # ← ИЗМЕНИТЬ ИМПОРТ!
from apps.api.models.category import Category

router = APIRouter(prefix="/api/v1/categories", tags=["categories"])

@router.get("/", response_model=List[Category])
def get_categories(session: Session = Depends(get_session_depends)):  # ← ИСПОЛЬЗОВАТЬ get_session_depends
    stmt = select(Category).where(Category.is_active == True).order_by(Category.sort_order)
    return session.exec(stmt).all()