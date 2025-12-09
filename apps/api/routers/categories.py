# apps/api/routers/categories.py  (временно)
from fastapi import APIRouter, HTTPException
from sqlmodel import select, Session
from typing import List
from shared.db.engine import get_engine
from apps.api.models.category import Category

router = APIRouter(prefix="/api/v1/categories", tags=["categories"])

@router.get("/", response_model=List[Category])
def get_categories():
    engine = get_engine()
    try:
        with Session(engine) as session:
            stmt = select(Category).where(Category.is_active == True).order_by(Category.sort_order)
            return session.exec(stmt).all()
    except Exception as e:
        # временная диагностическая отдача
        raise HTTPException(status_code=500, detail=str(e))
