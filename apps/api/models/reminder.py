# apps/api/models/reminder.py
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB  # либо JSON если предпочитаешь
from datetime import datetime
from typing import Optional

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
    metadata: dict = Field(default_factory=dict, sa_column=Column("JSONB"))