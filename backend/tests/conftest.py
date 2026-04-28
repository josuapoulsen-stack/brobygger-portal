"""
backend/tests/conftest.py — Delte fixtures til alle tests

Brug:
    pytest backend/tests/ -v

Kræver ingen database i FASE 1 — TestClient rammer 503-stubs.
I FASE 2: tilsæt en test-database og override get_db-dependency.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture(scope="session")
def client():
    """FastAPI TestClient — deles på tværs af alle tests i sessionen."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_headers():
    """
    Dummy auth-header til beskyttede endpoints.
    FASE 2: Generer et rigtigt test-JWT her.
    """
    return {"Authorization": "Bearer test-token-placeholder"}
