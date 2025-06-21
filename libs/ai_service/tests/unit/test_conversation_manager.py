"""
Tests the business logic in isolation without external dependencies.
"""

import uuid
from unittest.mock import MagicMock, Mock, patch

import pytest
from langchain.memory import ConversationBufferMemory
from langchain.schema import AIMessage, HumanMessage

from ...app.services.conversation_manager import ConversationManager


class TestConversationManager:
    """Unit tests for ConversationManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.conversation_manager = ConversationManager()
        self.test_session_uuid = "550e8400-e29b-41d4-a716-446655440000"
        self.test_user_id = 1

    def test_init(self):
        """Test ConversationManager initialization."""
        cm = ConversationManager()
        assert cm._session_cache == {}
        assert isinstance(cm._session_cache, dict)

    def test_get_memory_for_session_cache_hit(self):
        """Test getting memory when session exists in cache."""
        # Setup: Put memory in cache
        memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )
        cache_key = (self.test_session_uuid, self.test_user_id)
        self.conversation_manager._session_cache[cache_key] = memory

        # Test
        result = self.conversation_manager.get_memory_for_session(
            self.test_session_uuid, self.test_user_id
        )

        # Assert
        assert result is memory

    @patch("libs.ai_service.app.services.conversation_manager.get_db")
    def test_get_memory_for_session_cache_miss_no_db_record(self, mock_get_db):
        """Test getting memory when not in cache and no DB record."""
        # Setup mock database session
        mock_db_session = Mock()
        mock_get_db.return_value = iter([mock_db_session])
        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        # Test
        result = self.conversation_manager.get_memory_for_session(
            self.test_session_uuid, self.test_user_id
        )

        # Assert
        assert isinstance(result, ConversationBufferMemory)
        assert result.memory_key == "chat_history"
        assert result.return_messages is True

        # Check it was cached
        cache_key = (self.test_session_uuid, self.test_user_id)
        assert cache_key in self.conversation_manager._session_cache

    @patch("libs.ai_service.app.services.conversation_manager.get_db")
    def test_get_memory_for_session_loads_from_database(self, mock_get_db):
        """Test loading conversation history from database."""
        # Setup mock database session
        mock_db_session = Mock()
        mock_get_db.return_value = iter([mock_db_session])

        # Mock chat session with conversation data
        mock_chat_session = Mock()
        mock_chat_session.session_data = {
            "messages": [
                {"type": "human", "content": "Hello"},
                {"type": "ai", "content": "Hi there!"},
            ]
        }
        mock_db_session.query.return_value.filter.return_value.first.return_value = (
            mock_chat_session
        )

        # Test
        result = self.conversation_manager.get_memory_for_session(
            self.test_session_uuid, self.test_user_id
        )

        # Assert
        assert isinstance(result, ConversationBufferMemory)
        assert len(result.chat_memory.messages) == 2
        assert isinstance(result.chat_memory.messages[0], HumanMessage)
        assert isinstance(result.chat_memory.messages[1], AIMessage)
        assert result.chat_memory.messages[0].content == "Hello"
        assert result.chat_memory.messages[1].content == "Hi there!"

    @patch("libs.ai_service.app.services.conversation_manager.get_db")
    def test_save_session_to_database_new_session(self, mock_get_db):
        """Test saving a new session to database."""
        # Setup
        mock_db_session = Mock()
        mock_get_db.return_value = iter([mock_db_session])
        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )
        memory.chat_memory.add_message(HumanMessage(content="Test message"))

        # Test
        result = self.conversation_manager.save_session_to_database(
            self.test_session_uuid, self.test_user_id, memory, mock_db_session
        )

        # Assert
        assert result is True
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

    @patch("libs.ai_service.app.services.conversation_manager.get_db")
    def test_save_session_to_database_update_existing(self, mock_get_db):
        """Test updating an existing session in database."""
        # Setup
        mock_db_session = Mock()
        mock_get_db.return_value = iter([mock_db_session])

        # Mock existing session
        mock_existing_session = Mock()
        mock_db_session.query.return_value.filter.return_value.first.return_value = (
            mock_existing_session
        )

        memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )
        memory.chat_memory.add_message(HumanMessage(content="Updated message"))

        # Test
        result = self.conversation_manager.save_session_to_database(
            self.test_session_uuid, self.test_user_id, memory, mock_db_session
        )

        # Assert
        assert result is True
        mock_db_session.add.assert_not_called()  # Should not add, just update
        mock_db_session.commit.assert_called_once()
        assert mock_existing_session.session_data is not None

    def test_create_new_session(self):
        """Test creating a new session."""
        with patch.object(
            self.conversation_manager, "save_session_to_database", return_value=True
        ):
            # Test
            session_uuid = self.conversation_manager.create_new_session(
                self.test_user_id
            )

            # Assert
            assert isinstance(session_uuid, str)
            # Validate UUID format
            uuid.UUID(session_uuid)  # Should not raise exception

            # Check session is cached
            cache_key = (session_uuid, self.test_user_id)
            assert cache_key in self.conversation_manager._session_cache

    def test_clear_session_cache(self):
        """Test clearing session from cache."""
        # Setup: Add session to cache
        memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )
        cache_key = (self.test_session_uuid, self.test_user_id)
        self.conversation_manager._session_cache[cache_key] = memory

        # Test
        self.conversation_manager.clear_session_cache(
            self.test_session_uuid, self.test_user_id
        )

        # Assert
        assert cache_key not in self.conversation_manager._session_cache

    def test_clear_session_cache_nonexistent(self):
        """Test clearing cache for non-existent session."""
        # Test - should not raise exception
        self.conversation_manager.clear_session_cache(
            self.test_session_uuid, self.test_user_id
        )

        # Assert - no exception raised
        assert True

    def test_get_cache_size(self):
        """Test getting cache size."""
        # Test empty cache
        assert self.conversation_manager.get_cache_size() == 0

        # Add some sessions
        memory1 = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )
        memory2 = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )

        self.conversation_manager._session_cache[("uuid1", 1)] = memory1
        self.conversation_manager._session_cache[("uuid2", 2)] = memory2

        # Test
        assert self.conversation_manager.get_cache_size() == 2

    @patch("libs.ai_service.app.services.conversation_manager.get_db")
    def test_get_user_sessions(self, mock_get_db):
        """Test getting user sessions from database."""
        # Setup
        mock_db_session = Mock()
        mock_get_db.return_value = iter([mock_db_session])

        # Mock session data
        mock_session = Mock()
        mock_session.session_uuid = uuid.UUID(self.test_session_uuid)
        mock_session.created_at = Mock()
        mock_session.created_at.isoformat.return_value = "2024-01-01T10:00:00"
        mock_session.last_activity = Mock()
        mock_session.last_activity.isoformat.return_value = "2024-01-01T11:00:00"
        mock_session.updated_at = Mock()
        mock_session.updated_at.isoformat.return_value = "2024-01-01T10:30:00"
        mock_session.session_data = {
            "messages": [
                {"type": "human", "content": "Hello, I need paint for my room"},
                {"type": "ai", "content": "I can help you with that!"},
            ]
        }

        mock_db_session.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
            mock_session
        ]

        # Test
        sessions = self.conversation_manager.get_user_sessions(
            self.test_user_id, limit=10
        )

        # Assert
        assert len(sessions) == 1
        session = sessions[0]
        assert session["session_uuid"] == self.test_session_uuid
        assert session["message_count"] == 2
        assert session["preview"] == "Hello, I need paint for my room"

    def test_cleanup_inactive_sessions(self):
        """Test cleaning up inactive sessions from cache."""
        # Setup: Fill cache beyond max size
        for i in range(5):
            memory = ConversationBufferMemory(
                memory_key="chat_history", return_messages=True
            )
            self.conversation_manager._session_cache[(f"uuid{i}", i)] = memory

        assert self.conversation_manager.get_cache_size() == 5

        # Test: Cleanup with max_cache_size=3
        self.conversation_manager.cleanup_inactive_sessions(max_cache_size=3)

        # Assert: Should have 3 sessions left
        assert self.conversation_manager.get_cache_size() == 3

    def test_serialization_of_messages(self):
        """Test message serialization for database storage."""
        memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )

        # Add messages with different types
        human_msg = HumanMessage(content="Hello")
        ai_msg = AIMessage(content="Hi there!")

        memory.chat_memory.add_message(human_msg)
        memory.chat_memory.add_message(ai_msg)

        with patch(
            "libs.ai_service.app.services.conversation_manager.get_db"
        ) as mock_get_db:
            mock_db_session = Mock()
            mock_get_db.return_value = iter([mock_db_session])
            mock_db_session.query.return_value.filter.return_value.first.return_value = (
                None
            )

            # Test serialization during save
            result = self.conversation_manager.save_session_to_database(
                self.test_session_uuid, self.test_user_id, memory, mock_db_session
            )

            # Assert
            assert result is True

            # Check the session data passed to the database
            call_args = mock_db_session.add.call_args[0][0]
            session_data = call_args.session_data

            assert len(session_data["messages"]) == 2
            assert session_data["messages"][0]["type"] == "human"
            assert session_data["messages"][0]["content"] == "Hello"
            assert session_data["messages"][1]["type"] == "ai"
            assert session_data["messages"][1]["content"] == "Hi there!"
