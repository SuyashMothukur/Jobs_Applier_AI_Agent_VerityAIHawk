"""Tests for service info endpoints."""

import pytest
from fastapi.testclient import TestClient

from src.api.server import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_service_info(client):
    response = client.get("/api/v1/info")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "aihawk"
    assert data["llm_model"]
    assert "/health" in data["endpoints"].values()


def test_health_typed_response(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
