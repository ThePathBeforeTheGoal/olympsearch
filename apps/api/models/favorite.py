from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column

class Favorite(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(sa_column=Column(UUID(as_uuid=False)))  # ← УБРАЛИ foreign_key
    olympiad_id: int = Field(foreign_key="olympiad.id")
    added_at: datetime = Field(default_factory=datetime.utcnow)
    note: Optional[str] = None
    is_archived: bool = Field(default=False)