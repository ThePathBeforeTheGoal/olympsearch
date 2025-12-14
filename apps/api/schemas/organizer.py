# apps/api/schemas/organizer.py
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel

class OrganizerOut(SQLModel):
    id: int
    name: str
    slug: str

    short_name: Optional[str] = None
    website_url: Optional[str] = None
    description: Optional[str] = None

    priority: Optional[int] = None
    is_premium: Optional[bool] = None
    premium_level: Optional[int] = None
    premium_until: Optional[datetime] = None

    owner_user_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

