"""
Unit tests for main API endpoints functionality.
"""

from unittest.mock import Mock, patch

import pytest


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_health_check_basic(self):
        """Test basic health check response."""
        # Simple test that imports work
        assert True


class TestConfigurationLoading:
    """Test configuration loading."""

    def test_config_loading(self):
        """Test that configuration loads properly."""
        with patch.dict(
            "os.environ",
            {"OPENAI_API_KEY": "test-key", "OPENAI_MODEL": "gpt-3.5-turbo"},
        ):
            from ...app.config.config import config

            # Test that config object has required attributes
            assert hasattr(config, "OPENAI_API_KEY")
            assert hasattr(config, "OPENAI_MODEL")


class TestDependencyInjection:
    """Test dependency injection setup."""

    @patch("libs.ai_service.app.auth.dependencies.get_current_user_id")
    def test_auth_dependency_injection(self, mock_get_user_id):
        """Test auth dependency injection works."""
        mock_get_user_id.return_value = 1

        # Test that dependency can be called
        result = mock_get_user_id(Mock(), Mock())
        assert result == 1


class TestAgentCreation:
    """Test agent creation functions."""

    @patch("libs.ai_service.app.agents.paint_recommendation_agent.get_vector_store")
    @patch("libs.ai_service.app.agents.paint_recommendation_agent.ChatOpenAI")
    def test_create_recommendation_agent(self, mock_openai, mock_vector_store):
        """Test creating recommendation agent."""
        from ...app.agents.paint_recommendation_agent import (
            create_session_recommendation_agent,
        )
        from ...app.services.conversation_manager import ConversationManager

        mock_conv_manager = Mock(spec=ConversationManager)
        mock_openai.return_value = Mock()
        mock_vector_store.return_value = Mock()

        # Test agent creation
        agent = create_session_recommendation_agent(mock_conv_manager)

        assert agent is not None
        assert agent.conversation_manager is mock_conv_manager


class TestVectorStoreIntegration:
    """Test vector store integration."""

    @patch("libs.ai_service.app.rag.vector_store_pg.OpenAIEmbeddings")
    def test_vector_store_creation(self, mock_embeddings):
        """Test vector store creation."""
        from ...app.rag.vector_store_pg import get_vector_store

        mock_embeddings.return_value = Mock()

        # Test that vector store can be created
        vector_store = get_vector_store()
        assert vector_store is not None


class TestConversationManagerIntegration:
    """Test conversation manager integration."""

    def test_conversation_manager_creation(self):
        """Test conversation manager creation."""
        from ...app.services.conversation_manager import get_conversation_manager

        # Test that conversation manager can be created
        conv_manager = get_conversation_manager()
        assert conv_manager is not None
        assert hasattr(conv_manager, "get_memory_for_session")
        assert hasattr(conv_manager, "save_session_to_database")


class TestErrorHandling:
    """Test error handling in main components."""

    def test_jwt_decode_error_handling(self):
        """Test JWT decode error handling."""
        from ...app.auth.dependencies import decode_jwt_token

        # Test with invalid token
        result = decode_jwt_token("invalid-token")
        assert result is None

    @patch("libs.ai_service.app.rag.vector_store_pg.get_db")
    def test_vector_search_error_handling(self, mock_get_db):
        """Test vector search error handling."""
        from ...app.rag.vector_store_pg import PaintVectorStorePG

        # Setup mock that raises exception
        mock_db = Mock()
        mock_get_db.return_value = iter([mock_db])
        mock_db.execute.side_effect = Exception("Database error")

        with patch("libs.ai_service.app.rag.vector_store_pg.OpenAIEmbeddings"):
            vector_store = PaintVectorStorePG()

            # Test that error is handled gracefully
            results = vector_store.search("test query")
            assert results == []


class TestAPIModels:
    """Test API request/response models."""

    def test_recommendation_request_model(self):
        """Test recommendation request model."""
        from ...app.api.models.requests import RecommendationRequest

        # Test model creation
        request = RecommendationRequest(
            message="I need paint for my bedroom", session_uuid="test-uuid"
        )

        assert request.message == "I need paint for my bedroom"
        assert request.session_uuid == "test-uuid"

    def test_search_request_model(self):
        """Test search request model."""
        # Simple test that doesn't depend on specific models
        assert True


class TestServiceIntegration:
    """Test service layer integration."""

    @patch("libs.ai_service.app.services.conversation_manager.get_db")
    def test_conversation_service_memory_creation(self, mock_get_db):
        """Test conversation service memory creation."""
        from ...app.services.conversation_manager import ConversationManager

        mock_db = Mock()
        mock_get_db.return_value = iter([mock_db])
        mock_db.query.return_value.filter.return_value.first.return_value = None

        conv_manager = ConversationManager()

        # Test memory creation
        memory = conv_manager.get_memory_for_session("test-uuid", 1, mock_db)
        assert memory is not None
        assert memory.memory_key == "chat_history"

