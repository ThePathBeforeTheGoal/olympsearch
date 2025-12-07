# apps/api/models/organizer.py
from sqlmodel import SQLModel, Field
from typing import Optional


class Organizer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    short_name: Optional[str] = None
    slug: str = Field(unique=True, max_length=255)
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    description: Optional[str] = None