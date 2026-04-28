"""
Pydantic-modeller for Profil (brobyggerens egen profil).
"""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, EmailStr


class ProfilBase(BaseModel):
    navn: str
    fornavn: Optional[str] = None
    efternavn: Optional[str] = None
    email: Optional[EmailStr] = None
    mobil: Optional[str] = None
    kon: Optional[str] = None
    hq: Optional[str] = None
    typer: list[str] = []
    sprog: list[str] = ["dansk"]
    bio: Optional[str] = None
    avatarUrl: Optional[str] = None


class ProfilUpdate(BaseModel):
    navn: Optional[str] = None
    fornavn: Optional[str] = None
    efternavn: Optional[str] = None
    email: Optional[EmailStr] = None
    mobil: Optional[str] = None
    kon: Optional[str] = None
    hq: Optional[str] = None
    typer: Optional[list[str]] = None
    sprog: Optional[list[str]] = None
    bio: Optional[str] = None


class Profil(ProfilBase):
    id: str
    azureOid: Optional[str] = None   # Azure Entra ID Object ID

    model_config = {"from_attributes": True}
