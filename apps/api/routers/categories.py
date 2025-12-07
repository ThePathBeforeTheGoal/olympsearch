# apps/api/routers/categories.py
from fastapi import APIRouter, Depends
from sqlmodel import select
from typing import List
from shared.db.engine import get_session
from apps.api.models.category import Category
from sqlmodel import Session

router = APIRouter(prefix="/api/v1/categories", tags=["categories"])

@router.get("/", response_model=List[Category])
def get_categories(session: Session = Depends(get_session)):
    stmt = select(Category).where(Category.is_active == True).order_by(Category.sort_order)
    return session.exec(stmt).all()
