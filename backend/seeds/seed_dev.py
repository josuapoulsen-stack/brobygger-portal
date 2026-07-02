"""
backend/seeds/seed_dev.py — fiktivt udviklings-/test-seed via ORM.

Bruger ORM'en direkte, så data GARANTERET matcher skemaet (gyldige UUID'er,
korrekte enum-værdier, ARRAY/JSON-kolonner). Foretrækkes frem for demo_data.sql,
hvis IDs er hårdkodede og ikke er gyldige UUID'er.

GYLDEN REGEL: KUN opdigtet data her — aldrig rigtige borgere. Seedet er til at
verificere at API'et kan læse/skrive mod databasen i et testmiljø.

Kør EFTER migrations:
    alembic -c backend/alembic.ini upgrade head
    python -m backend.seeds.seed_dev            # tilføjer
    python -m backend.seeds.seed_dev --reset    # rydder kerne-tabeller først
"""

import sys
from datetime import datetime, date, timezone, timedelta

from ..database import SessionLocal
from ..orm_models import BrobyggerORM, MenneskORM, AftaleORM
from ..routers.mennesker import normaliser_telefon


def _norm(obj):
    """Sæt telefon_norm hvis feltet findes."""
    if getattr(obj, "telefon", None):
        obj.telefon_norm = normaliser_telefon(obj.telefon)
    return obj


def seed(reset: bool = False) -> None:
    db = SessionLocal()
    try:
        if reset:
            db.query(AftaleORM).delete()
            db.query(MenneskORM).delete()
            db.query(BrobyggerORM).delete()
            db.commit()

        # ── Brobyggere (frivillige) ──────────────────────────────────────────
        brobyggere = [
            _norm(BrobyggerORM(
                navn="Maja Lindberg", email="maja@example.com", telefon="+45 28 11 22 33",
                typer=["en-til-en", "cafe-gruppe"], sprog=["dansk", "engelsk"],
                hq="København N", status="aktiv", active=1, max_active=3,
                startdato=date(2023, 9, 1), naeste_tid="Tirsdag kl. 14-16",
            )),
            _norm(BrobyggerORM(
                navn="Thomas Eriksen", email="thomas@example.com", telefon="+45 40 55 66 77",
                typer=["en-til-en"], sprog=["dansk"],
                hq="Aarhus C", status="aktiv", active=0, max_active=2,
                startdato=date(2022, 6, 15), naeste_tid="Torsdag kl. 09-11",
            )),
            _norm(BrobyggerORM(
                navn="Amira Osman", email="amira@example.com", telefon="+45 51 88 99 00",
                typer=["en-til-en", "netvaerk"], sprog=["dansk", "arabisk", "engelsk"],
                hq="København S", status="aktiv", active=2, max_active=3,
                startdato=date(2023, 1, 20), naeste_tid="Mandag kl. 10-12",
            )),
        ]
        db.add_all(brobyggere)
        db.flush()  # tildel UUID'er så vi kan referere dem i aftaler

        # ── Mennesker (borgere) — anonymiserede demo-profiler ────────────────
        mennesker = [
            _norm(MenneskORM(
                navn="Ahmad Karimi", alder=34, kon="mand", telefon="+45 71 20 30 40",
                typer=["en-til-en"], sprog=["dansk", "arabisk"],
                status="matched", matched_with=brobyggere[2].id,
                hq="København S", kilde="Egen henvendelse",
            )),
            _norm(MenneskORM(
                navn="Bente Sørensen", alder=68, kon="kvinde", telefon="+45 22 44 66 88",
                typer=["cafe-gruppe"], sprog=["dansk"],
                status="aktiv", matched_with=brobyggere[0].id,
                hq="København N", kilde="Kommune",
            )),
            _norm(MenneskORM(
                navn="Clara Nielsen", alder=29, kon="kvinde", telefon="+45 30 50 70 90",
                typer=["en-til-en", "netvaerk"], sprog=["dansk", "engelsk"],
                status="ny", hq="Aarhus C", kilde="Læge", ucla_fravalgt=True,
            )),
        ]
        db.add_all(mennesker)
        db.flush()

        # ── Aftaler ──────────────────────────────────────────────────────────
        naa = datetime.now(timezone.utc)
        aftaler = [
            AftaleORM(
                brobygger_id=brobyggere[2].id, menneske_id=mennesker[0].id,
                dato=naa + timedelta(days=2), varighed=60, type="moede",
                sted="Café Nord, Nørrebro", status="planlagt",
                brobygningstype="Social", brobygger_note="Første møde — mød op 10 min før.",
            ),
            AftaleORM(
                brobygger_id=brobyggere[0].id, menneske_id=mennesker[1].id,
                dato=naa - timedelta(days=5), varighed=90, type="aktivitet",
                sted="Medborgerhuset", status="gennemfoert",
                brobygningstype="Forening", udfald="gennemfoert", varighed_min=85,
            ),
        ]
        db.add_all(aftaler)
        db.commit()

        print(f"Seed OK: {len(brobyggere)} brobyggere, {len(mennesker)} mennesker, {len(aftaler)} aftaler.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed(reset="--reset" in sys.argv)
