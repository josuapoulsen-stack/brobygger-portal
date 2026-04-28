"""
backend/routers/profil.py

GET    /v1/profil/me    → hent egen profil (fra Azure token)
PATCH  /v1/profil/me    → opdatér profil
"""

from fastapi import APIRouter, HTTPException
from ..models.profil import Profil, ProfilUpdate

router = APIRouter(prefix="/v1/profil", tags=["Profil"])


@router.get("/me", response_model=Profil)
def get_my_profile():
    """
    FASE 2:
        # current_user injiceres fra Depends(get_current_user)
        return db.query(BrobyggerORM).filter_by(azure_oid=current_user.oid).first()
    """
    raise HTTPException(503, "Backend ikke aktivt endnu")


@router.patch("/me", response_model=Profil)
def update_my_profile(data: ProfilUpdate):
    raise HTTPException(503, "Backend ikke aktivt endnu")
