"""
Pydantic-modeller for Brobyggere (frivillige).

Feltnavne er snake_case og spejler `BrobyggerORM` + OpenAPI-kontrakten 1:1.
"""

from __future__ import annotations
from datetime import date, datetime
from typing import Literal, Optional
from uuid import UUID
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
    afdeling: Optional[str] = None
    kon: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    # Kapacitet
    status: BrobyggerStatus = "ny"
    active: int = 0                       # antal aktive forløb
    max_active: int = 3                   # max kapacitet
    # Tilgængelighed
    tilgaengelig_fra: Optional[date] = None
    naeste_tid: Optional[str] = None      # fx "Tirsdag kl. 14-17"
    # Frivilligdata
    startdato: Optional[date] = None
    seneste_moede: Optional[date] = None
    noter: Optional[str] = None


class BrobyggerCreate(BrobyggerBase):
    pass


class BrobyggerUpdate(BaseModel):
    navn: Optional[str] = None
    email: Optional[EmailStr] = None
    telefon: Optional[str] = None
    typer: Optional[list[str]] = None
    sprog: Optional[list[str]] = None
    hq: Optional[str] = None
    afdeling: Optional[str] = None
    kon: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    status: Optional[BrobyggerStatus] = None
    active: Optional[int] = None
    max_active: Optional[int] = None
    tilgaengelig_fra: Optional[date] = None
    naeste_tid: Optional[str] = None
    startdato: Optional[date] = None
    seneste_moede: Optional[date] = None
    noter: Optional[str] = None


class Brobygger(BrobyggerBase):
    id: UUID
    telefon_norm: Optional[str] = None    # kanonisk telefon (read-only, afledt)
    created_at: datetime

    model_config = {"from_attributes": True}
