"""
Pydantic-modeller for Statistik / SROI.
"""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel


class DashboardStats(BaseModel):
    totalMennesker: int = 0
    totalBrobyggere: int = 0
    totalAftaler: int = 0
    aktiveBrobyggere: int = 0
    matchRate: float = 0.0           # pct. af mennesker der er matchet
    gnsAftBrobygger: float = 0.0     # gns. aftaler per brobygger


class SROISnapshot(BaseModel):
    # Nøgletal til SROI-beregning
    totalForloeb: int = 0
    afsluttedeForloeb: int = 0
    totalTimer: float = 0.0
    estimatedValueDKK: float = 0.0
    investmentDKK: float = 0.0
    sroiRatio: float = 0.0           # value / investment
    # Periode
    fraAar: Optional[int] = None
    tilAar: Optional[int] = None
    hq: Optional[str] = None
