"""
backend/routers/statistik.py

GET /v1/statistik/dashboard?hq=   → nøgletal til dashboard
GET /v1/statistik/sroi?hq=        → SROI-snapshot
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..models.statistik import DashboardStats, SROISnapshot

router = APIRouter(prefix="/v1/statistik", tags=["Statistik"])


@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard(hq: Optional[str] = Query(None)):
    """
    FASE 2:
        q = db.query(...)
        if hq: q = q.filter_by(hq=hq)
        return DashboardStats(
            totalMennesker=q.count(),
            ...
        )
    """
    raise HTTPException(503, "Backend ikke aktivt endnu")


@router.get("/sroi", response_model=SROISnapshot)
def get_sroi(hq: Optional[str] = Query(None)):
    """
    FASE 2:
        # Beregn SROI-metrics fra aftaler + forløbsdata
        # Investering: lønkroner til koordinatorer + driftsudgifter
        # Effekt: anslået værdi af frivilligtimer + kvalitative indikatorer
    """
    raise HTTPException(503, "Backend ikke aktivt endnu")
