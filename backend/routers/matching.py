"""
backend/routers/matching.py

GET   /v1/matching/suggestions?menneske_id=...  → forslag til brobyggere
POST  /v1/matching/confirm                       → bekræft match
"""

from fastapi import APIRouter, HTTPException, Query
from ..models.matching import MatchSuggestion, MatchConfirm

router = APIRouter(prefix="/v1/matching", tags=["Matching"])


@router.get("/suggestions", response_model=list[MatchSuggestion])
def get_suggestions(menneske_id: str = Query(...)):
    """
    FASE 2 — matchingslogik:
        menneske = db.query(MenneskORM).get(menneske_id)
        kandidater = db.query(BrobyggerORM).filter(
            BrobyggerORM.status == "aktiv",
            BrobyggerORM.active < BrobyggerORM.max_active,
        ).all()
        # Score baseret på overlappende typer + sprog + geografisk nærhed
        scored = [(b, compute_score(menneske, b)) for b in kandidater]
        scored.sort(key=lambda x: -x[1])
        return [MatchSuggestion(brobygger=b, score=s) for b, s in scored[:5]]
    """
    raise HTTPException(503, "Backend ikke aktivt endnu")


@router.post("/confirm")
def confirm_match(data: MatchConfirm):
    """
    FASE 2:
        db.query(MenneskORM).filter_by(id=data.menneske_id).update({
            "matched_with": data.brobygger_id,
            "status": "matched",
        })
        db.query(BrobyggerORM).filter_by(id=data.brobygger_id).update({
            "active": BrobyggerORM.active + 1
        })
        db.commit()
        # Notifikation til begge parter
    """
    raise HTTPException(503, "Backend ikke aktivt endnu")
