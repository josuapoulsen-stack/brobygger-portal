"""
Pydantic-modeller for Aftaler (møder/aktiviteter).
"""

from __future__ import annotations
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel


AftaleStatus = Literal["planlagt", "gennemfoert", "aflyst", "udsat"]
AftaleType = Literal["moede", "aktivitet", "telefonopkald", "online"]


class AftaleBase(BaseModel):
    brobyggerId: str
    menneskeId: str
    dato: datetime
    varighed: int = 60              # minutter
    type: AftaleType = "moede"
    sted: Optional[str] = None
    beskrivelse: Optional[str] = None
    status: AftaleStatus = "planlagt"
    notes: str = ""


class AftaleCreate(AftaleBase):
    pass


class AftaleStatusUpdate(BaseModel):
    status: AftaleStatus
    notes: str = ""


class Aftale(AftaleBase):
    id: str
    createdAt: datetime

    model_config = {"from_attributes": True}
