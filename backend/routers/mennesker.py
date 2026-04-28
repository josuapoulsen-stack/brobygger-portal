"""
backend/routers/mennesker.py — CRUD-endpoints for Mennesker

GET    /v1/mennesker          → liste (filtrér på status, hq)
GET    /v1/mennesker/{id}     → enkelt
POST   /v1/mennesker          → opret
PATCH  /v1/mennesker/{id}     → opdatér
DELETE /v1/mennesker/{id}     → slet (soft-delete i prod)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
# from sqlalchemy.orm import Session
# from ..database import get_db
from ..models.mennesker import Menneske, MenneskCreate, MenneskUpdate

router = APIRouter(prefix="/v1/mennesker", tags=["Mennesker"])


@router.get("", response_model=list[Menneske])
def list_mennesker(
    status: Optional[str] = Query(None, description="Filtrer på status"),
    hq: Optional[str] = Query(None, description="Filtrer på koordinatorkontor"),
    # db: Session = Depends(get_db),  # Aktivér ved FASE 2
):
    """
    Returnér alle mennesker — optionelt filtreret.

    FASE 2: Erstat med DB-query:
        rows = db.query(MenneskORM)
        if status: rows = rows.filter(MenneskORM.status == status)
        if hq:     rows = rows.filter(MenneskORM.hq == hq)
        return rows.all()
    """
    raise HTTPException(503, "Backend ikke aktivt endnu — brug USE_BACKEND=false i src/api/index.js")


@router.get("/{menneske_id}", response_model=Menneske)
def get_menneske(menneske_id: str):
    """
    Hent ét menneske på ID.
    """
    raise HTTPException(503, "Backend ikke aktivt endnu")


@router.post("", response_model=Menneske, status_code=201)
def create_menneske(data: MenneskCreate):
    """
    Opret nyt menneske.

    FASE 2:
        record = MenneskORM(**data.model_dump(), id=str(uuid4()), created_at=utcnow())
        db.add(record); db.commit(); db.refresh(record)
        return record
    """
    raise HTTPException(503, "Backend ikke aktivt endnu")


@router.patch("/{menneske_id}", response_model=Menneske)
def update_menneske(menneske_id: str, data: MenneskUpdate):
    raise HTTPException(503, "Backend ikke aktivt endnu")


@router.delete("/{menneske_id}", status_code=204)
def delete_menneske(menneske_id: str):
    """
    Soft-delete i prod: sæt status = 'slettet' + anonymisér PII efter 30 dage.
    """
    raise HTTPException(503, "Backend ikke aktivt endnu")
