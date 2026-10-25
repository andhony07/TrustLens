"""Test validation rules, input constraints, and malformed requests."""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_empty_input_rejection(client):
    """Test 2: Empty input string is rejected with 422."""
    response = client.post("/api/analyze", json={"text": "", "input_type": "message"})
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data or "error" in data


def test_whitespace_only_input_rejection(client):
    """Test 3: Whitespace-only input is rejected with 422."""
    response = client.post("/api/analyze", json={"text": "   \n\t   ", "input_type": "job_offer"})
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data or "error" in data


def test_oversized_input_rejection(client):
    """Test 4: Input exceeding 10,000 characters is rejected with 422."""
    oversized_text = "A" * 10001
    response = client.post("/api/analyze", json={"text": oversized_text, "input_type": "message"})
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data or "error" in data


def test_unexpected_input_types_and_malformed_requests(client):
    """Test 15: Invalid input_type enum or malformed JSON payloads are handled."""
    # Invalid enum value
    response = client.post("/api/analyze", json={"text": "Valid message text here", "input_type": "crypto_scam"})
    assert response.status_code == 422

    # Missing required 'text' field
    response_missing = client.post("/api/analyze", json={"input_type": "message"})
    assert response_missing.status_code == 422

    # Malformed non-JSON body
    response_raw = client.post("/api/analyze", content="not json", headers={"Content-Type": "application/json"})
    assert response_raw.status_code == 422
