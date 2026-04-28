"""
Pydantic-modeller for Beskeder og Tråde.
"""

from __future__ import annotations
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel


class Thread(BaseModel):
    id: str
    titel: str
    sidstebesked: Optional[str] = None
    ulaest: int = 0
    fromBrobygger: bool = False
    official: bool = False
    updatedAt: datetime

    model_config = {"from_attributes": True}


class Message(BaseModel):
    id: str
    threadId: str
    from_role: Literal["brobygger", "raadgiver", "admin"]
    text: str
    time: str          # "HH:MM" — præsentationsformat
    sentAt: datetime

    model_config = {"from_attributes": True}


class MessageCreate(BaseModel):
    text: str
    from_role: Literal["brobygger", "raadgiver", "admin"]
