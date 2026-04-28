"""
Pydantic-modeller for Mennesker (borgere/klienter).

Felter spejler prototype-globals (window.SoS_MENNESKER).
"""

from __future__ import annotations
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, field_validator


MenneskStatus = Literal["ny", "matched", "aktiv", "afsluttet", "venteliste"]
KonType = Literal["mand", "kvinde", "ikke-binær", "ønsker ikke at oplyse"]


class MenneskBase(BaseModel):
    navn: str
    alder: Optional[int] = None
    kon: Optional[KonType] = None
    email: Optional[EmailStr] = None
    telefon: Optional[str] = None
    adresse: Optional[str] = None
    # Behov og kontekst
    typer: list[str] = []          # samme type-liste som brobyggere
    sprog: list[str] = ["dansk"]
    noter: Optional[str] = None
    # Status
    status: MenneskStatus = "ny"
    matchedWith: Optional[str] = None   # brobygger ID
    # Helbred (GDPR Art. 9 — krypteres i DB)
    helbredsnoter: Optional[str] = None
    # Koordinator
    raaadgiverId: Optional[str] = None
    hq: Optional[str] = None


class MenneskCreate(MenneskBase):
    pass


class MenneskUpdate(BaseModel):
    navn: Optional[str] = None
    alder: Optional[int] = None
    kon: Optional[KonType] = None
    email: Optional[EmailStr] = None
    telefon: Optional[str] = None
    adresse: Optional[str] = None
    typer: Optional[list[str]] = None
    sprog: Optional[list[str]] = None
    noter: Optional[str] = None
    status: Optional[MenneskStatus] = None
    matchedWith: Optional[str] = None
    helbredsnoter: Optional[str] = None
    raaadgiverId: Optional[str] = None
    hq: Optional[str] = None


class Menneske(MenneskBase):
    id: str
    createdAt: datetime

    model_config = {"from_attributes": True}
