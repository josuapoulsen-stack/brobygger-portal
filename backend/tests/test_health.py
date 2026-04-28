"""
test_health.py — Health-check og basis-endpoints

Disse tests kræver ingen database og skal altid bestå.
"""


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "environment" in data


def test_root(client):
    resp = client.get("/")
    assert resp.status_code == 200


def test_openapi_schema(client):
    """OpenAPI-skemaet kan genereres uden fejl."""
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    schema = resp.json()
    assert schema["info"]["title"] == "SoS Brobygger Portal API"
