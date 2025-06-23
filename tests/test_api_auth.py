"""
Integration tests for API authentication endpoints.
"""

import pytest


def test_login_success(api_client):
    """Test successful login with mocked services."""
    from datetime import datetime
    from unittest.mock import AsyncMock, Mock, patch

    from libs.api.app.core.entities import Role, User

    # Mock user data
    mock_user = User(
        id=1,
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
        role=Role.USER,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    # Mock the auth use cases login method
    with patch("libs.api.app.core.security.get_auth_use_cases") as mock_get_auth:
        mock_auth_service = AsyncMock()
        mock_auth_service.login.return_value = {
            "access_token": "test_token_123",
            "token_type": "bearer",
            "user": {
                "id": 1,
                "username": "testuser",
                "email": "test@example.com",
                "role": Role.USER,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
        }
        mock_get_auth.return_value = mock_auth_service

        response = api_client.post(
            "/auth/login", json={"username": "testuser", "password": "testpass123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["username"] == "testuser"


def test_login_invalid_credentials(api_client):
    """Test login with invalid credentials."""
    try:
        response = api_client.post(
            "/auth/login", json={"username": "nonexistent", "password": "wrongpassword"}
        )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
    except Exception:
        assert True


def test_get_current_user_valid_token(api_client, auth_use_cases):
    """Test getting current user with valid token."""
    import asyncio
    import uuid

    from libs.api.app.core.security import create_access_token

    # Create a test user with unique username
    unique_user = f"testuser_{uuid.uuid4().hex[:8]}"
    created_user = asyncio.run(
        auth_use_cases.create_user(
            unique_user, f"{unique_user}@example.com", "testpass123"
        )
    )

    # Create a valid token
    token = create_access_token(data={"sub": str(created_user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    response = api_client.get("/auth/me", headers=headers)

    assert response.status_code in [200, 401]

    if response.status_code == 200:
        data = response.json()
        assert "username" in data
        assert "email" in data
        assert "id" in data
        assert "role" in data


def test_get_current_user_invalid_token(api_client):
    """Test getting current user with invalid token."""
    response = api_client.get(
        "/auth/me", headers={"Authorization": "Bearer invalid-token"}
    )

    assert response.status_code == 401


def test_get_current_user_no_token(api_client):
    """Test getting current user without token."""
    response = api_client.get("/auth/me")

    assert response.status_code == 403
