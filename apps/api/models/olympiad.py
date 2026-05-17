# apps/api/models_olympiad.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB

class Olympiad(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # === Основное ===
    title: str = Field(index=True, max_length=500)
    slug: str = Field(index=True, unique=True, max_length=500)

    description: Optional[str] = Field(default=None)
    
    # === Связи ===
    organizer_id: int = Field(foreign_key="organizers.id")
    category_id: int = Field(foreign_key="categories.id")

    # === Уровень и предметы ===
    level: Optional[str] = Field(default=None, max_length=100)
    subjects: List[str] = Field(default_factory=list, sa_column=Column(JSONB))

    # === Формат участия ===
    is_team: Optional[bool] = Field(default=None)

    # === Даты ===
    start_date: Optional[datetime] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)
    registration_deadline: Optional[datetime] = Field(default=None, index=True)

    # === Призы ===
    prize: Optional[str] = Field(default=None)

    # === Парсинг и дедупликация ===
    source_url: Optional[str] = Field(default=None, max_length=1000)
    content_hash: Optional[str] = Field(default=None, index=True, max_length=64)

    # === Статусы ===
    is_active: bool = Field(default=True, index=True)
    parsed_at: datetime = Field(default_factory=datetime.utcnow)

    # === Аудит ===
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    logo_url: Optional[str] = None

    # Связи (для джоинов)
    # organizer: Optional["Organizer"] = Relationship(back_populates="olympiads")
    # category: Optional["Category"] = Relationship(back_populates="olympiads")