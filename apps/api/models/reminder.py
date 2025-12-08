# apps/api/models/reminder.py — ИСПРАВЛЕНО
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB

class Reminder(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="auth.users.id")
    olympiad_id: int = Field(foreign_key="olympiad.id")
    remind_at: datetime
    channel: str = Field(default="tg")
    is_sent: bool = Field(default=False)
    sent_at: Optional[datetime] = None
    send_attempts: int = Field(default=0)
    last_attempt_at: Optional[datetime] = None
    fail_reason: Optional[str] = None
    recurrence: Optional[str] = None
    extra_data: dict = Field(default_factory=dict, sa_column=Column(JSONB))  # ← ИСПРАВЛЕНО!