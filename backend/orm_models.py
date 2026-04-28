"""
backend/orm_models.py — SQLAlchemy ORM-modeller

Spejler SQL-migrationerne 001–005 præcist.
Bruges af FastAPI-routerne i FASE 2 via Depends(get_db).

Import i routerne:
    from ..orm_models import BrobyggerORM, MenneskORM, AftaleORM, ...

Tilføj til database.py når du aktiverer:
    from .orm_models import Base
    Base.metadata.create_all(bind=engine)  # kun dev — brug alembic i prod
"""

from __future__ import annotations
from datetime import datetime, date
from typing import Optional
from sqlalchemy import (
    Column, String, Integer, Boolean, Float, Text, Date, DateTime,
    ForeignKey, ARRAY, Enum as PgEnum, LargeBinary, BigInteger, JSON,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, BYTEA
from sqlalchemy.orm import relationship, Mapped, mapped_column
import uuid
import enum

from .database import Base


# ── Enums (spejler PostgreSQL ENUM types) ─────────────────────────────────────

class MenneskStatusEnum(str, enum.Enum):
    ny          = "ny"
    matched     = "matched"
    aktiv       = "aktiv"
    afsluttet   = "afsluttet"
    venteliste  = "venteliste"


class BrobyggerStatusEnum(str, enum.Enum):
    ny      = "ny"
    aktiv   = "aktiv"
    pause   = "pause"
    inaktiv = "inaktiv"


class AftaleStatusEnum(str, enum.Enum):
    planlagt      = "planlagt"
    gennemfoert   = "gennemfoert"
    aflyst        = "aflyst"
    udsat         = "udsat"


class AftaleTypeEnum(str, enum.Enum):
    moede          = "moede"
    aktivitet      = "aktivitet"
    telefonopkald  = "telefonopkald"
    online         = "online"


class BrugerRolleEnum(str, enum.Enum):
    Brobygger = "Brobygger"
    Raadgiver = "Raadgiver"
    Admin     = "Admin"


class NotifTypeEnum(str, enum.Enum):
    ny_aftale       = "ny_aftale"
    aftale_godkendt = "aftale_godkendt"
    aftale_aflyst   = "aftale_aflyst"
    ny_besked       = "ny_besked"
    match_forslag   = "match_forslag"
    paamindelse     = "paamindelse"
    system          = "system"


# ═══════════════════════════════════════════════════════════════════════════════
# BROBYGGERE
# ═══════════════════════════════════════════════════════════════════════════════

class BrobyggerORM(Base):
    __tablename__ = "brobyggere"

    id              = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    azure_oid       = Column(String, unique=True, nullable=True)
    navn            = Column(String, nullable=False)
    email           = Column(String, nullable=True)
    telefon         = Column(String, nullable=True)
    typer           = Column(ARRAY(String), nullable=False, default=list)
    sprog           = Column(ARRAY(String), nullable=False, default=lambda: ["dansk"])
    hq              = Column(String, nullable=True)
    kon             = Column(String, nullable=True)
    bio             = Column(Text, nullable=True)
    avatar_url      = Column(String, nullable=True)
    status          = Column(PgEnum(BrobyggerStatusEnum, name="brobygger_status"), nullable=False, default=BrobyggerStatusEnum.ny)
    active          = Column(Integer, nullable=False, default=0)
    max_active      = Column(Integer, nullable=False, default=3)
    tilgaengelig_fra = Column(Date, nullable=True)
    naeste_tid      = Column(String, nullable=True)
    startdato       = Column(Date, nullable=True)
    seneste_moede   = Column(Date, nullable=True)
    noter           = Column(Text, nullable=True)
    created_at      = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at      = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())

    # Relations
    aftaler         = relationship("AftaleORM",     back_populates="brobygger")
    mennesker       = relationship("MenneskORM",    back_populates="brobygger", foreign_keys="MenneskORM.matched_with")


# ═══════════════════════════════════════════════════════════════════════════════
# BRUGERE (medarbejdere — Entra ID-baserede)
# ═══════════════════════════════════════════════════════════════════════════════

class BrugerORM(Base):
    __tablename__ = "brugere"

    id              = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    azure_oid       = Column(String, unique=True, nullable=False)
    display_name    = Column(String, nullable=False)
    email           = Column(String, nullable=True)
    rolle           = Column(PgEnum(BrugerRolleEnum, name="bruger_rolle"), nullable=False)
    hq              = Column(String, nullable=True)
    aktiv           = Column(Boolean, nullable=False, default=True)
    sidst_login     = Column(DateTime(timezone=True), nullable=True)
    created_at      = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at      = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())

    # Relations
    mennesker       = relationship("MenneskORM", back_populates="raadgiver", foreign_keys="MenneskORM.raadgiver_id")
    notifikationer  = relationship("NotifikationORM", back_populates="bruger")
    push_subs       = relationship("PushSubscriptionORM", back_populates="bruger", cascade="all, delete-orphan")


