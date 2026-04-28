"""
test_mennesker.py — Tests for /v1/mennesker

FASE 1: Alle endpoints returnerer 503 — vi tester at de svarer korrekt.
FASE 2: Erstat 503-assertions med rigtige data-assertions + DB-fixtures.
"""

import pytest


class TestMenneskerFase1:
    """Verifikation af at FASE 1-stubs svarer med 503."""

    def test_list_returns_503(self, client):
        resp = client.get("/v1/mennesker")
        assert resp.status_code == 503

    def test_get_returns_503(self, client):
        resp = client.get("/v1/mennesker/m-123")
        assert resp.status_code == 503

    def test_create_returns_503(self, client):
        resp = client.post("/v1/mennesker", json={"navn": "Test Person"})
        assert resp.status_code == 503

    def test_update_returns_503(self, client):
        resp = client.patch("/v1/mennesker/m-123", json={"navn": "Nyt Navn"})
        assert resp.status_code == 503

    def test_delete_returns_503(self, client):
        resp = client.delete("/v1/mennesker/m-123")
        assert resp.status_code == 503


# ── FASE 2: Uncomment og udfyld disse tests når backend er aktiv ──────────────

# class TestMenneskerFase2:
#
#     def test_create_og_hent(self, client, auth_headers):
#         # Opret
#         create_resp = client.post("/v1/mennesker",
#             json={"navn": "Ali Hassan", "typer": ["en-til-en"], "sprog": ["arabisk"]},
#             headers=auth_headers,
#         )
#         assert create_resp.status_code == 201
#         m = create_resp.json()
#         assert m["navn"] == "Ali Hassan"
#         assert "id" in m
#
#         # Hent
#         get_resp = client.get(f"/v1/mennesker/{m['id']}", headers=auth_headers)
#         assert get_resp.status_code == 200
#         assert get_resp.json()["navn"] == "Ali Hassan"
#
#     def test_list_filtrering(self, client, auth_headers):
#         resp = client.get("/v1/mennesker?status=ny", headers=auth_headers)
#         assert resp.status_code == 200
#         data = resp.json()
#         assert all(m["status"] == "ny" for m in data)
#
#     def test_soft_delete(self, client, auth_headers, test_menneske):
#         resp = client.delete(f"/v1/mennesker/{test_menneske['id']}", headers=auth_headers)
#         assert resp.status_code == 204
#         # Skal stadig eksistere (soft delete) men ikke dukke op i listen
#         list_resp = client.get("/v1/mennesker", headers=auth_headers)
#         ids = [m["id"] for m in list_resp.json()]
#         assert test_menneske["id"] not in ids
