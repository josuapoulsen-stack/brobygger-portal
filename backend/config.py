"""
backend/config.py — Konfiguration via environment variables

Alle variabler defineres i .env.example (og .env lokalt).
Pydantic-Settings validerer og giver defaults ved opstart.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # ── App ───────────────────────────────────────────────────────────────────
    ENVIRONMENT: str = "development"          # development | staging | production
    LOG_LEVEL: str = "info"

    # ── Database ──────────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql://bbadmin:password@localhost:5432/brobygger"

    # ── Azure Entra ID ────────────────────────────────────────────────────────
    AZURE_CLIENT_ID: str = "TODO_CLIENT_ID"
    AZURE_TENANT_ID: str = "TODO_TENANT_ID"

    # ── SignalR ───────────────────────────────────────────────────────────────
    SIGNALR_CONNECTION_STRING: str = ""

    # ── Web Push / VAPID ──────────────────────────────────────────────────────
    VAPID_PRIVATE_KEY: str = ""
    VAPID_PUBLIC_KEY: str = ""
    VAPID_SUBJECT: str = "mailto:admin@sosbrobygger.dk"

    # ── CORS ──────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    # ── JWT (kun dev — erstat med Entra ID JWKS i prod) ──────────────────────
    JWT_SECRET: str = "TODO_CHANGE_IN_PROD_min32chars_secret_key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ── Produktions-vagt: fail closed på usikker konfiguration ─────────────────
    # Backend NÆGTER at starte i produktion med dev-secrets/stub-config.
    @model_validator(mode="after")
    def _guard_production_secrets(self):
        if self.ENVIRONMENT == "production":
            problemer = []
            if "TODO" in self.JWT_SECRET or len(self.JWT_SECRET) < 32:
                problemer.append("JWT_SECRET (default/for kort)")
            if self.JWT_ALGORITHM == "HS256":
                problemer.append("JWT_ALGORITHM=HS256 - brug RS256 + Entra ID JWKS i prod")
            if self.AZURE_TENANT_ID.startswith("TODO") or self.AZURE_CLIENT_ID.startswith("TODO"):
                problemer.append("AZURE_TENANT_ID/AZURE_CLIENT_ID (ikke sat)")
            if "password@localhost" in self.DATABASE_URL:
                problemer.append("DATABASE_URL (default dev-vaerdi)")
            if problemer:
                raise ValueError(
                    "Usikker produktions-konfiguration - backend naegter at starte. "
                    "Ret foer deploy: " + "; ".join(problemer)
                )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
