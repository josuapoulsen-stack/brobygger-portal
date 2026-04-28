"""
backend/routers/aftaler.py

GET    /v1/aftaler                    → liste (filter: brobygger_id, menneske_id, status)
GET    /v1/aftaler/{id}               → enkelt
POST   /v1/aftaler                    → opret
PATCH  /v1/aftaler/{id}/status        → opdatér status + noter
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..models.aftaler import Aftale, AftaleCreate, AftaleStatusUpdate

router = APIRouter(prefix="/v1/aftaler", tags=["Aftaler"])


@router.get("", response_model=list[Aftale])
def list_aftaler(
    brobygger_id: Optional[str] = Query(None),
    menneske_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
):
    raise HTTPException(503, "Backend ikke aktivt endnu")


@router.get("/{aftale_id}", response_model=Aftale)
def get_aftale(aftale_id: str):
    raise HTTPException(503, "Backend ikke aktivt endnu")


@router.post("", response_model=Aftale, status_code=201)
def create_aftale(data: AftaleCreate):
    """
    FASE 2:
        # Tjek brobygger har kapacitet
        b = db.query(BrobyggerORM).get(data.brobyggerId)
        if b.active >= b.maxActive:
            raise HTTPException(409, "Brobygger har ikke kapacitet")
        record = AftaleORM(**data.model_dump(), id=str(uuid4()), ...)
        db.add(record); db.commit()
        # Send SignalR-event til brobygger
        await signalr.send("nyAftale", {...})
        return record
    """
    raise HTTPException(503, "Backend ikke aktivt endnu")


@router.patch("/{aftale_id}/status")
def update_aftale_status(aftale_id: str, data: AftaleStatusUpdate):
    raise HTTPException(503, "Backend ikke aktivt endnu")
