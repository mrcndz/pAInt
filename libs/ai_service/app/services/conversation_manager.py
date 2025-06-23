import json
import logging
import uuid
from typing import Dict, List, Optional

from langchain.memory import ConversationBufferMemory
from langchain.schema import AIMessage, BaseMessage, HumanMessage
from shared.database import get_db
from shared.models import ChatSessionModel
from sqlalchemy.orm import Session

from ..config.config import config

logger = logging.getLogger(__name__)


class ConversationManager:
    """
    Manages conversation sessions with hybrid in-memory + database persistence.

    # In-memory cache for active sessions
    # Automatic database persistence
    # Session isolation per user
    # Message history serialization/deserialization
    """

    def __init__(self):
        # In-memory cache: (session_uuid, user_id) -> ConversationBufferMemory
        self._session_cache: Dict[tuple, ConversationBufferMemory] = {}

    def get_memory_for_session(
        self, session_uuid: str, user_id: int, db_session: Optional[Session] = None
    ) -> ConversationBufferMemory:
        """
        Get or create memory object for a session.

        Args:
            session_uuid: Public session identifier
            user_id: User ID for security verification
            db_session: Optional database session

        Returns:
            ConversationBufferMemory object for the session
        """
        logger.info(f"Getting memory for session {session_uuid}, user {user_id}")

        # Create cache key with user isolation
        cache_key = (session_uuid, user_id)

        # Check in-memory cache first
        if cache_key in self._session_cache:
            logger.debug(f"Found session {session_uuid} for user {user_id} in cache")
            return self._session_cache[cache_key]

        # Not in cache, load from database
        memory = self._load_memory_from_database(session_uuid, user_id, db_session)

        # Cache the memory object with user isolation
        self._session_cache[cache_key] = memory
        logger.debug(f"Cached memory for session {session_uuid}, user {user_id}")

        return memory

    def _load_memory_from_database(
        self, session_uuid: str, user_id: int, db_session: Optional[Session] = None
    ) -> ConversationBufferMemory:
        """
        Load conversation history from database and create memory object.

        Args:
            session_uuid: Public session identifier
            user_id: User ID for security verification
            db_session: Optional database session

        Returns:
            ConversationBufferMemory populated with history
        """
        use_provided_session = db_session is not None
        if not use_provided_session:
            db_session = next(get_db())

        try:
            # Query for session with security check (user_id must match)
            chat_session = (
                db_session.query(ChatSessionModel)
                .filter(
                    ChatSessionModel.session_uuid == session_uuid,
                    ChatSessionModel.user_id == user_id,
                )
                .first()
            )

            # Create new memory object
            memory = ConversationBufferMemory(
                memory_key="chat_history", return_messages=True
            )

            if chat_session and chat_session.session_data:
                # Load existing conversation history
                messages_data = chat_session.session_data.get("messages", [])
                logger.info(
                    f"Loading {len(messages_data)} messages for session {session_uuid}"
                )

                # Convert serialized messages back to LangChain message objects
                for msg_data in messages_data:
                    if msg_data["type"] == "human":
                        message = HumanMessage(content=msg_data["content"])
                    elif msg_data["type"] == "ai":
                        message = AIMessage(content=msg_data["content"])
                    else:
                        continue

                    # Add message to memory
                    memory.chat_memory.add_message(message)

                logger.info(f"Loaded conversation history for session {session_uuid}")
            else:
                logger.info(f"No existing history found for session {session_uuid}")

            return memory

        except Exception as e:
            logger.error(f"Error loading memory from database: {e}")
            # Return empty memory on error
            return ConversationBufferMemory(
                memory_key="chat_history", return_messages=True
            )
        finally:
            if not use_provided_session:
                db_session.close()

    def save_session_to_database(
        self,
        session_uuid: str,
        user_id: int,
        memory: ConversationBufferMemory,
        db_session: Optional[Session] = None,
    ) -> bool:
        """
        Save conversation memory to database.

        Args:
            session_uuid: Public session identifier
            user_id: User ID for the session
            memory: LangChain memory object to persist
            db_session: Optional database session

        Returns:
            True if saved successfully, False otherwise
        """
        use_provided_session = db_session is not None
        if not use_provided_session:
            db_session = next(get_db())

        try:
            logger.info(f"Saving session {session_uuid} to database")

            # Serialize messages from memory
            messages_data = []
            for message in memory.chat_memory.messages:
                if isinstance(message, HumanMessage):
                    msg_data = {
                        "type": "human",
                        "content": message.content,
                        "timestamp": message.additional_kwargs.get("timestamp"),
                    }
                elif isinstance(message, AIMessage):
                    msg_data = {
                        "type": "ai",
                        "content": message.content,
                        "timestamp": message.additional_kwargs.get("timestamp"),
                    }
                else:
                    continue

                messages_data.append(msg_data)

            session_data = {
                "messages": messages_data,
                "message_count": len(messages_data),
            }

            # Try to find existing session
            chat_session = (
                db_session.query(ChatSessionModel)
                .filter(
                    ChatSessionModel.session_uuid == session_uuid,
                    ChatSessionModel.user_id == user_id,
                )
                .first()
            )

            if chat_session:
                # Update existing session
                chat_session.session_data = session_data
                logger.debug(f"Updated existing session {session_uuid}")
            else:
                # Create new session
                chat_session = ChatSessionModel(
                    session_uuid=uuid.UUID(session_uuid),
                    user_id=user_id,
                    session_data=session_data,
                )
                db_session.add(chat_session)
                logger.debug(f"Created new session {session_uuid}")

            db_session.commit()
            logger.info(
                f"Successfully saved session {session_uuid} with {len(messages_data)} messages"
            )
            return True

        except Exception as e:
            logger.error(f"Error saving session to database: {e}")
            db_session.rollback()
            return False
        finally:
            if not use_provided_session:
                db_session.close()

    def create_new_session(self, user_id: int) -> str:
        """
        Create a new conversation session.

        Args:
            user_id: User ID for the new session

        Returns:
            New session UUID as string
        """
        session_uuid = str(uuid.uuid4())
        logger.info(f"Creating new session {session_uuid} for user {user_id}")

        # Create empty memory for new session
        memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )

        # Cache the memory with user isolation
        cache_key = (session_uuid, user_id)
        self._session_cache[cache_key] = memory

        # Save to database
        self.save_session_to_database(session_uuid, user_id, memory)

        return session_uuid

    def get_latest_session_uuid(self, user_id: int) -> Optional[str]:
        """
        Get the most recent session UUID for a user.

        Args:
            user_id: User ID to get latest session for

        Returns:
            Latest session UUID as string, or None if no sessions exist
        """
        db_session = next(get_db())
        
        try:
            # Get the most recent session for this user
            latest_session = (
                db_session.query(ChatSessionModel)
                .filter(ChatSessionModel.user_id == user_id)
                .order_by(ChatSessionModel.last_activity.desc())
                .first()
            )
            
            if latest_session:
                return str(latest_session.session_uuid)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting latest session for user {user_id}: {e}")
            return None
        finally:
            db_session.close()

    def clear_session_cache(self, session_uuid: str, user_id: int) -> None:
        """
        Remove session from in-memory cache.

        Args:
            session_uuid: Session to remove from cache
            user_id: User ID for the session
        """
        cache_key = (session_uuid, user_id)
        if cache_key in self._session_cache:
            del self._session_cache[cache_key]
            logger.debug(
                f"Cleared session {session_uuid} for user {user_id} from cache"
            )

    def get_cache_size(self) -> int:
        """Get current cache size for monitoring."""
        return len(self._session_cache)

    def get_user_sessions(
        self, user_id: int, limit: Optional[int] = None
    ) -> List[dict]:
        """
        Get all chat sessions for a specific user.

        Args:
            user_id: User ID to get sessions for
            limit: Maximum number of sessions to return

        Returns:
            List of session dictionaries with metadata
        """
        # Use config default if no limit provided
        if limit is None:
            limit = config.CONVERSATION_MAX_USER_SESSIONS

        db_session = next(get_db())

        try:

            # Query user's sessions ordered by last activity (most recent first)
            sessions = (
                db_session.query(ChatSessionModel)
                .filter(ChatSessionModel.user_id == user_id)
                .order_by(ChatSessionModel.last_activity.desc())
                .limit(limit)
                .all()
            )

            session_list = []
            for session in sessions:
                # Count messages in session data
                session_data = session.session_data or {}
                messages = session_data.get("messages", [])
                message_count = len(messages)

                # Get first user message as preview
                preview = "No messages"
                for msg in messages:
                    if msg.get("type") == "human" and msg.get("content"):
                        preview = msg["content"][:100] + (
                            "..." if len(msg["content"]) > 100 else ""
                        )
                        break

                session_info = {
                    "session_uuid": str(session.session_uuid),
                    "created_at": (
                        session.created_at.isoformat() if session.created_at else None
                    ),
                    "last_activity": (
                        session.last_activity.isoformat()
                        if session.last_activity
                        else None
                    ),
                    "updated_at": (
                        session.updated_at.isoformat() if session.updated_at else None
                    ),
                    "message_count": message_count,
                    "preview": preview,
                    "is_active": str(session.session_uuid)
                    in [key[0] for key in self._session_cache.keys()],
                }
                session_list.append(session_info)

            logger.info(f"Retrieved {len(session_list)} sessions for user {user_id}")
            return session_list

        except Exception as e:
            logger.error(f"Error getting user sessions: {e}")
            raise e
        finally:
            db_session.close()

    def cleanup_inactive_sessions(self, max_cache_size: Optional[int] = None) -> None:
        """
        Clean up cache if it gets too large removing oldest entries.

        Args:
            max_cache_size: Maximum number of sessions to keep in cache
        """
        # Use config default if no max_cache_size provided
        if max_cache_size is None:
            max_cache_size = config.CONVERSATION_MAX_CACHE_SIZE

        if len(self._session_cache) > max_cache_size:
            # Remove oldest sessions (simple cleanup strategy)
            sessions_to_remove = len(self._session_cache) - max_cache_size
            sessions_to_delete = list(self._session_cache.keys())[:sessions_to_remove]

            for session_uuid in sessions_to_delete:
                del self._session_cache[session_uuid]

            logger.info(f"Cleaned up {sessions_to_remove} sessions from cache")


# Global instance
conversation_manager = ConversationManager()


def get_conversation_manager() -> ConversationManager:
    """Get the global conversation manager instance."""
    return conversation_manager
