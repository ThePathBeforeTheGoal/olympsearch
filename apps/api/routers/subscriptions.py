# apps/api/routers/subscriptions.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from shared.db.engine import get_session
from apps.api.models.subscription import Plan, UserSubscription, SubscriptionAudit
from apps.api.services.subscriptions import activate_subscription, cancel_subscription, create_audit
from apps.api.auth import get_current_user, get_admin_user
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/api/v1/subscriptions", tags=["subscriptions"])

@router.get("/plans", response_model=List[Plan])
def list_plans(session: Session = Depends(get_session)):
    stmt = select(Plan)
    return session.exec(stmt).all()

@router.get("/me", response_model=List[UserSubscription])
def my_subscriptions(session: Session = Depends(get_session), user = Depends(get_current_user)):
    stmt = select(UserSubscription).where(UserSubscription.user_id == user.id)
    return session.exec(stmt).all()

@router.post("/demo/activate", status_code=201)
def demo_activate(plan_key: str, session: Session = Depends(get_session), user = Depends(get_current_user)):
    # quick demo endpoint to activate a plan for the current user (no payment)
    sub = activate_subscription(session=session, user_id=user.id, plan_key=plan_key, provider="internal-demo", provider_payment_id=None, started_at=datetime.utcnow())
    return {"message": "activated", "subscription_id": sub.id, "expires_at": sub.expires_at}

@router.post("/{subscription_id}/cancel", status_code=200)
def cancel(subscription_id: int, session: Session = Depends(get_session), user = Depends(get_current_user)):
    sub = session.get(UserSubscription, subscription_id)
    if not sub or sub.user_id != user.id:
        raise HTTPException(status_code=404, detail="Not found")
    cancel_subscription(session, subscription_id)
    return {"message": "canceled"}

# Admin webhook receiver can be in webhooks router; we provide helper to be used there
@router.get("/audit", response_model=List[SubscriptionAudit])
def list_audit(session: Session = Depends(get_session), admin = Depends(get_admin_user)):
    stmt = select(SubscriptionAudit).order_by(SubscriptionAudit.created_at.desc()).limit(200)
    return session.exec(stmt).all()
