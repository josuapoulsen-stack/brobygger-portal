"""
Pydantic-modeller for Brobyggere (frivillige).
"""

from __future__ import annotations
from datetime import date, datetime
from typing import Literal, Optional
from pydantic import BaseModel, EmailStr


BrobyggerStatus = Literal["aktiv", "pause", "inaktiv", "ny"]


class BrobyggerBase(BaseModel):
    navn: str
    email: Optional[EmailStr] = None
    telefon: Optional[str] = None
    # Profil
    typer: list[str] = []
    sprog: list[str] = ["dansk"]
    hq: Optional[str] = None
    # Kapacitet
    status: BrobyggerStatus = "ny"
    active: int = 0               # antal aktive forløb
    maxActive: int = 3            # max kapacitet
    # Tilgængelighed
    tilgaengeligFra: Optional[date] = None
    naesteTid: Optional[str] = None   # fx "Tirsdag kl. 14-17"
    # Frivilligdata
    startdato: Optional[date] = None
    senesteMoede: Optional[date] = None
    noter: Optional[str] = None


class BrobyggerUpdate(BaseModel):
    navn: Optional[str] = None
    email: Optional[EmailStr] = None
    telefon: Optional[str] = None
    typer: Optional[list[str]] = None
    sprog: Optional[list[str]] = None
    hq: Optional[str] = None
    status: Optional[BrobyggerStatus] = None
    active: Optional[int] = None
    maxActive: Optional[int] = None
    tilgaengeligFra: Optional[date] = None
    naesteTid: Optional[str] = None
    noter: Optional[str] = None


class Brobygger(BrobyggerBase):
    id: str
    createdAt: datetime

    model_config = {"from_attributes": True}
