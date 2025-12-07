# apps/api/models/category.py
from sqlmodel import SQLModel, Field
from typing import Optional


class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=255)
    slug: str = Field(unique=True, max_length=128)
    icon: Optional[str] = None
    description: Optional[str] = None
    sort_order: int = Field(default=0)
    is_active: bool = Field(default=True)