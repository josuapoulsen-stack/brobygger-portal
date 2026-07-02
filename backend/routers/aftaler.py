"""
backend/routers/aftaler.py — CRUD-endpoints for Aftaler (møder/aktiviteter)

GET    /v1/aftaler                    → liste (filter: brobygger_id, menneske_id, status)
GET    /v1/aftaler/{id}               → enkelt
POST   /v1/aftaler                    → opret (kapacitetstjek på brobygger)
PATCH  /v1/aftaler/{id}/status        → opdatér status + noter
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..orm_models import AftaleORM, BrobyggerORM, MenneskORM
from ..models.aftaler import Aftale, AftaleCreate, AftaleStatusUpdate
from .auth import require_user

router = APIRouter(prefix="/v1/aftaler", tags=["Aftaler"], dependencies=[Depends(require_user)])

# Statusser der tæller som et "aktivt forløb" på brobyggeren
AKTIVE_STATUS = {"planlagt", "pending", "confirmed"}


def _hent(db: Session, aftale_id: UUID) -> AftaleORM:
    obj = db.get(AftaleORM, aftale_id)
    if obj is None:
        raise HTTPException(404, "Aftale ikke fundet")
    return obj


@router.get("", response_model=list[Aftale])
def list_aftaler(
    brobygger_id: Optional[UUID] = Query(None),
    menneske_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(AftaleORM)
    if brobygger_id:
        q = q.filter(AftaleORM.brobygger_id == brobygger_id)
    if menneske_id:
        q = q.filter(AftaleORM.menneske_id == menneske_id)
    if status:
        q = q.filter(AftaleORM.status == status)
    return q.order_by(AftaleORM.dato.desc()).all()


@router.get("/{aftale_id}", response_model=Aftale)
def get_aftale(aftale_id: UUID, db: Session = Depends(get_db)):
    return _hent(db, aftale_id)


@router.post("", response_model=Aftale, status_code=201)
def create_aftale(data: AftaleCreate, db: Session = Depends(get_db)):
    brobygger = db.get(BrobyggerORM, data.brobygger_id)
    if brobygger is None:
        raise HTTPException(404, "Brobygger ikke fundet")
    if db.get(MenneskORM, data.menneske_id) is None:
        raise HTTPException(404, "Menneske ikke fundet")
    if data.status in AKTIVE_STATUS and brobygger.active >= brobygger.max_active:
        raise HTTPException(409, "Brobygger har ikke kapacitet")

    obj = AftaleORM(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    # TODO (SSE): push "ny_aftale"-event til brobygger via egen backend-stream
    return obj


@router.patch("/{aftale_id}/status", response_model=Aftale)
def update_aftale_status(aftale_id: UUID, data: AftaleStatusUpdate, db: Session = Depends(get_db)):
    obj = _hent(db, aftale_id)
    obj.status = data.status
    if data.notes:
        obj.notes = data.notes
    db.commit()
    db.refresh(obj)
    return obj
