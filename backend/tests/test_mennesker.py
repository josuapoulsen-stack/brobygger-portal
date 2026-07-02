"""
test_mennesker.py — Tests for /v1/mennesker

Endpoints er nu DB-aktive (bruger get_db). En funktionel round-trip kræver derfor
en test-Postgres + get_db-override i conftest. Indtil den er sat op, skippes
DB-afhængige tests. De gamle "503-stub"-tests er fjernet, da de ikke længere gælder.
"""

import pytest

pytestmark = pytest.mark.skip(
    reason="Kræver test-Postgres + get_db-override (FASE 2). "
           "Endpoints er DB-aktive; SQLite duer ikke pga. ARRAY/BYTEA/JSON/UUID-kolonner."
)


class TestMennesker:

    def test_create_og_hent(self, client, auth_headers):
        create_resp = client.post(
            "/v1/mennesker",
            json={"navn": "Ali Hassan", "typer": ["en-til-en"], "sprog": ["arabisk"]},
            headers=auth_headers,
        )
        assert create_resp.status_code == 201
        m = create_resp.json()
        assert m["navn"] == "Ali Hassan"
        assert "id" in m

        get_resp = client.get(f"/v1/mennesker/{m['id']}", headers=auth_headers)
        assert get_resp.status_code == 200
        assert get_resp.json()["navn"] == "Ali Hassan"

    def test_list_filtrering(self, client, auth_headers):
        resp = client.get("/v1/mennesker?status=ny", headers=auth_headers)
        assert resp.status_code == 200
        assert all(m["status"] == "ny" for m in resp.json())

    def test_telefon_norm_afledes(self, client, auth_headers):
        resp = client.post(
            "/v1/mennesker",
            json={"navn": "Test Normalisering", "telefon": "+45 71 20 30 40"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["telefon_norm"] == "71203040"

    def test_soft_delete(self, client, auth_headers):
        created = client.post("/v1/mennesker", json={"navn": "Slettes"}, headers=auth_headers).json()
        resp = client.delete(f"/v1/mennesker/{created['id']}", headers=auth_headers)
        assert resp.status_code == 204
        # Efter soft-delete: 404 på direkte opslag + væk fra listen
        assert client.get(f"/v1/mennesker/{created['id']}", headers=auth_headers).status_code == 404
        ids = [m["id"] for m in client.get("/v1/mennesker", headers=auth_headers).json()]
        assert created["id"] not in ids