# ═══════════════════════════════════════════════════════════════════════════════
# MENNESKER
# ═══════════════════════════════════════════════════════════════════════════════

class MenneskORM(Base):
    __tablename__ = "mennesker"

    id                  = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    navn                = Column(String, nullable=False)
    alder               = Column(Integer, nullable=True)
    kon                 = Column(String, nullable=True)
    email               = Column(String, nullable=True)
    telefon             = Column(String, nullable=True)
    adresse             = Column(String, nullable=True)
    typer               = Column(ARRAY(String), nullable=False, default=list)
    sprog               = Column(ARRAY(String), nullable=False, default=lambda: ["dansk"])
    noter               = Column(Text, nullable=True)
    helbredsnoter_enc   = Column(BYTEA, nullable=True)   # pgp_sym_encrypt — Art. 9
    status              = Column(PgEnum(MenneskStatusEnum, name="menneske_status"), nullable=False, default=MenneskStatusEnum.ny)
    matched_with        = Column(PG_UUID(as_uuid=True), ForeignKey("brobyggere.id"), nullable=True)
    raadgiver_id        = Column(PG_UUID(as_uuid=True), ForeignKey("brugere.id"), nullable=True)
    hq                  = Column(String, nullable=True)
    created_at          = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at          = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())
    deleted_at          = Column(DateTime(timezone=True), nullable=True)
    anonymized_at       = Column(DateTime(timezone=True), nullable=True)

    # Relations
    brobygger   = relationship("BrobyggerORM", back_populates="mennesker", foreign_keys=[matched_with])
    raadgiver   = relationship("BrugerORM",    back_populates="mennesker", foreign_keys=[raadgiver_id])
    aftaler     = relationship("AftaleORM",    back_populates="menneske")
    samtykker   = relationship("SamtykkeORM",  back_populates="menneske", cascade="all, delete-orphan")

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


# ═══════════════════════════════════════════════════════════════════════════════
# AFTALER
# ═══════════════════════════════════════════════════════════════════════════════

class AftaleORM(Base):
    __tablename__ = "aftaler"

    id              = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brobygger_id    = Column(PG_UUID(as_uuid=True), ForeignKey("brobyggere.id"), nullable=False)
    menneske_id     = Column(PG_UUID(as_uuid=True), ForeignKey("mennesker.id"), nullable=False)
    dato            = Column(DateTime(timezone=True), nullable=False)
    varighed        = Column(Integer, nullable=False, default=60)
    type            = Column(PgEnum(AftaleTypeEnum, name="aftale_type"), nullable=False, default=AftaleTypeEnum.moede)
    sted            = Column(String, nullable=True)
    beskrivelse     = Column(Text, nullable=True)
    status          = Column(PgEnum(AftaleStatusEnum, name="aftale_status"), nullable=False, default=AftaleStatusEnum.planlagt)
    notes           = Column(Text, nullable=False, default="")
    created_at      = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at      = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())

    # Relations
    brobygger   = relationship("BrobyggerORM", back_populates="aftaler")
    menneske    = relationship("MenneskORM",   back_populates="aftaler")


# ═══════════════════════════════════════════════════════════════════════════════
# BESKEDER
# ═══════════════════════════════════════════════════════════════════════════════

class BeskedTraadORM(Base):
    __tablename__ = "besked_traade"

    id              = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    titel           = Column(String, nullable=False)
    brobygger_id    = Column(PG_UUID(as_uuid=True), ForeignKey("brobyggere.id"), nullable=True)
    from_brobygger  = Column(Boolean, nullable=False, default=False)
    official        = Column(Boolean, nullable=False, default=False)
    ulaest_count    = Column(Integer, nullable=False, default=0)
    sidste_besked   = Column(Text, nullable=True)
    created_at      = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at      = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())

    # Relations
    beskeder    = relationship("BeskedORM", back_populates="traad", cascade="all, delete-orphan",
                               order_by="BeskedORM.sent_at")


