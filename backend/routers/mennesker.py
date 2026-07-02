"""
backend/routers/mennesker.py — CRUD-endpoints for Mennesker

GET    /v1/mennesker          → liste (filtrér på status, hq)
GET    /v1/mennesker/{id}     → enkelt
POST   /v1/mennesker          → opret
PATCH  /v1/mennesker/{id}     → opdatér
DELETE /v1/mennesker/{id}     → soft-delete (deleted_at sættes)

GDPR Art. 9: `helbredsnoter` modtages write-only og krypteres server-side til
`helbredsnoter_enc`. Krypteringen (pgcrypto pgp_sym_encrypt) er endnu IKKE koblet
på — feltet ignoreres derfor indtil da, så der aldrig gemmes helbredsdata i klartekst.
"""

import re
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..orm_models import MenneskORM
from ..models.mennesker import Menneske, MenneskCreate, MenneskUpdate

router = APIRouter(prefix="/v1/mennesker", tags=["Mennesker"])


def normaliser_telefon(raw: Optional[str]) -> Optional[str]:
    """Kanonisk dansk telefon: kun cifre, uden +45/0045-landekode. Bruges til genkendelse."""
    if not raw:
        return None
    d = re.sub(r"\D", "", raw)
    if d.startswith("0045"):
        d = d[4:]
    elif d.startswith("45") and len(d) == 10:
        d = d[2:]
    return d or None


def _hent(db: Session, menneske_id: UUID) -> MenneskORM:
    obj = db.get(MenneskORM, menneske_id)
    if obj is None or obj.deleted_at is not None:
        raise HTTPException(404, "Menneske ikke fundet")
    return obj


@router.get("", response_model=list[Menneske])
def list_mennesker(
    status: Optional[str] = Query(None, description="Filtrer på status"),
    hq: Optional[str] = Query(None, description="Filtrer på koordinatorkontor"),
    db: Session = Depends(get_db),
):
    q = db.query(MenneskORM).filter(MenneskORM.deleted_at.is_(None))
    if status:
        q = q.filter(MenneskORM.status == status)
    if hq:
        q = q.filter(MenneskORM.hq == hq)
    return q.order_by(MenneskORM.created_at.desc()).all()


@router.get("/{menneske_id}", response_model=Menneske)
def get_menneske(menneske_id: UUID, db: Session = Depends(get_db)):
    return _hent(db, menneske_id)


@router.post("", response_model=Menneske, status_code=201)
def create_menneske(data: MenneskCreate, db: Session = Depends(get_db)):
    payload = data.model_dump(exclude={"helbredsnoter"})
    obj = MenneskORM(**payload)
    obj.telefon_norm = normaliser_telefon(obj.telefon)
    # TODO (Art. 9): krypter data.helbredsnoter → obj.helbredsnoter_enc via pgcrypto
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.patch("/{menneske_id}", response_model=Menneske)
def update_menneske(menneske_id: UUID, data: MenneskUpdate, db: Session = Depends(get_db)):
    obj = _hent(db, menneske_id)
    changes = data.model_dump(exclude_unset=True, exclude={"helbredsnoter"})
    for felt, vaerdi in changes.items():
        setattr(obj, felt, vaerdi)
    if "telefon" in changes:
        obj.telefon_norm = normaliser_telefon(obj.telefon)
    # TODO (Art. 9): hvis data.helbredsnoter er sat → krypter til obj.helbredsnoter_enc
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{menneske_id}", status_code=204)
def delete_menneske(menneske_id: UUID, db: Session = Depends(get_db)):
    """Soft-delete: sæt deleted_at. Anonymisering af PII sker via batch-job efter 30 dage."""
    from datetime import datetime, timezone
    obj = _hent(db, menneske_id)
    obj.deleted_at = datetime.now(timezone.utc)
    obj.status = "afsluttet"
    db.commit()
