import pytest


def test_ai_root_endpoint(ai_client):
    """Test AI service root endpoint."""
    response = ai_client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "pAInt AI Service"
    assert data["version"] == "2.0.0"
    assert "description" in data


def test_ai_health_endpoint(ai_client):
    """Test AI service health check."""
    response = ai_client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ai_service"
