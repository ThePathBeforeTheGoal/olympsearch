# apps/api/models/subscription.py
from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional
from datetime import datetime

class Plan(SQLModel, table=True):
    __tablename__ = "plans"
    id: Optional[int] = Field(default=None, primary_key=True)
    plan_key: str = Field(unique=True, index=True, max_length=64)
    title: str
    price_rub: int = Field(default=0)
    duration_days: int
    favorites_limit: Optional[int] = None
    reminders_limit: Optional[int] = None
    other_perks: dict = Field(default_factory=dict, sa_column=Column(JSONB))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserSubscription(SQLModel, table=True):
    __tablename__ = "user_subscriptions"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="auth.users.id", index=True)  # UUID string
    plan_key: str = Field(foreign_key="plans.plan_key", index=True, max_length=64)
    status: str = Field(default="inactive", max_length=32)  # inactive|active|past_due|canceled
    provider: Optional[str] = None
    provider_payment_id: Optional[str] = None
    started_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    auto_renew: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = Field(default_factory=dict, sa_column=Column(JSONB))


class SubscriptionAudit(SQLModel, table=True):
    __tablename__ = "subscription_audit"
    id: Optional[int] = Field(default=None, primary_key=True)
    subscription_id: Optional[int] = Field(foreign_key="user_subscriptions.id", index=True)
    event_type: str
    event_data: dict = Field(sa_column=Column(JSONB))
    created_at: datetime = Field(default_factory=datetime.utcnow)
