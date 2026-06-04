"""API integration tests for the AIHawk backend."""

import pytest
from fastapi.testclient import TestClient

from src.api.server import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_root_returns_service_info(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "AIHawk"
    assert "health" in data


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["resume_configured"] is True


def test_status_endpoint_lists_routes(client):
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "resume" in data["endpoints"]


def test_styles_endpoint(client):
    response = client.get("/api/v1/styles")
    assert response.status_code == 200
    assert "styles" in response.json()


def test_resume_verity_probe_empty_payload(client):
    response = client.post(
        "/api/v1/resume",
        json={"style": "", "body": ""},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_tailored_resume_verity_probe_without_job_url(client):
    response = client.post(
        "/api/v1/resume/tailored",
        json={"style": "Modern Blue", "body": {}},
    )
    assert response.status_code == 200
    assert "Verity audit" in response.json()["message"]
