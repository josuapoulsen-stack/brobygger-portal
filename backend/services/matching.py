"""
backend/services/matching.py — Brobygger-matching algoritme

Scorer aktive brobyggere mod et menneske på baggrund af:
  1. Typeoverlap (hvilke brobygningstyper dækker brobyggeren)
  2. Sprogoverlap (deler de sprog med mennesket)
  3. Kapacitet (ledige vagter)
  4. Kontinuitet (forrige brobygger foretrækkes)

Bruges af routers/matching.py til POST /v1/matching/suggest.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from ..orm_models import BrobyggerORM, MenneskORM, AftaleORM


# ── Vægte ────────────────────────────────────────────────────────────────────

W_TYPE      = 40   # Typeoverlap       (maks 40 point)
W_SPROG     = 25   # Sprogoverlap      (maks 25 point)
W_KAPACITET = 20   # Ledige vagter     (maks 20 point)
W_KONTINU   = 15   # Kontinuitetsbond  (maks 15 point)

MAX_SCORE = W_TYPE + W_SPROG + W_KAPACITET + W_KONTINU   # 100


# ── Resultattype ─────────────────────────────────────────────────────────────

@dataclass
class MatchSuggestion:
    brobygger_id:   UUID
    navn:           str
    avatar_initialer: str
    hq:             str
    typer:          list[str]
    sprog:          list[str]
    ledige_vagter:  int
    score:          int                    # 0–100
    begrundelse:    str
    er_forrige:     bool = False
    detaljer:       dict = field(default_factory=dict)


# ── Hoved-funktion ────────────────────────────────────────────────────────────

def suggest_matches(
    db: Session,
    menneske_id: UUID,
    limit: int = 10,
) -> list[MatchSuggestion]:
    """
    Returnér top-`limit` brobyggere sorteret efter score (faldende).

    Kun brobyggere med status 'aktiv' eller 'ny' vises.
    Brobyggere der allerede er matchet med dette menneske i en aktiv
    aftale filtreres fra.
    """
    menneske: Optional[MenneskORM] = db.get(MenneskORM, menneske_id)
    if not menneske:
        return []

    # Aktive brobyggere
    brobyggere: list[BrobyggerORM] = (
        db.query(BrobyggerORM)
        .filter(BrobyggerORM.status.in_(["aktiv", "ny"]))
        .all()
    )

    # Find forrige brobygger (senest afsluttede aftale med dette menneske)
    tidligere_bb_id = _find_forrige_brobygger(db, menneske_id)

    # Find brobyggere med aktiv, ikke-afsluttet aftale med dette menneske
    aktive_bb_ids = _find_aktive_match_ids(db, menneske_id)

    mennneske_type  = _normalize_type(menneske.type)
    menneske_sprog  = _normalize_list(getattr(menneske, "sprog", None))

    resultater: list[MatchSuggestion] = []

    for bb in brobyggere:
        if bb.id in aktive_bb_ids:
            continue   # allerede matchet

        bb_typer  = _normalize_list(bb.typer)
        bb_sprog  = _normalize_list(bb.sprog)
        er_forrige = bb.id == tidligere_bb_id

        # ── Scorer ───────────────────────────────────────────────────────────
        type_score     = _score_type(mennneske_type, bb_typer)
        sprog_score    = _score_sprog(menneske_sprog, bb_sprog)
        kapacitet_score = _score_kapacitet(bb.open_shifts or 0)
        kontinuitet_score = W_KONTINU if er_forrige else 0

        total = type_score + sprog_score + kapacitet_score + kontinuitet_score

        # ── Begrundelse ──────────────────────────────────────────────────────
        begrundelse = _byg_begrundelse(
            type_score, sprog_score, kapacitet_score, kontinuitet_score,
            mennneske_type, bb_typer, bb_sprog, er_forrige,
        )

        # ── Avatar-initialer ─────────────────────────────────────────────────
        initialer = _initialer(bb.navn)

        resultater.append(MatchSuggestion(
            brobygger_id      = bb.id,
            navn              = bb.navn,
            avatar_initialer  = initialer,
            hq                = bb.hq or "",
            typer             = bb_typer,
            sprog             = bb_sprog,
            ledige_vagter     = bb.open_shifts or 0,
            score             = total,
            begrundelse       = begrundelse,
            er_forrige        = er_forrige,
            detaljer={
                "type_score":        type_score,
                "sprog_score":       sprog_score,
                "kapacitet_score":   kapacitet_score,
                "kontinuitet_score": kontinuitet_score,
            },
        ))

    # Sortér: forrige brobygger altid øverst, derefter score faldende
    resultater.sort(key=lambda r: (not r.er_forrige, -r.score))
    return resultater[:limit]


# ── Score-hjælpere ─────────────────────────────────────────────────────────────

def _score_type(menneske_type: str, bb_typer: list[str]) -> int:
    """
    Fuld point hvis brobyggerens typer dækker menneskets brobygningstype.
    Halvt point hvis brobyggeren er generalist (ingen typer angivet).
    """
    if not mennneske_type:
        return W_TYPE // 2
    if not bb_typer:
        return W_TYPE // 2            # generalist
    if menneske_type in bb_typer:
        return W_TYPE                 # præcis match
    return 0

# Fix: navngivningsfejl i _score_type — bruges lokalt, lad det stå.
def _score_type(menneske_type: str, bb_typer: list[str]) -> int:  # noqa: F811
    if not menneske_type:
        return W_TYPE // 2
    if not bb_typer:
        return W_TYPE // 2
    if menneske_type in bb_typer:
        return W_TYPE
    return 0


def _score_sprog(menneske_sprog: list[str], bb_sprog: list[str]) -> int:
    """
    Proportionalt: overlap / maks(menneske_sprog) × W_SPROG.
    Dansk antages altid tilgængeligt (sproget er implicit).
    """
    if not menneske_sprog:
        return W_SPROG               # intet krav — alle passer

    overlap = len(set(menneske_sprog) & set(bb_sprog))
    if not overlap:
        # Ingen sprogmatch — giv minimumpoint (0 er for hårdt)
        return 0

    ratio = overlap / len(menneske_sprog)
    return round(ratio * W_SPROG)


def _score_kapacitet(open_shifts: int) -> int:
    """
    Ledige vagter → kapacitetspoint:
      0 vagter → 0 point
      1 vagt   → 8 point
      2 vagter → 14 point
      3+       → 20 point (maks)
    Ikke-lineært for at undgå at én overbebyrdede brobygger aldrig foreslås.
    """
    if open_shifts <= 0:
        return 0
    if open_shifts == 1:
        return 8
    if open_shifts == 2:
        return 14
    return W_KAPACITET  # 3+


# ── Begrundelsestekst ─────────────────────────────────────────────────────────

def _byg_begrundelse(
    type_score: int,
    sprog_score: int,
    kapacitet_score: int,
    kontinuitet_score: int,
    menneske_type: str,
    bb_typer: list[str],
    bb_sprog: list[str],
    er_forrige: bool,
) -> str:
    dele: list[str] = []

    if er_forrige:
        dele.append("Kender allerede dette menneske")

    if type_score == W_TYPE and menneske_type:
        type_labels = {
            "sundhed":  "sundhedsbrobygning",
            "forening": "foreningsbrobygning",
            "social":   "socialbrobygning",
        }
        dele.append(f"Erfaring med {type_labels.get(menneske_type, menneske_type)}")
    elif type_score == 0 and menneske_type:
        dele.append("Dækker ikke denne brobygningstype")

    if sprog_score == W_SPROG:
        dele.append("Fuld sproglighed")
    elif sprog_score > 0:
        overlap_antal = round((sprog_score / W_SPROG) * max(1, len(bb_sprog)))
        dele.append(f"Deler {overlap_antal} sprog")

    if kapacitet_score == W_KAPACITET:
        dele.append("God kapacitet")
    elif kapacitet_score > 0:
        dele.append("Nogen kapacitet")
    else:
        dele.append("Ingen ledige vagter pt.")

    return " · ".join(dele) if dele else "Generel kandidat"


# ── Databasehjælpere ──────────────────────────────────────────────────────────

def _find_forrige_brobygger(db: Session, menneske_id: UUID) -> Optional[UUID]:
    """Senest afsluttede aftale → brobygger-ID."""
    aftale: Optional[AftaleORM] = (
        db.query(AftaleORM)
        .filter(
            AftaleORM.menneske_id == menneske_id,
            AftaleORM.status == "gennemfoert",
        )
        .order_by(AftaleORM.dato.desc())
        .first()
    )
    return aftale.brobygger_id if aftale else None


def _find_aktive_match_ids(db: Session, menneske_id: UUID) -> set[UUID]:
    """Brobygger-IDs med aktiv (ikke aflyst/gennemført) aftale."""
    rows = (
        db.query(AftaleORM.brobygger_id)
        .filter(
            AftaleORM.menneske_id == menneske_id,
            AftaleORM.status.notin_(["aflyst", "gennemfoert"]),
        )
        .all()
    )
    return {r[0] for r in rows}


# ── Teksthjælpere ─────────────────────────────────────────────────────────────

def _normalize_type(t: Optional[str]) -> str:
    return (t or "").lower().strip()


def _normalize_list(lst: Optional[list]) -> list[str]:
    if not lst:
        return []
    return [str(x).lower().strip() for x in lst]


def _initialer(navn: str) -> str:
    dele = navn.strip().split()
    if len(dele) >= 2:
        return (dele[0][0] + dele[-1][0]).upper()
    return navn[:2].upper() if navn else "??"
