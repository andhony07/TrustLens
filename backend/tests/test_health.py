"""Test health and documentation endpoints."""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_endpoint_success(client):
    """Test 1: Health endpoint returns status ok and metadata."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["application_name"] == "TrustLens AI"
    assert data["analyzer_version"] == "1.0.0"
    assert "timestamp" in data


def test_swagger_documentation_accessible(client):
    """Ensure OpenAPI docs are accessible without auth."""
    response = client.get("/api/docs")
    assert response.status_code == 200
    assert "swagger-ui" in response.text.lower()
