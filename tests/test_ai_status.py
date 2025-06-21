"""
Unit tests for AI service status and admin endpoints.
"""

from unittest.mock import Mock, patch

import pytest


def test_ai_service_status(ai_client, auth_headers):
    """Test getting detailed AI service status."""
    with (
        patch("ai_service.app.api.dependencies.get_session_aware_agent") as mock_agent,
        patch(
            "ai_service.app.api.dependencies.get_vector_store_instance"
        ) as mock_store,
    ):

        mock_agent_instance = Mock()
        mock_agent_instance.llm = Mock()
        mock_agent_instance.tools = []
        mock_agent.return_value = mock_agent_instance

        mock_store.return_value = Mock()

        response = ai_client.get("/api/v1/status", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "pAInt AI Service"
        assert data["status"] == "operational"
        assert "components" in data
        assert "capabilities" in data
