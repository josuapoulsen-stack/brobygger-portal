"""
test_beskeder.py — Tests for /v1/beskeder
"""


class TestBeskeder:

    def test_threads_returns_503(self, client):
        resp = client.get("/v1/beskeder/threads?role=brobygger")
        assert resp.status_code == 503

    def test_threads_kræver_rolle(self, client):
        resp = client.get("/v1/beskeder/threads")
        # role er required query param — FastAPI returnerer 422
        assert resp.status_code == 422

    def test_messages_returns_503(self, client):
        resp = client.get("/v1/beskeder/threads/t-123/messages")
        assert resp.status_code == 503

    def test_send_message_returns_503(self, client):
        resp = client.post("/v1/beskeder/threads/t-123/messages", json={
            "text": "Hej",
            "from_role": "brobygger",
        })
        assert resp.status_code == 503

    def test_mark_read_returns_503(self, client):
        resp = client.post("/v1/beskeder/threads/t-123/read")
        assert resp.status_code == 503
