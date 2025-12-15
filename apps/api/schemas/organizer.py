# apps/api/schemas/organizer.py
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel

class OrganizerOut(SQLModel):
    id: int
    name: str
    slug: str

    short_name: Optional[str] = None
    logo_url: Optional[str] = None  # Added if needed
    banner_url: Optional[str] = None  # Added if needed
    website_url: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None  # Added if needed (from table)
    region: Optional[str] = None  # Added if needed (from table)
    is_verified: Optional[bool] = None  # Added if needed (from table, defaults to False in data)
    priority: Optional[int] = None
    is_premium: Optional[bool] = None
    premium_level: Optional[int] = None
    premium_until: Optional[datetime] = None
    owner_user_id: Optional[str] = None
    contact_email: Optional[str] = None  # Added if needed (from table)
    meta_title: Optional[str] = None  # Added if needed (from table)
    meta_description: Optional[str] = None  # Added if needed (from table)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None