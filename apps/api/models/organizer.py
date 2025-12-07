# apps/api/models/organizer.py
from typing import Optional
from datetime import datetime

from sqlmodel import SQLModel, Field
# JSONB здесь не используется, оставлю импорт если понадобится позже
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB


class Organizer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(..., max_length=255)
    short_name: Optional[str] = Field(default=None, max_length=100)
    slug: str = Field(..., unique=True, max_length=255)
    logo_url: Optional[str] = Field(default=None)
    website_url: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)

    # optional extras:
    priority: int = Field(default=0)
    is_premium: bool = Field(default=False)
    premium_until: Optional[datetime] = Field(default=None)
    premium_level: Optional[int] = Field(default=0)
    owner_user_id: Optional[str] = Field(default=None, foreign_key="auth.users.id")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
