import pytest


def test_api_root_endpoint(api_client):
    """Test API root endpoint returns correct information."""
    response = api_client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "pAInt CRUD API"
    assert data["version"] == "1.0.0"
    assert "endpoints" in data
    assert "health" in data["endpoints"]


def test_api_health_endpoint(api_client):
    """Test API health check endpoint."""
    response = api_client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "api_service"
    assert "components" in data
    assert data["components"]["api"] is True
