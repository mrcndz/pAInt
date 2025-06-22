"""
Tests the agent business logic in isolation.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from langchain.memory import ConversationBufferMemory

from ...app.agents.paint_recommendation_agent import PaintRecommendationAgent


class TestPaintRecommendationAgent:
    """Unit tests for PaintRecommendationAgent class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_conversation_manager = Mock()
        self.mock_vector_store = Mock()

        # Create agent with mocked dependencies
        with (
            patch(
                "libs.ai_service.app.agents.paint_recommendation_agent.get_vector_store"
            ) as mock_get_vs,
            patch(
                "libs.ai_service.app.agents.paint_recommendation_agent.ChatOpenAI"
            ) as mock_openai,
        ):

            mock_get_vs.return_value = self.mock_vector_store
            mock_openai.return_value = Mock()

            self.agent = PaintRecommendationAgent(self.mock_conversation_manager)

    def test_setup_tools_creates_correct_tools(self):
        """Test that tools are set up correctly."""
        tools = self.agent.tools
        tool_names = [tool.name for tool in tools]

        assert "search_paints" in tool_names
        assert "filter_paints" in tool_names
        assert "get_paint_details" in tool_names

    def test_get_paint_details_tool(self):
        """Test get paint details tool (placeholder implementation)."""
        # Test
        result = self.agent._get_paint_details_tool("paint-123")

        # Assert
        assert "paint-123" in result
        assert "serão implementados em breve" in result

    def test_create_session_recommendation_agent_factory(self):
        """Test factory function creates agent correctly."""
        from ...app.agents.paint_recommendation_agent import (
            create_session_recommendation_agent,
        )

        mock_conv_manager = Mock()

        with (
            patch(
                "libs.ai_service.app.agents.paint_recommendation_agent.get_vector_store"
            ),
            patch("libs.ai_service.app.agents.paint_recommendation_agent.ChatOpenAI"),
        ):

            agent = create_session_recommendation_agent(mock_conv_manager)

            assert agent is not None
            assert agent.conversation_manager is mock_conv_manager

    def test_agent_has_required_attributes(self):
        """Test that agent has all required attributes."""
        assert hasattr(self.agent, "conversation_manager")
        assert hasattr(self.agent, "vector_store")
        assert hasattr(self.agent, "llm")
        assert hasattr(self.agent, "tools")
        assert hasattr(self.agent, "prompt_template")

    def test_agent_tools_configuration(self):
        """Test that agent tools are properly configured."""
        assert len(self.agent.tools) == 4
        for tool in self.agent.tools:
            assert hasattr(tool, "name")
            assert hasattr(tool, "description")

    def test_conversation_manager_integration(self):
        """Test that conversation manager is properly integrated."""
        assert self.agent.conversation_manager is self.mock_conversation_manager

    def test_vector_store_integration(self):
        """Test that vector store is properly integrated."""
        assert self.agent.vector_store is self.mock_vector_store
