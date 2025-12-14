# apps/api/models/organizer.py — ИСПРАВЛЕНО НАВСЕГДА
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class Organizer(SQLModel, table=True):
    __tablename__ = "organizers"

    id: Optional[int] = Field(default=None, primary_key=True)

    name: str = Field(..., max_length=255)
    short_name: Optional[str] = Field(default=None, max_length=100)
    slug: str = Field(..., unique=True, max_length=255)

    logo_url: Optional[str] = Field(default=None)
    website_url: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)

    priority: int = Field(default=0)
    is_premium: bool = Field(default=False)
    premium_until: Optional[datetime] = Field(default=None)
    premium_level: Optional[int] = Field(default=0)

    owner_user_id: Optional[str] = Field(default=None, index=True)

    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)