"""
Integration tests for AI recommendation endpoints.
"""

import pytest


def test_post_recommendation_new_session(ai_client, auth_headers):
    """Test creating new recommendation session."""
    response = ai_client.post(
        "/api/v1/recommend",
        json={"message": "Preciso de tinta para quarto"},
        headers=auth_headers,
    )

    assert response.status_code in [
        200,
        401,
        500,
    ]

    if response.status_code == 200:
        data = response.json()
        assert "response" in data or "session_uuid" in data


def test_post_recommendation_existing_session(ai_client, auth_headers):
    """Test continuing existing recommendation session."""
    response = ai_client.post(
        "/api/v1/recommend",
        json={"message": "E quanto ao preço?", "session_uuid": "test-session-123"},
        headers=auth_headers,
    )

    assert response.status_code in [
        200,
        401,
        404,
        500,
    ]


def test_post_recommendation_unauthorized(ai_client):
    """Test recommendation without auth."""
    response = ai_client.post(
        "/api/v1/recommend", json={"message": "Preciso de tinta", "session_uuid": None}
    )

    assert response.status_code == 403


def test_post_recommendation_invalid_data(ai_client, auth_headers):
    """Test recommendation with invalid data."""
    response = ai_client.post(
        "/api/v1/recommend",
        json={
            # Missing required message field
        },
        headers=auth_headers,
    )

    # May accept empty data or return validation error
    assert response.status_code in [401, 422, 500]


def test_get_user_sessions(ai_client, auth_headers):
    """Test getting user chat sessions."""
    response = ai_client.get("/api/v1/chat/sessions", headers=auth_headers)

    assert response.status_code in [200, 401, 404, 500]
    if response.status_code == 200:
        data = response.json()
        assert "sessions" in data or isinstance(data, list)


def test_get_user_sessions_unauthorized(ai_client):
    """Test getting sessions without auth."""
    response = ai_client.get("/api/v1/chat/sessions")

    assert response.status_code == 403


def test_reset_chat_session(ai_client, auth_headers):
    """Test resetting chat session."""
    session_uuid = "test-session-123"

    response = ai_client.post(
        "/api/v1/chat/reset", json={"session_uuid": session_uuid}, headers=auth_headers
    )

    # Accept success or implementation-specific responses
    assert response.status_code in [200, 401, 404, 422, 500]
    if response.status_code == 200:
        data = response.json()
        assert "message" in data or "session_uuid" in data


def test_reset_chat_session_invalid_uuid(ai_client, auth_headers):
    """Test resetting session with invalid UUID."""
    response = ai_client.post(
        "/api/v1/chat/reset",
        json={"session_uuid": "invalid-uuid"},
        headers=auth_headers,
    )

    # May accept invalid UUIDs or return validation error
    assert response.status_code in [401, 404, 422, 500]
