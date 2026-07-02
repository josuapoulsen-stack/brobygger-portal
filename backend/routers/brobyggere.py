"""
backend/routers/brobyggere.py — CRUD-endpoints for Brobyggere (frivillige)

GET    /v1/brobyggere          → liste (filtrér på status, hq)
GET    /v1/brobyggere/{id}     → enkelt
POST   /v1/brobyggere          → opret
PATCH  /v1/brobyggere/{id}     → opdatér
DELETE /v1/brobyggere/{id}     → slet

I produktion oprettes brobyggere typisk via Azure Entra ID-invitation + onboarding,
men POST bevares til import/seed og koordinator-oprettelse.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..orm_models import BrobyggerORM
from ..models.brobyggere import Brobygger, BrobyggerCreate, BrobyggerUpdate
from .mennesker import normaliser_telefon
from .auth import require_user

router = APIRouter(prefix="/v1/brobyggere", tags=["Brobyggere"], dependencies=[Depends(require_user)])


def _hent(db: Session, brobygger_id: UUID) -> BrobyggerORM:
    obj = db.get(BrobyggerORM, brobygger_id)
    if obj is None:
        raise HTTPException(404, "Brobygger ikke fundet")
    return obj


@router.get("", response_model=list[Brobygger])
def list_brobyggere(
    status: Optional[str] = Query(None, description="Filtrer på status"),
    hq: Optional[str] = Query(None, description="Filtrer på hovedsæde"),
    db: Session = Depends(get_db),
):
    q = db.query(BrobyggerORM)
    if status:
        q = q.filter(BrobyggerORM.status == status)
    if hq:
        q = q.filter(BrobyggerORM.hq == hq)
    return q.order_by(BrobyggerORM.navn).all()


@router.get("/{brobygger_id}", response_model=Brobygger)
def get_brobygger(brobygger_id: UUID, db: Session = Depends(get_db)):
    return _hent(db, brobygger_id)


@router.post("", response_model=Brobygger, status_code=201)
def create_brobygger(data: BrobyggerCreate, db: Session = Depends(get_db)):
    obj = BrobyggerORM(**data.model_dump())
    obj.telefon_norm = normaliser_telefon(obj.telefon)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.patch("/{brobygger_id}", response_model=Brobygger)
def update_brobygger(brobygger_id: UUID, data: BrobyggerUpdate, db: Session = Depends(get_db)):
    obj = _hent(db, brobygger_id)
    changes = data.model_dump(exclude_unset=True)
    for felt, vaerdi in changes.items():
        setattr(obj, felt, vaerdi)
    if "telefon" in changes:
        obj.telefon_norm = normaliser_telefon(obj.telefon)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{brobygger_id}", status_code=204)
def delete_brobygger(brobygger_id: UUID, db: Session = Depends(get_db)):
    obj = _hent(db, brobygger_id)
    db.delete(obj)
    db.commit()
