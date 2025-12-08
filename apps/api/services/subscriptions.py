# apps/api/services/subscriptions.py
from sqlmodel import select
from shared.db.engine import get_session
from apps.api.models.subscription import UserSubscription, SubscriptionAudit, Plan
from apps.api.models import subscription as models_sub  # если требуется
from datetime import datetime, timedelta
from sqlmodel import Session
import logging

logger = logging.getLogger("subscriptions")

def create_audit(session: Session, subscription_id: int, event_type: str, event_data: dict):
    audit = SubscriptionAudit(subscription_id=subscription_id, event_type=event_type, event_data=event_data)
    session.add(audit)
    session.commit()
    session.refresh(audit)
    return audit

def activate_subscription(session: Session, user_id: str, plan_key: str, provider: str = None, provider_payment_id: str = None, started_at: datetime = None, expires_at: datetime = None, metadata: dict = None):
    """
    Создаёт/обновляет подписку пользователя: ставит status=active и обновляет профили.
    Idempotent: если есть активная подписка с тем же provider_payment_id — вернёт существующую.
    """
    if metadata is None:
        metadata = {}

    # check existing by provider_payment_id (idempotency)
    if provider_payment_id:
        existing = session.exec(select(UserSubscription).where(UserSubscription.provider_payment_id == provider_payment_id)).first()
        if existing:
            return existing

    # expire other active subs for this user (simple model)
    active_subs = session.exec(select(UserSubscription).where(UserSubscription.user_id == user_id, UserSubscription.status == "active")).all()
    for s in active_subs:
        s.status = "canceled"
        s.updated_at = datetime.utcnow()
        session.add(s)

    # create new subscription
    now = datetime.utcnow()
    started_at = started_at or now
    if expires_at is None:
        # compute from plan
        plan = session.exec(select(Plan).where(Plan.plan_key == plan_key)).first()
        if plan and plan.duration_days:
            expires_at = started_at + timedelta(days=plan.duration_days)
        else:
            expires_at = None

    sub = UserSubscription(
        user_id=user_id,
        plan_key=plan_key,
        status="active",
        provider=provider,
        provider_payment_id=provider_payment_id,
        started_at=started_at,
        expires_at=expires_at,
        auto_renew=False if provider is None else True,
        created_at=now,
        updated_at=now,
        extra_data=metadata or {}
    )
    session.add(sub)
    session.commit()
    session.refresh(sub)

    # apply plan limits to profile (simple approach: write favorites_limit/reminders_limit)
    try:
        if plan := session.exec(select(Plan).where(Plan.plan_key == plan_key)).first():
            # profiles table update
            session.execute(
                "UPDATE public.profiles SET favorites_limit = :fav, reminders_limit = :rem WHERE id = :uid",
                {"fav": plan.favorites_limit, "rem": plan.reminders_limit, "uid": user_id},
            )
            session.commit()
    except Exception as e:
        logger.exception("Failed to apply plan limits: %s", e)

    # audit
    create_audit(session, sub.id, "activated", {"plan_key": plan_key, "provider": provider, "provider_payment_id": provider_payment_id})
    return sub

def cancel_subscription(session: Session, subscription_id: int, reason: str = None):
    sub = session.get(UserSubscription, subscription_id)
    if not sub:
        return None
    sub.status = "canceled"
    sub.updated_at = datetime.utcnow()
    session.add(sub)
    session.commit()
    create_audit(session, sub.id, "canceled", {"reason": reason})
    return sub