class BeskedORM(Base):
    __tablename__ = "beskeder"

    id              = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    traad_id        = Column(PG_UUID(as_uuid=True), ForeignKey("besked_traade.id", ondelete="CASCADE"), nullable=False)
    from_rolle      = Column(PgEnum(BrugerRolleEnum, name="bruger_rolle"), nullable=False)
    fra_bruger_id   = Column(PG_UUID(as_uuid=True), ForeignKey("brugere.id"), nullable=True)
    tekst           = Column(Text, nullable=False)
    sent_at         = Column(DateTime(timezone=True), nullable=False, default=func.now())
    laest_af        = Column(ARRAY(PG_UUID(as_uuid=True)), nullable=True, default=list)
    signalr_msg_id  = Column(String, nullable=True)

    # Relations
    traad       = relationship("BeskedTraadORM", back_populates="beskeder")
    afsender    = relationship("BrugerORM", foreign_keys=[fra_bruger_id])


# ═══════════════════════════════════════════════════════════════════════════════
# NOTIFIKATIONER
# ═══════════════════════════════════════════════════════════════════════════════

class NotifikationORM(Base):
    __tablename__ = "notifikationer"

    id              = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bruger_id       = Column(PG_UUID(as_uuid=True), ForeignKey("brugere.id"), nullable=False)
    type            = Column(PgEnum(NotifTypeEnum, name="notif_type"), nullable=False)
    titel           = Column(String, nullable=False)
    tekst           = Column(Text, nullable=False)
    link            = Column(String, nullable=True)
    unread          = Column(Boolean, nullable=False, default=True)
    push_sendt      = Column(Boolean, nullable=False, default=False)
    push_sendt_at   = Column(DateTime(timezone=True), nullable=True)
    created_at      = Column(DateTime(timezone=True), nullable=False, default=func.now())

    # Relations
    bruger      = relationship("BrugerORM", back_populates="notifikationer")


# ═══════════════════════════════════════════════════════════════════════════════
# WEB PUSH SUBSCRIPTIONS
# ═══════════════════════════════════════════════════════════════════════════════

class PushSubscriptionORM(Base):
    __tablename__ = "push_subscriptions"

    id          = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bruger_id   = Column(PG_UUID(as_uuid=True), ForeignKey("brugere.id"), nullable=False)
    endpoint    = Column(Text, nullable=False, unique=True)
    p256dh      = Column(Text, nullable=False)
    auth_key    = Column(Text, nullable=False)
    user_agent  = Column(Text, nullable=True)
    created_at  = Column(DateTime(timezone=True), nullable=False, default=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)

    # Relations
    bruger      = relationship("BrugerORM", back_populates="push_subs")


# ═══════════════════════════════════════════════════════════════════════════════
# MAGIC LINK INVITATIONS
# ═══════════════════════════════════════════════════════════════════════════════

class InvitationORM(Base):
    __tablename__ = "invitations"

    id          = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email       = Column(String, nullable=False)
    navn        = Column(String, nullable=False)
    hq          = Column(String, nullable=True)
    token_hash  = Column(String, nullable=False, unique=True)   # sha256 af token
    sendt_af    = Column(PG_UUID(as_uuid=True), ForeignKey("brugere.id"), nullable=True)
    expires_at  = Column(DateTime(timezone=True), nullable=False)
    brugt       = Column(Boolean, nullable=False, default=False)
    brugt_at    = Column(DateTime(timezone=True), nullable=True)
    created_at  = Column(DateTime(timezone=True), nullable=False, default=func.now())


# ═══════════════════════════════════════════════════════════════════════════════
# SAMTYKKE (GDPR Art. 6 + 9)
# ═══════════════════════════════════════════════════════════════════════════════

class SamtykkeORM(Base):
    __tablename__ = "samtykker"

    id              = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    menneske_id     = Column(PG_UUID(as_uuid=True), ForeignKey("mennesker.id"), nullable=False)
    version         = Column(String, nullable=False)   # fx "2025-01-01"
    givet_af        = Column(String, nullable=True)    # navn på den der indhentede samtykke
    helbredsdata    = Column(Boolean, nullable=False, default=False)  # Art. 9-samtykke
    kontakt_data    = Column(Boolean, nullable=False, default=True)
    ip_adresse      = Column(String, nullable=True)
    enhed           = Column(String, nullable=True)    # user-agent
    trukket_tilbage = Column(Boolean, nullable=False, default=False)
    trukket_at      = Column(DateTime(timezone=True), nullable=True)
    created_at      = Column(DateTime(timezone=True), nullable=False, default=func.now())

    # Relations
    menneske    = relationship("MenneskORM", back_populates="samtykker")
