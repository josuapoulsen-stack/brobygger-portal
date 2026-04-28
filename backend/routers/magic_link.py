"""
backend/routers/magic_link.py — Magic link-login til brobyggere

Flow:
  1. Koordinator inviterer brobygger via POST /v1/auth/invite
     → generér signeret token (itsdangerous, 48t udløb)
     → send email med link: https://[app]/login?token=<token>

  2. Brobygger klikker link → app kalder POST /v1/auth/magic?token=<token>
     → valider token → opret/hent bruger → returnér JWT-session-token

  3. Frontend gemmer session-token i localStorage (30–90 dages udløb)
     → token sendes som Authorization: Bearer ved hvert API-kald

  4. Ved hvert app-start: stil GET /v1/auth/me
     → 200: session gyldig
     → 401: vis "Log ind"-knap (koordinator re-inviterer)

GDPR: invitation-tokens er personhenførbare → slettes ved brug eller udløb
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta, timezone
from typing import Optional
import secrets

# itsdangerous til signerede tokens (tidsbegrænsede)
# from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
# from ..config import settings
# from ..database import get_db

router = APIRouter(prefix="/v1/auth", tags=["Auth — Magic Link"])

# ── Token-signer (FASE 2: erstat secret med settings.JWT_SECRET) ──────────────
# signer = URLSafeTimedSerializer(settings.JWT_SECRET, salt="magic-link")

LINK_EXPIRY_HOURS = 48


class InviteRequest(BaseModel):
    email: EmailStr
    navn: str
    hq: Optional[str] = None
    besked: Optional[str] = None    # personlig hilsen i invitationsmail


class InviteResponse(BaseModel):
    ok: bool
    email: str
    expires_at: str                 # ISO-timestamp — til visning i UI


class MagicLinkResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int                 # sekunder
    rolle: str
    navn: str


@router.post("/invite", response_model=InviteResponse)
def invite_brobygger(data: InviteRequest):
    """
    Opret og send invitations-magic-link til en ny brobygger.

    Kræver rollen Raadgiver eller Admin.

    FASE 2:
        # Generer token
        token = signer.dumps(data.email)

        # Gem invitation i DB med udløbsdato
        invite = InvitationORM(
            email=data.email,
            navn=data.navn,
            hq=data.hq,
            token_hash=hashlib.sha256(token.encode()).hexdigest(),
            expires_at=utcnow() + timedelta(hours=LINK_EXPIRY_HOURS),
            sendt_af=current_user.id,
        )
        db.add(invite); db.commit()

        # Send email via Exchange Online (Microsoft Graph)
        link = f"{settings.FRONTEND_URL}/login?token={token}"
        await send_magic_link_email(
            to=data.email,
            navn=data.navn,
            link=link,
            besked=data.besked,
        )

        return InviteResponse(
            ok=True,
            email=data.email,
            expires_at=(utcnow() + timedelta(hours=LINK_EXPIRY_HOURS)).isoformat(),
        )
    """
    raise HTTPException(503, "Backend ikke aktivt endnu")


@router.post("/magic", response_model=MagicLinkResponse)
def verify_magic_link(token: str = Query(..., description="Magic link-token fra email")):
    """
    Valider magic link-token og returnér session-JWT til frontenden.

    FASE 2:
        # Valider signatur + udløb
        try:
            email = signer.loads(token, max_age=LINK_EXPIRY_HOURS * 3600)
        except SignatureExpired:
            raise HTTPException(410, "Linket er udløbet — bed din koordinator om et nyt")
        except BadSignature:
            raise HTTPException(401, "Ugyldigt link")

        # Find eller opret brobygger
        bruger = db.query(BrugerORM).filter_by(email=email).first()
        if not bruger:
            raise HTTPException(404, "Ingen invitation fundet for denne email")

        # Markér token som brugt (forhindre genbrug)
        invitation = db.query(InvitationORM).filter_by(email=email, brugt=False).first()
        invitation.brugt = True
        bruger.sidst_login = utcnow()
        db.commit()

        # Udsted JWT-session (30 dage)
        access_token = create_session_jwt(bruger, expires_days=30)
        return MagicLinkResponse(
            access_token=access_token,
            expires_in=30 * 24 * 3600,
            rolle="brobygger",
            navn=bruger.display_name,
        )
    """
    raise HTTPException(503, "Backend ikke aktivt endnu")


@router.post("/refresh", response_model=MagicLinkResponse)
def refresh_session():
    """
    Forny session-token inden udløb (stille fornyelse i baggrunden).

    Kald dette fra frontenden 7 dage før token udløber.
    """
    raise HTTPException(503, "Backend ikke aktivt endnu")
