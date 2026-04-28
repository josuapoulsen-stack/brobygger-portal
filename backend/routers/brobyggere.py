"""
backend/routers/brobyggere.py

GET    /v1/brobyggere         → liste (filtrér på status, hq, type)
GET    /v1/brobyggere/{id}    → enkelt
PATCH  /v1/brobyggere/{id}    → opdatér (koordinator-brug)

Oprettelse sker via Azure Entra ID invitation + onboarding-wizard i appen.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..models.brobyggere import Brobygger, BrobyggerUpdate

router = APIRouter(prefix="/v1/brobyggere", tags=["Brobyggere"])


@router.get("", response_model=list[Brobygger])
def list_brobyggere(
    status: Optional[str] = Query(None),
    hq: Optional[str] = Query(None),
    type: Optional[str] = Query(None, description="Filtrer på type (en-to-en, gruppe, ...)"),
):
    """
    FASE 2:
        rows = db.query(BrobyggerORM)
        if status: rows = rows.filter(...)
        return rows.order_by(BrobyggerORM.navn).all()
    """
    raise HTTPException(503, "Backend ikke aktivt endnu")


@router.get("/{brobygger_id}", response_model=Brobygger)
def get_brobygger(brobygger_id: str):
    raise HTTPException(503, "Backend ikke aktivt endnu")


@router.patch("/{brobygger_id}", response_model=Brobygger)
def update_brobygger(brobygger_id: str, data: BrobyggerUpdate):
    raise HTTPException(503, "Backend ikke aktivt endnu")
