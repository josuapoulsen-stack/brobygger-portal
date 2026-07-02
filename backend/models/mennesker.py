"""
Pydantic-modeller for Mennesker (borgere/klienter).

Feltnavne er snake_case og spejler ORM'en (`MenneskORM`) + OpenAPI-kontrakten
1:1, så `from_attributes` kan fylde response-modellen direkte fra en ORM-række.

GDPR Art. 9: `helbredsnoter` er WRITE-ONLY — den modtages ved oprettelse/opdatering
(krypteres server-side til `helbredsnoter_enc`) men returneres ALDRIG i klartekst.
"""

from __future__ import annotations
from datetime import datetime
from typing import Literal, Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr


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
    typer: list[str] = []
    sprog: list[str] = ["dansk"]
    noter: Optional[str] = None
    # Status og relationer
    status: MenneskStatus = "ny"
    matched_with: Optional[UUID] = None      # brobygger-ID
    raadgiver_id: Optional[UUID] = None      # koordinator (bruger)
    hq: Optional[str] = None
    afdeling: Optional[str] = None
    # Klassificering / rapportering
    kilde: Optional[str] = None              # henvisningskilde
    meetpoint: Optional[str] = None
    sroi_maalgruppe: Optional[str] = None
    helbreds_kategorier: Optional[list[str]] = None
    praeferencer: Optional[dict] = None
    afslut_trivsel: Optional[int] = None
    afslut_aarsag: Optional[str] = None
    ucla_fravalgt: bool = False


class MenneskCreate(MenneskBase):
    # Write-only — krypteres server-side, ekkoes aldrig tilbage
    helbredsnoter: Optional[str] = None


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
    matched_with: Optional[UUID] = None
    raadgiver_id: Optional[UUID] = None
    hq: Optional[str] = None
    afdeling: Optional[str] = None
    kilde: Optional[str] = None
    meetpoint: Optional[str] = None
    sroi_maalgruppe: Optional[str] = None
    helbreds_kategorier: Optional[list[str]] = None
    praeferencer: Optional[dict] = None
    afslut_trivsel: Optional[int] = None
    afslut_aarsag: Optional[str] = None
    ucla_fravalgt: Optional[bool] = None
    helbredsnoter: Optional[str] = None       # write-only


class Menneske(MenneskBase):
    id: UUID
    telefon_norm: Optional[str] = None        # kanonisk telefon (read-only, afledt)
    created_at: datetime

    model_config = {"from_attributes": True}
