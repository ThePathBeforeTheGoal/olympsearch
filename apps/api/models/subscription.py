# apps/api/models/subscription.py — ФИНАЛЬНАЯ ВЕРСИЯ (ДЕПЛОЙ ВЗЛЕТИТ)
from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB, UUID
from typing import Optional
from datetime import datetime

# 1. Сначала Plan — без проблем
class Plan(SQLModel, table=True):
    __tablename__ = "plans"  # ← Явно указываем имя таблицы

    id: Optional[int] = Field(default=None, primary_key=True)
    plan_key: str = Field(unique=True, index=True)
    title: str
    price_rub: int = Field(default=0)
    duration_days: int
    favorites_limit: Optional[int] = None
    reminders_limit: Optional[int] = None
    other_perks: dict = Field(default_factory=dict, sa_column=Column(JSONB))


# 2. UserSubscription — УБРАЛИ foreign_key отовсюду!
class UserSubscription(SQLModel, table=True):
    __tablename__ = "user_subscriptions"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(sa_column=Column(UUID(as_uuid=False)), index=True)
    plan_key: str = Field(index=True)  # ← БЕЗ foreign_key! Только индекс!
    status: str = Field(default="inactive")
    provider: Optional[str] = None
    provider_payment_id: Optional[str] = None
    started_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    auto_renew: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    extra_data: dict = Field(default_factory=dict, sa_column=Column(JSONB))


# 3. SubscriptionAudit — FK только к своей таблице
class SubscriptionAudit(SQLModel, table=True):
    __tablename__ = "subscription_audit"

    id: Optional[int] = Field(default=None, primary_key=True)
    subscription_id: int = Field(foreign_key="user_subscriptions.id")
    event_type: str
    event_data: dict = Field(sa_column=Column(JSONB))
    created_at: datetime = Field(default_factory=datetime.utcnow)