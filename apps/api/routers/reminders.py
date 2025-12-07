# apps/api/routers/reminders.py
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from shared.db.engine import get_session
from apps.api.models.reminder import Reminder
from auth import get_current_user

router = APIRouter(prefix="/api/v1/reminders", tags=["reminders"])

@router.get("/", response_model=List[Reminder])
def get_reminders(session: Session = Depends(get_session), user = Depends(get_current_user)):
    stmt = select(Reminder).where(Reminder.user_id == user.id, Reminder.is_sent == False)
    return session.exec(stmt).all()
