"""
backend/routers/beskeder.py

GET    /v1/beskeder/threads                         → tråde (filtrér på rolle)
GET    /v1/beskeder/threads/{threadId}/messages     → beskeder i tråd
POST   /v1/beskeder/threads/{threadId}/messages     → send besked
POST   /v1/beskeder/threads/{threadId}/read         → markér læst

Real-time: SignalR broadcaster sender "nyBesked"-event til abonnenter.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..models.beskeder import Thread, Message, MessageCreate

router = APIRouter(prefix="/v1/beskeder", tags=["Beskeder"])


@router.get("/threads", response_model=list[Thread])
def list_threads(role: str = Query(..., description="brobygger | raadgiver | admin")):
    """
    FASE 2:
        if role == "brobygger":
            return db.query(ThreadORM).filter(ThreadORM.brobygger_id == current_user.id).all()
        elif role == "raadgiver":
            return db.query(ThreadORM).filter(ThreadORM.raadgiver_id == current_user.id).all()
    """
    raise HTTPException(503, "Backend ikke aktivt endnu")


@router.get("/threads/{thread_id}/messages", response_model=list[Message])
def get_messages(thread_id: str):
    raise HTTPException(503, "Backend ikke aktivt endnu")


@router.post("/threads/{thread_id}/messages", response_model=Message, status_code=201)
def send_message(thread_id: str, data: MessageCreate):
    """
    FASE 2:
        msg = MessageORM(id=str(uuid4()), thread_id=thread_id, ...)
        db.add(msg); db.commit()
        # SignalR broadcast
        await signalr_hub.send_to_group(thread_id, "nyBesked", msg.to_dict())
        # Web Push til modtager (hvis offline)
        await push_service.notify(recipient_id, {"title": "Ny besked", "body": data.text[:80]})
        return msg
    """
    raise HTTPException(503, "Backend ikke aktivt endnu")


@router.post("/threads/{thread_id}/read", status_code=200)
def mark_thread_read(thread_id: str):
    raise HTTPException(503, "Backend ikke aktivt endnu")
