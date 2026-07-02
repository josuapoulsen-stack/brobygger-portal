"""
test_aftaler.py — Tests for /v1/aftaler

Endpoints er nu DB-aktive (bruger get_db). Skippes indtil test-Postgres + get_db-override
er sat op (FASE 2). Bemærk: request-felter er snake_case (brobygger_id/menneske_id).
"""

import pytest

pytestmark = pytest.mark.skip(
    reason="Kræver test-Postgres + get_db-override (FASE 2)."
)


class TestAftaler:

    def test_list_med_filter(self, client, auth_headers):
        resp = client.get("/v1/aftaler?status=planlagt", headers=auth_headers)
        assert resp.status_code == 200

    def test_create_og_statusskift(self, client, auth_headers, seed_ids):
        create = client.post(
            "/v1/aftaler",
            json={
                "brobygger_id": seed_ids["brobygger"],
                "menneske_id": seed_ids["menneske"],
                "dato": "2026-08-15T10:00:00Z",
                "type": "moede",
            },
            headers=auth_headers,
        )
        assert create.status_code == 201
        aftale_id = create.json()["id"]

        patch = client.patch(
            f"/v1/aftaler/{aftale_id}/status",
            json={"status": "gennemfoert", "notes": "Gik fint"},
            headers=auth_headers,
        )
        assert patch.status_code == 200
        assert patch.json()["status"] == "gennemfoert"
