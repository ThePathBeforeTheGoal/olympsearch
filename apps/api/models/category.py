# apps/api/models/category.py
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB

class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=255)
    slug: str = Field(unique=True, max_length=128)
    icon: Optional[str] = None
    description: Optional[str] = None
    sort_order: int = Field(default=0)
    is_active: bool = Field(default=True)

    # Эти поля отражают схему БД
    meta: dict = Field(default_factory=dict, sa_column=Column(JSONB))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
