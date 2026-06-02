"""
backend/main.py — SoS Brobygger Portal — FastAPI-applikation

Start lokalt:
    cd brobygger-portal
    pip install -r backend/requirements.txt
    uvicorn backend.main:app --reload --port 8000

Miljøvariable læses fra .env (se .env.example).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from .config import settings
from .routers import (
    mennesker,
    brobyggere,
    aftaler,
    beskeder,
    profil,
    matching,
    statistik,
    notifikationer,
    auth,
)


# ── Lifespan (startup / shutdown) ────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # FASE 2: Initialiser DB-forbindelser, SignalR-hub, VAPID-nøgler
    # from .database import engine
    # from .models_orm import Base
    # Base.metadata.create_all(bind=engine)  # kun dev — brug Alembic i prod
    print(f"🟢 SoS Brobygger Portal API starter [{settings.ENVIRONMENT}]")
    yield
    print("🔴 API lukker ned")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="SoS Brobygger Portal API",
    description=(
        "REST API til Brobygger-portalen.\n\n"
        "**FASE 1:** Alle endpoints returnerer 503 — brug `USE_BACKEND=false` i `src/api/index.js`.\n"
        "**FASE 2:** Sæt `USE_BACKEND=true` + deploy backend til Azure App Service."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(mennesker.router)
app.include_router(brobyggere.router)
app.include_router(aftaler.router)
app.include_router(beskeder.router)
app.include_router(profil.router)
app.include_router(matching.router)
app.include_router(statistik.router)
app.include_router(notifikationer.router)


# ── Health-check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Meta"])
def health_check():
    """
    Returnér API-status og DB-forbindelsestjek.

    - `status: "ok"` → alt kører
    - `status: "degraded"` → API kører, DB er utilgængelig
    """
    db_ok = False
    db_error: str | None = None
    db_version: str | None = None

    try:
        from .database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            row = conn.execute(text("SELECT version()")).fetchone()
            db_version = str(row[0]).split(" ")[0] + " " + str(row[0]).split(" ")[1] if row else None
            db_ok = True
    except Exception as exc:
        db_error = str(exc)

    return {
        "status":      "ok" if db_ok else "degraded",
        "environment": settings.ENVIRONMENT,
        "version":     app.version,
        "timestamp":   datetime.now(timezone.utc).isoformat(),
        "database": {
            "connected": db_ok,
            "version":   db_version,
            "error":     db_error,
        },
        "backend_mode": "FASE 2 (live DB)" if db_ok else "FASE 1 (prototype — ingen DB)",
    }


@app.get("/v1/status", tags=["Meta"])
def api_status():
    """
    Returnér en quick oversigt af datamængder (kun når DB er tilgængelig).
    Bruges af frontenden til at vise 'backend er aktiv'-banner.
    """
    try:
        from .database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            counts = {}
            for tbl in ("mennesker", "brobyggere", "aftaler", "brugere"):
                try:
                    row = conn.execute(text(f"SELECT COUNT(*) FROM {tbl}")).fetchone()
                    counts[tbl] = row[0] if row else 0
                except Exception:
                    counts[tbl] = None
        return {"live": True, "counts": counts}
    except Exception:
        # Ingen DB → returnér prototype-tilstand
        return {"live": False, "counts": {}, "note": "Kør backend med PostgreSQL for live data"}


@app.get("/", tags=["Meta"])
def root():
    return {
        "api": "SoS Brobygger Portal",
        "docs": "/docs",
        "status": "USE_BACKEND=false — prototype mode aktiv",
    }
