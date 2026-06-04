"""Tests for configuration validation."""

import pytest
from fastapi.testclient import TestClient

from src.api.server import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_config_validate_endpoint(client):
    response = client.get("/api/v1/config/validate")
    assert response.status_code == 200
    data = response.json()
    assert data["checks"]["resume_file_exists"] is True
    assert "resume_file" in data["checks"]
