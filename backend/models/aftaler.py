"""
Pydantic-modeller for Aftaler (møder/aktiviteter).

Feltnavne er snake_case og spejler `AftaleORM` + OpenAPI-kontrakten 1:1.
"""

from __future__ import annotations
from datetime import datetime
from typing import Literal, Optional
from uuid import UUID
from pydantic import BaseModel


AftaleStatus = Literal[
    "planlagt", "gennemfoert", "aflyst", "udsat",
    "kladde", "pending", "confirmed", "afslaaet", "brudt",
]
AftaleType = Literal["moede", "aktivitet", "telefonopkald", "online"]


class AftaleBase(BaseModel):
    brobygger_id: UUID
    menneske_id: UUID
    dato: datetime
    varighed: int = 60                    # minutter
    type: AftaleType = "moede"
    sted: Optional[str] = None
    beskrivelse: Optional[str] = None
    status: AftaleStatus = "planlagt"
    notes: str = ""
    # Klassificering (fra stamdata)
    aftaletype: Optional[str] = None
    brobygningstype: Optional[str] = None   # Social | Forening | Sundhed
    henvender: Optional[str] = None
    modtager: Optional[str] = None
    finansiering: Optional[str] = None
    samarbejdspartner: Optional[str] = None
    afdeling: Optional[str] = None
    aflyst_af: Optional[str] = None
    aflysnings_aarsag: Optional[str] = None
    transportplan: Optional[str] = None
    aktivitets_tid: Optional[str] = None
    fremmoede_type: Optional[str] = None
    gentagelse: Optional[str] = None
    aftale_form: Optional[str] = None
    brobygger_note: Optional[str] = None    # briefing til brobygger
    raadgiver_opfoelgning: Optional[str] = None
    # brobyggerLog (udfald af afholdt aftale)
    udfald: Optional[str] = None            # gennemfoert | afbud | ikke-modt
    varighed_min: Optional[int] = None
    log_note: Optional[str] = None
    logged_at: Optional[datetime] = None


class AftaleCreate(AftaleBase):
    pass


class AftaleStatusUpdate(BaseModel):
    status: AftaleStatus
    notes: str = ""


class Aftale(AftaleBase):
    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}
