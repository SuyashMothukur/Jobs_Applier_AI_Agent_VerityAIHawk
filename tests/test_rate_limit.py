"""Tests for API rate limiting."""

import config
import pytest
from fastapi.testclient import TestClient

from src.api.server import app


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setattr(config, "RATE_LIMIT_REQUESTS", 2)
    monkeypatch.setattr(config, "RATE_LIMIT_WINDOW_SECONDS", 60)
    with TestClient(app) as test_client:
        yield test_client


def test_health_not_rate_limited(client):
    for _ in range(5):
        response = client.get("/health")
        assert response.status_code == 200


def test_resume_rate_limit_returns_429(client):
    # Audit probes return 200 until the limit is hit.
    first = client.post("/api/v1/resume", json={"style": "", "body": ""})
    second = client.post("/api/v1/resume", json={"style": "", "body": ""})
    third = client.post("/api/v1/resume", json={"style": "", "body": ""})

    assert first.status_code == 200
    assert second.status_code == 200
    assert third.status_code == 429
    assert "Rate limit exceeded" in third.json()["detail"]
    assert "Retry-After" in third.headers


def test_health_includes_rate_limit_config(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["rate_limit"]["requests"] == 2
    assert data["rate_limit"]["window_seconds"] == 60
