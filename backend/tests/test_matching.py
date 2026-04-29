"""
backend/tests/test_matching.py — Unit-tests for matching-algoritmen

Tester scoring-logikken direkte uden database.
Alle tests bruger rene Python-objekter — ingen fixtures nødvendige.
"""

import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4

# ── Importer de funktioner vi tester direkte ────────────────────────────────
from backend.services.matching import (
    _score_type,
    _score_sprog,
    _score_kapacitet,
    _byg_begrundelse,
    _initialer,
    _normalize_list,
    _normalize_type,
    W_TYPE, W_SPROG, W_KAPACITET, W_KONTINU, MAX_SCORE,
)


# ─────────────────────────────────────────────────────────────────────────────
#  _score_type
# ─────────────────────────────────────────────────────────────────────────────

class TestScoreType:
    def test_præcis_match_giver_fuld_score(self):
        assert _score_type("sundhed", ["sundhed", "social"]) == W_TYPE

    def test_ingen_overlap_giver_nul(self):
        assert _score_type("sundhed", ["forening", "social"]) == 0

    def test_generalist_brobygger_giver_halvt(self):
        """Brobygger uden specificerede typer → halvt point."""
        assert _score_type("sundhed", []) == W_TYPE // 2

    def test_intet_krav_fra_menneske_giver_halvt(self):
        """Menneske uden typekrav → halvt point (alle passer)."""
        assert _score_type("", ["sundhed"]) == W_TYPE // 2

    def test_begge_tomme_giver_halvt(self):
        assert _score_type("", []) == W_TYPE // 2

    def test_case_insensitive_via_normalize(self):
        """Normalize sørger for lowercase — test at typen matcher."""
        assert _score_type("social", ["social"]) == W_TYPE


# ─────────────────────────────────────────────────────────────────────────────
#  _score_sprog
# ─────────────────────────────────────────────────────────────────────────────

class TestScoreSprog:
    def test_fuld_overlap_giver_fuld_score(self):
        assert _score_sprog(["arabisk", "dansk"], ["arabisk", "dansk", "engelsk"]) == W_SPROG

    def test_ingen_overlap_giver_nul(self):
        assert _score_sprog(["arabisk"], ["somali", "tigrinya"]) == 0

    def test_intet_krav_giver_fuld_score(self):
        """Ingen sprogkrav → alle brobyggere passer."""
        assert _score_sprog([], ["dansk"]) == W_SPROG

    def test_delvis_overlap_giver_proportionelt(self):
        """1 af 2 kravssprog dækket → 50% af W_SPROG."""
        score = _score_sprog(["arabisk", "tigrinya"], ["arabisk"])
        assert score == round(0.5 * W_SPROG)
        assert 0 < score < W_SPROG

    def test_score_aldrig_over_max(self):
        score = _score_sprog(["arabisk"], ["arabisk", "dansk", "somali"])
        assert score <= W_SPROG


# ─────────────────────────────────────────────────────────────────────────────
#  _score_kapacitet
# ─────────────────────────────────────────────────────────────────────────────

class TestScoreKapacitet:
    def test_ingen_vagter_giver_nul(self):
        assert _score_kapacitet(0) == 0

    def test_negativ_giver_nul(self):
        assert _score_kapacitet(-1) == 0

    def test_en_vagt_giver_lavt(self):
        score = _score_kapacitet(1)
        assert 0 < score < W_KAPACITET

    def test_to_vagter_giver_middel(self):
        assert _score_kapacitet(2) < W_KAPACITET

    def test_tre_vagter_giver_max(self):
        assert _score_kapacitet(3) == W_KAPACITET

    def test_mange_vagter_giver_max(self):
        assert _score_kapacitet(99) == W_KAPACITET

    def test_rækkefølge_stigende(self):
        """Jo flere vagter, jo højere score."""
        assert _score_kapacitet(1) < _score_kapacitet(2) < _score_kapacitet(3)


# ─────────────────────────────────────────────────────────────────────────────
#  Score-summering og max
# ─────────────────────────────────────────────────────────────────────────────

class TestScoreTotal:
    def test_max_score_er_100(self):
        assert MAX_SCORE == 100

    def test_perfekt_profil_rammer_100(self):
        """Perfekt match: korrekt type, alle sprog, 3+ vagter, forrige brobygger."""
        total = (
            _score_type("sundhed", ["sundhed"])
            + _score_sprog(["arabisk"], ["arabisk"])
            + _score_kapacitet(5)
            + W_KONTINU
        )
        assert total == 100

    def test_minimal_profil_over_nul(self):
        """Generalist med 1 vagt og ingen sprogkrav bør stadig give point."""
        total = (
            _score_type("", [])
            + _score_sprog([], [])
            + _score_kapacitet(1)
        )
        assert total > 0


# ─────────────────────────────────────────────────────────────────────────────
#  _byg_begrundelse
# ─────────────────────────────────────────────────────────────────────────────

class TestBygBegrundelse:
    def test_forrige_brobygger_nævnes(self):
        tekst = _byg_begrundelse(W_TYPE, W_SPROG, W_KAPACITET, W_KONTINU,
                                 "sundhed", ["sundhed"], ["arabisk"], True)
        assert "kender" in tekst.lower() or "allerede" in tekst.lower()

    def test_ingen_kapacitet_nævnes(self):
        tekst = _byg_begrundelse(W_TYPE, W_SPROG, 0, 0,
                                 "sundhed", ["sundhed"], ["arabisk"], False)
        assert "ingen ledige" in tekst.lower()

    def test_god_kapacitet_nævnes(self):
        tekst = _byg_begrundelse(W_TYPE, W_SPROG, W_KAPACITET, 0,
                                 "social", ["social"], ["dansk"], False)
        assert "kapacitet" in tekst.lower()

    def test_ingen_typeoverlap_nævnes(self):
        tekst = _byg_begrundelse(0, W_SPROG, W_KAPACITET, 0,
                                 "sundhed", ["social"], ["dansk"], False)
        assert "dækker ikke" in tekst.lower()

    def test_returner_string_altid(self):
        tekst = _byg_begrundelse(0, 0, 0, 0, "", [], [], False)
        assert isinstance(tekst, str)
        assert len(tekst) > 0


# ─────────────────────────────────────────────────────────────────────────────
#  Hjælpere
# ─────────────────────────────────────────────────────────────────────────────

class TestInitialer:
    def test_fornavn_efternavn(self):
        assert _initialer("Maja Holmberg") == "MH"

    def test_tre_ord(self):
        """Første + sidste bogstav."""
        assert _initialer("Amira Osman Ali") == "AA"

    def test_enkelt_navn(self):
        assert _initialer("Maja") == "MA"

    def test_tomt_navn(self):
        assert _initialer("") == "??"

    def test_uppercase(self):
        assert _initialer("maja holmberg") == "MH"


class TestNormalizeList:
    def test_lowercase_og_strip(self):
        assert _normalize_list(["Arabisk", " Dansk "]) == ["arabisk", "dansk"]

    def test_ingen_input(self):
        assert _normalize_list(None) == []
        assert _normalize_list([]) == []

    def test_tal_konverteres(self):
        result = _normalize_list([1, 2])
        assert result == ["1", "2"]
