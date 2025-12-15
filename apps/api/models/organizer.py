# apps/api/models/organizer.py — ДЕЙСТВИТЕЛЬНО ИСПРАВЛЕНО НАВСЕГДА :)
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import func  # Для автозаполнения дат

class Organizer(SQLModel, table=True):
    __tablename__ = "organizers"

    id: Optional[int] = Field(default=None, primary_key=True)

    name: str = Field(..., max_length=255)  # Required
    short_name: Optional[str] = Field(default=None, max_length=100)
    slug: str = Field(..., unique=True, max_length=255)  # Required, unique

    logo_url: Optional[str] = Field(default=None)
    banner_url: Optional[str] = Field(default=None)  # Добавлено (missing в твоём коде)
    website_url: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)

    type: Optional[str] = Field(default=None)  # Добавлено (e.g., 'other')
    region: Optional[str] = Field(default=None)  # Добавлено

    is_verified: bool = Field(default=False)  # Добавлено (bool, default False)

    priority: int = Field(default=0)
    is_premium: bool = Field(default=False)
    premium_until: Optional[datetime] = Field(default=None)
    premium_level: Optional[int] = Field(default=0)

    owner_user_id: Optional[str] = Field(default=None, index=True)

    contact_email: Optional[str] = Field(default=None)  # Добавлено
    meta_title: Optional[str] = Field(default=None)  # Добавлено
    meta_description: Optional[str] = Field(default=None)  # Добавлено

    created_at: Optional[datetime] = Field(default=None, sa_column_kwargs={"server_default": func.now()})
    updated_at: Optional[datetime] = Field(default=None, sa_column_kwargs={"server_default": func.now(), "onupdate": func.now()})