# apps/api/models/olympiad.py
from sqlmodel import SQLModel, Field, JSON, Column
from typing import Optional, List
from datetime import datetime


class Olympiad(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # === Основное ===
    title: str = Field(index=True, max_length=500)
    slug: str = Field(index=True, unique=True, max_length=500)  # будет генерироваться из title

    description: Optional[str] = Field(default=None)
    organizer: Optional[str] = Field(default=None, max_length=300)

    # === Уровень и предметы ===
    level: Optional[str] = Field(default=None, max_length=100)        # Всерос, регион, вуз и т.д.
    subjects: List[str] = Field(default_factory=list, sa_column=Column(JSON))  # ["Математика", "Физика"]

    # === Формат участия ===
    is_team: Optional[bool] = Field(default=None)  # True = командная, False = личная, None = не указано

    # === Даты ===
    start_date: Optional[datetime] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)
    registration_deadline: Optional[datetime] = Field(default=None, index=True)  # для сортировки

    # === Призы ===
    prize: Optional[str] = Field(default=None)  # "льгота БВИ, 100к руб, диплом I степени"

    # === Парсинг и дедупликация ===
    source_url: str = Field(max_length=1000)
    content_hash: str = Field(index=True, max_length=64)  # для предотвращения дублей

    # === Статусы ===
    is_active: bool = Field(default=True, index=True)
    parsed_at: datetime = Field(default_factory=datetime.utcnow)

    # === Аудит ===
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)