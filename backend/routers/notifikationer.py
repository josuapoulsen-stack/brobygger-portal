"""
backend/routers/notifikationer.py

GET   /v1/notifikationer              → alle notifikationer for aktuel bruger
POST  /v1/notifikationer/{id}/read    → markér læst
POST  /v1/push/subscribe              → gem Web Push-subscription (VAPID)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(tags=["Notifikationer"])


class PushSubscription(BaseModel):
    endpoint: str
    keys: dict          # { "p256dh": "...", "auth": "..." }


@router.get("/v1/notifikationer")
def list_notifikationer():
    raise HTTPException(503, "Backend ikke aktivt endnu")


@router.post("/v1/notifikationer/{notif_id}/read")
def mark_notifikation_read(notif_id: str):
    raise HTTPException(503, "Backend ikke aktivt endnu")


@router.post("/v1/push/subscribe", status_code=201)
def subscribe_push(data: PushSubscription):
    """
    Gem Web Push-subscription så backend kan sende push-notifikationer
    til brugerens browser/PWA når de er offline.

    FASE 2:
        sub = PushSubscriptionORM(
            user_id=current_user.id,
            endpoint=data.endpoint,
            p256dh=data.keys["p256dh"],
            auth=data.keys["auth"],
        )
        db.merge(sub); db.commit()
    """
    raise HTTPException(503, "Backend ikke aktivt endnu")
