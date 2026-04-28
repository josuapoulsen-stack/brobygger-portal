"""
Pydantic-modeller for Matching.
"""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel
from .brobyggere import Brobygger


class MatchSuggestion(BaseModel):
    brobygger: Brobygger
    score: float = 1.0            # 0.0–1.0, simpel lokal logik i FASE 1
    begrundelse: Optional[str] = None


class MatchConfirm(BaseModel):
    menneske_id: str
    brobygger_id: str
