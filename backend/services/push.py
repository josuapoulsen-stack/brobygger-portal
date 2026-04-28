"""
backend/services/push.py — Web Push-notifikationer via VAPID

Sender push til én eller alle enheder registreret på en bruger.
VAPID-nøgler er genereret og gemt i .env.example.

Brug:
    await push_to_user(db, bruger_id, title="Ny besked", body="Maja siger...")
    await push_to_all_brobyggere(db, title="...", body="...")
"""

import json
import logging
from uuid import UUID
from typing import Optional
from pywebpush import webpush, WebPushException
from sqlalchemy.orm import Session

from ..config import settings
from ..orm_models import PushSubscriptionORM

log = logging.getLogger(__name__)


def _send_one(subscription: PushSubscriptionORM, payload: dict) -> bool:
    """
    Send push til én subscription. Returnerer True ved succes.
    Returnerer False og logger ved fejl (expired/invalid endpoint slettes ikke her).
    """
    try:
        webpush(
            subscription_info={
                "endpoint": subscription.endpoint,
                "keys": {
                    "p256dh": subscription.p256dh,
                    "auth":   subscription.auth_key,
                },
            },
            data=json.dumps(payload),
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={"sub": settings.VAPID_SUBJECT},
        )
        return True
    except WebPushException as e:
        status = getattr(e.response, "status_code", None)
        if status in (404, 410):
            # Endpoint er udløbet/slettet — marker til sletning
            log.info("Push-endpoint udløbet (bruger=%s): %s", subscription.bruger_id, subscription.endpoint[:60])
            return False
        log.warning("Push-fejl (bruger=%s): %s", subscription.bruger_id, e)
        return False


async def push_to_user(
    db: Session,
    bruger_id: UUID,
    title: str,
    body: str,
    url: str = "/",
    tag: Optional[str] = None,
    icon: str = "/logo.png",
) -> int:
    """
    Send push til alle enheder registreret på én bruger.
    Returnerer antal vellykkede afsendelser.
    """
    subs = db.query(PushSubscriptionORM).filter_by(bruger_id=bruger_id).all()
    if not subs:
        return 0

    payload = {"title": title, "body": body, "url": url, "icon": icon}
    if tag:
        payload["tag"] = tag

    ok_count = 0
    expired = []

    for sub in subs:
        success = _send_one(sub, payload)
        if success:
            ok_count += 1
        else:
            expired.append(sub)

    # Ryd udløbne subscriptions
    for sub in expired:
        db.delete(sub)
    if expired:
        db.commit()

    return ok_count


async def push_to_all_brobyggere(
    db: Session,
    title: str,
    body: str,
    url: str = "/",
    hq: Optional[str] = None,
) -> int:
    """
    Udsend push-notifikation til alle aktive brobyggere (fx officielle nyheder).
    Filtrer optionelt på HQ.
    """
    from ..orm_models import BrugerORM, BrobyggerStatusEnum, BrugerRolleEnum

    query = db.query(BrugerORM).filter_by(rolle=BrugerRolleEnum.Brobygger, aktiv=True)
    if hq:
        query = query.filter_by(hq=hq)

    brugere = query.all()
    total = 0
    for bruger in brugere:
        total += await push_to_user(db, bruger.id, title, body, url)
    return total
