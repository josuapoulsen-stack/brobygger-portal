"""
test_aftaler.py — Tests for /v1/aftaler
"""


class TestAftaler:

    def test_list_returns_503(self, client):
        resp = client.get("/v1/aftaler")
        assert resp.status_code == 503

    def test_list_med_filter(self, client):
        resp = client.get("/v1/aftaler?brobygger_id=b-123&status=planlagt")
        assert resp.status_code == 503

    def test_create_returns_503(self, client):
        resp = client.post("/v1/aftaler", json={
            "brobyggerId": "b-123",
            "menneskeId":  "m-456",
            "dato":        "2025-06-15T10:00:00Z",
        })
        assert resp.status_code == 503

    def test_update_status_returns_503(self, client):
        resp = client.patch("/v1/aftaler/a-123/status", json={"status": "gennemfoert"})
        assert resp.status_code == 503
