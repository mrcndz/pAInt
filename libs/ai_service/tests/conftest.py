"""
Pytest configuration for AI service unit tests.
"""

import os
import sys
from unittest.mock import Mock, patch

import pytest

# Add the app directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../app"))


@pytest.fixture
def mock_openai_embeddings():
    """Mock OpenAI embeddings."""
    mock = Mock()
    mock.embed_query.return_value = [0.1, 0.2, 0.3, 0.4, 0.5]
    return mock


@pytest.fixture
def mock_openai_chat():
    """Mock OpenAI chat model."""
    mock = Mock()
    mock.invoke.return_value = "Mocked AI response"
    return mock


@pytest.fixture
def mock_database_session():
    """Mock database session."""
    mock = Mock()
    mock.query.return_value.filter.return_value.first.return_value = None
    mock.add.return_value = None
    mock.commit.return_value = None
    mock.rollback.return_value = None
    mock.close.return_value = None
    return mock


@pytest.fixture
def mock_conversation_manager():
    """Mock conversation manager."""
    from langchain.memory import ConversationBufferMemory

    mock = Mock()
    mock.get_memory_for_session.return_value = ConversationBufferMemory(
        memory_key="chat_history", return_messages=True
    )
    mock.save_session_to_database.return_value = True
    mock.create_new_session.return_value = "550e8400-e29b-41d4-a716-446655440000"
    mock.get_cache_size.return_value = 0
    return mock


@pytest.fixture
def mock_vector_store():
    """Mock vector store."""
    mock = Mock()
    mock.search.return_value = [
        {
            "id": "test-paint-1",
            "name": "Test Blue Paint",
            "color": "Blue",
            "product_line": "Premium",
            "environment": "internal",
            "finish_type": "matte",
            "price": 89.90,
            "features": ["lavável", "antimofo"],
            "surface_types": ["parede", "teto"],
            "ai_summary": "Perfect for bedrooms",
            "relevance_score": 0.95,
        }
    ]
    return mock


@pytest.fixture
def sample_chat_session_data():
    """Sample chat session data for testing."""
    return {
        "messages": [
            {
                "type": "human",
                "content": "Preciso de tinta para meu quarto",
                "timestamp": None,
            },
            {
                "type": "ai",
                "content": "Recomendo uma tinta azul tranquila para seu quarto",
                "timestamp": None,
            },
        ],
        "message_count": 2,
    }


@pytest.fixture
def sample_paint_data():
    """Sample paint product data."""
    return {
        "id": "paint-test-1",
        "name": "Azul Tranquilo",
        "color": "Blue",
        "product_line": "Premium",
        "environment": "internal",
        "finish_type": "matte",
        "price": 89.90,
        "features": ["lavável", "antimofo"],
        "surface_types": ["parede", "teto"],
        "ai_summary": "Uma tinta azul suave, perfeita para ambientes que buscam tranquilidade",
        "usage_tags": ["quarto", "relaxante", "interno"],
    }


@pytest.fixture(autouse=True)
def mock_config():
    """Mock configuration for all tests."""
    with patch("libs.ai_service.app.config.config") as mock_config:
        mock_config.OPENAI_API_KEY = "test-api-key"
        mock_config.OPENAI_MODEL = "gpt-3.5-turbo"
        mock_config.JWT_SECRET = "super-secret-jwt-key"
        yield mock_config


@pytest.fixture(autouse=True)
def mock_get_db():
    """Mock database connection for all tests."""
    with patch("shared.database.get_db") as mock:
        mock_session = Mock()
        mock.return_value = iter([mock_session])
        yield mock
