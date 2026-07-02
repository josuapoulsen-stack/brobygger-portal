"""
backend/routers/auth.py — Azure Entra ID JWT-validering + rolle-dependencies

Backend validerer hvert beskyttet API-kald mod Azure Entra ID's JWKS-endpoint
(RS256). Frontend (MSAL.js) henter et access token og sender det som:
    Authorization: Bearer <access_token>

To valideringsveje:
  • Entra konfigureret (AZURE_TENANT_ID/CLIENT_ID sat) → ægte RS256 JWKS-validering
    (signatur + issuer + audience). Dette er produktionsvejen.
  • Entra IKKE konfigureret + ENVIRONMENT != production → HS256 dev-token
    (udstedes af /v1/auth/dev-token) så testsystemet kan bruges før Entra er sat op.
    Denne vej er umulig i produktion: startup-vagten i config.py nægter at boote
    prod med HS256/TODO-config.

Dependencies til brug i routere:
    require_user            → kræver et gyldigt token (enhver rolle)
    require_roles("Admin")  → kræver en af de angivne app-roller

Endpoints:
    GET  /v1/auth/me         → dekodede claims (oid, name, roles, email)
    POST /v1/auth/logout     → informativt (token-invalidering sker i Entra ID)
    POST /v1/auth/dev-token  → dev-only: mint testtoken (404 i prod / når Entra er sat op)
"""

from datetime import datetime, timedelta, timezone
from typing import Callable, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel

from ..config import settings

router = APIRouter(prefix="/v1/auth", tags=["Auth"])
bearer_scheme = HTTPBearer(auto_error=False)

# ── JWKS-cache (Microsoft roterer nøgler sjældent) ───────────────────────────
_jwks_cache: Optional[dict] = None

ENTRA_JWKS_URL = (
    f"https://login.microsoftonline.com/{settings.AZURE_TENANT_ID}"
    "/discovery/v2.0/keys"
)
ENTRA_ISSUER = (
    f"https://login.microsoftonline.com/{settings.AZURE_TENANT_ID}/v2.0"
)


def _entra_configured() -> bool:
    """True når Azure Entra ID er sat op (rigtige tenant/client-IDs)."""
    return not (
        settings.AZURE_TENANT_ID.startswith("TODO")
        or settings.AZURE_CLIENT_ID.startswith("TODO")
    )


def _valid_audiences() -> set[str]:
    cid = settings.AZURE_CLIENT_ID
    return {cid, f"api://{cid}"}


async def _get_jwks(force_refresh: bool = False) -> dict:
    global _jwks_cache
    if _jwks_cache is None or force_refresh:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(ENTRA_JWKS_URL)
            resp.raise_for_status()
            _jwks_cache = resp.json()
    return _jwks_cache


class TokenClaims(BaseModel):
    oid: str                    # Azure Object ID — stabil bruger-ID
    name: Optional[str] = None
    email: Optional[str] = None
    roles: list[str] = []       # ["Brobygger"] | ["Raadgiver"] | ["Admin"]
    preferred_username: Optional[str] = None


async def _decode_entra(token: str) -> dict:
    """Valider et Entra-access-token mod Microsofts JWKS (RS256)."""
    try:
        kid = jwt.get_unverified_header(token).get("kid")
    except JWTError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, f"Ugyldigt token-header: {e}")

    jwks = await _get_jwks()
    key = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
    if key is None:
        # Nøglen kan være roteret — hent JWKS frisk én gang
        jwks = await _get_jwks(force_refresh=True)
        key = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
    if key is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token-nøgle (kid) findes ikke i Entra JWKS")

    try:
        claims = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            issuer=ENTRA_ISSUER,
            options={"verify_aud": False},  # audience tjekkes manuelt mod begge gyldige former
        )
    except JWTError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, f"Token afvist: {e}")

    if claims.get("aud") not in _valid_audiences():
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token har forkert audience")
    return claims


def _decode_dev(token: str) -> dict:
    """Dev-only: dekodér et HS256 testtoken. Aldrig aktiv i produktion."""
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, f"Ugyldigt dev-token: {e}")


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> TokenClaims:
    """FastAPI-dependency: validér Bearer-token og returnér claims."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mangler Authorization-header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    if _entra_configured():
        claims = await _decode_entra(token)
    elif settings.ENVIRONMENT != "production":
        claims = _decode_dev(token)
    else:
        # Uopnåeligt i praksis: startup-vagten blokerer prod uden Entra
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Auth ikke konfigureret (Entra mangler i produktion)",
        )

    try:
        return TokenClaims(**claims)
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token mangler påkrævede claims (oid)")


# ── Genbrugelige autorisations-dependencies ──────────────────────────────────
require_user = get_current_user


def require_roles(*allowed: str) -> Callable:
    """Dependency-factory: kræver at brugeren har mindst én af de angivne app-roller."""
    async def _dep(user: TokenClaims = Depends(get_current_user)) -> TokenClaims:
        if not (set(user.roles) & set(allowed)):
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail=f"Kræver rolle: {' | '.join(allowed)}",
            )
        return user
    return _dep


@router.get("/me", response_model=TokenClaims)
async def get_me(user: TokenClaims = Depends(get_current_user)):
    """Returnér de dekodede claims for det aktuelle token."""
    return user


@router.post("/logout")
async def logout():
    """Klient-side logout: MSAL.js kalder msalInstance.logout(). Stateless JWT server-side."""
    return {"message": "Log ud via MSAL.js på klienten."}


# ── Dev-only: mint et testtoken så testsystemet kan bruges før Entra er sat op ─
class DevTokenRequest(BaseModel):
    oid: str = "dev-00000000-0000-0000-0000-000000000001"
    name: str = "Dev Bruger"
    email: Optional[str] = None
    roles: list[str] = ["Admin"]


@router.post("/dev-token")
async def dev_token(req: DevTokenRequest):
    """
    Udsteder et kortlivet HS256-testtoken. Returnerer 404 i produktion OG når
    Entra er konfigureret — så snart rigtig login er sat op, findes vejen ikke.
    """
    if settings.ENVIRONMENT == "production" or _entra_configured():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ikke tilgængelig")

    now = datetime.now(timezone.utc)
    payload = {
        "oid": req.oid,
        "name": req.name,
        "email": req.email,
        "roles": req.roles,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }
