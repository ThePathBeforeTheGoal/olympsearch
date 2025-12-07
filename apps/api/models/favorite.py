# apps/api/models/favorite.py
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Favorite(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="auth.users.id")
    olympiad_id: int = Field(foreign_key="olympiad.id")
    added_at: datetime = Field(default_factory=datetime.utcnow)
    note: Optional[str] = None
    is_archived: bool = Field(default=False)
