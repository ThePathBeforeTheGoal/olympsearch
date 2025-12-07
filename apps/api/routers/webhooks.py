# apps/api/routers/webhooks.py
from fastapi import APIRouter, Request, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
import logging
from apps.api.services.subscriptions import activate_subscription, create_audit
from sqlmodel import Session

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])
logger = logging.getLogger("webhooks")

def verify_signature(payload: dict, headers) -> bool:
    # TODO: implement YooKassa signature verification using headers and secret
    return True  # В демо — принимаем. В проде — обязательно валидировать!

def process_payment(payload: dict):
    # TODO: реализовать idempotent обработку вебхука:
    #  - найти provider_payment_id
    #  - проверить, не обработан ли уже
    #  - создать subscription + audit, обновить profiles
    logger.info("Processing payment webhook: %s", payload)

@router.post("/yookassa")
async def yookassa_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()
    headers = request.headers
    if not verify_signature(payload, headers):
        raise HTTPException(status_code=400, detail="Invalid signature")
    background_tasks.add_task(process_payment, payload)
    return {"status": "ok"}
