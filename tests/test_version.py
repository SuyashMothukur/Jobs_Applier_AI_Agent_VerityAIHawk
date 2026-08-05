"""Tests for API version endpoint and response headers."""

import pytest
from fastapi.testclient import TestClient

from src.api.server import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_version_endpoint(client):
    response = client.get("/api/v1/version")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["api_version"]
    assert data["llm_provider"]


def test_version_headers_on_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers.get("x-aihawk-service") == "aihawk"
    assert response.headers.get("x-aihawk-version")
