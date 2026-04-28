"""
backend/database.py — PostgreSQL-forbindelse via SQLAlchemy

FASE 1 (prototype): Ikke i brug — app læser fra localStorage/globals.
FASE 2 (backend):   Importér `get_db` som FastAPI-dependency i routerne.

Forbindelsesstreng sættes via DATABASE_URL i .env:
  postgresql://bbadmin:password@brobygger-dev-db.postgres.database.azure.com/brobygger?sslmode=require
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import settings

# ── Engine ────────────────────────────────────────────────────────────────────
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,          # genopbyg forbindelser ved timeout
    pool_size=5,
    max_overflow=10,
    connect_args={"sslmode": "require"} if "azure" in settings.DATABASE_URL else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ── Base-klasse til ORM-modeller (bruges ikke i FASE 1) ───────────────────────
class Base(DeclarativeBase):
    pass


# ── FastAPI dependency ────────────────────────────────────────────────────────
def get_db():
    """
    Yield en database-session og luk den bagefter.

    Brug som:
        @router.get("/ting")
        def get_ting(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
