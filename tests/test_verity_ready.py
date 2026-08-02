"""Tests for Verity readiness endpoint."""

import pytest
from fastapi.testclient import TestClient

from src.api.server import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_verity_ready_endpoint(client):
    response = client.get("/api/v1/verity/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "aihawk"
    assert "ready_for_verity" in data
    assert data["checks"]["backend_running"] is True
    assert "resume" in data["suggested_backend_paths"]
