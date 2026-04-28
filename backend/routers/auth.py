"""
backend/routers/auth.py — Azure Entra ID JWT-validering

I FASE 2 validerer backend hvert API-kald mod Azure Entra ID's JWKS-endpoint.
Frontend (MSAL.js) henter token og sender det som:
    Authorization: Bearer <access_token>

Endpoints:
    GET  /v1/auth/me   → dekodede claims (oid, name, roles, email)
    POST /v1/auth/logout → (informativt — token-invalidering sker i Entra ID)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
import httpx
from jose import jwt, jwk, JWTError
from jose.utils import base64url_decode
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


async def _get_jwks() -> dict:
    global _jwks_cache
    if _jwks_cache is None:
        async with httpx.AsyncClient() as client:
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


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> TokenClaims:
    """
    FastAPI-dependency: validerer Bearer-token og returnerer claims.

    Brug i routes:
        @router.get("/beskyttet")
        def beskyttet(user: TokenClaims = Depends(get_current_user)):
            ...
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mangler Authorization-header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # TODO (FASE 2): Valider mod Microsoft JWKS
    # jwks = await _get_jwks()
    # claims = jwt.decode(
    #     token,
    #     jwks,
    #     algorithms=["RS256"],
    #     audience=settings.AZURE_CLIENT_ID,
    #     issuer=ENTRA_ISSUER,
    # )

    # FASE 1-stub: Dekodér uden validering (KUN til lokal dev)
    try:
        claims = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_exp": True},
        )
        return TokenClaims(**claims)
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Ugyldigt token: {e}",
        )


@router.get("/me", response_model=TokenClaims)
async def get_me(user: TokenClaims = Depends(get_current_user)):
    """Returnér de dekodede claims for det aktuelle token."""
    return user


@router.post("/logout")
async def logout():
    """
    Klient-side logout: MSAL.js kalder msalInstance.logout().
    Server-side har ingen session at invalidere (stateless JWT).
    """
    return {"message": "Log ud via MSAL.js på klienten."}
