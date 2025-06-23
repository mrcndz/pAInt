from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .entities import ChatSession, PaintProduct, User


class PaintProductRepository(ABC):
    """Repository for paint products."""

    @abstractmethod
    async def create(self, product: PaintProduct) -> PaintProduct:
        """Create a new paint product."""
        pass

    @abstractmethod
    async def get_by_id(self, product_id: int) -> Optional[PaintProduct]:
        """Get paint product by ID."""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[PaintProduct]:
        """Get all paint products with pagination."""
        pass

    @abstractmethod
    async def search(
        self, filters: Dict[str, Any], skip: int = 0, limit: int = 100
    ) -> List[PaintProduct]:
        """Search paint products with filters."""
        pass

    @abstractmethod
    async def update(
        self, product_id: int, product: PaintProduct
    ) -> Optional[PaintProduct]:
        """Update paint product."""
        pass

    @abstractmethod
    async def delete(self, product_id: int) -> bool:
        """Delete paint product."""
        pass


class UserRepository(ABC):
    """Repository for users."""

    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user."""
        pass

    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        pass

    @abstractmethod
    async def update(self, user_id: int, user: User) -> Optional[User]:
        """Update user."""
        pass

    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        """Delete user."""
        pass


class ChatSessionRepository(ABC):
    """Repository for chat sessions."""

    @abstractmethod
    async def create(self, session: ChatSession) -> ChatSession:
        """Create a new chat session."""
        pass

    @abstractmethod
    async def get_by_id(self, session_id: str) -> Optional[ChatSession]:
        """Get chat session by ID."""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> List[ChatSession]:
        """Get chat sessions by user ID."""
        pass

    @abstractmethod
    async def update(
        self, session_id: str, session: ChatSession
    ) -> Optional[ChatSession]:
        """Update chat session."""
        pass

    @abstractmethod
    async def delete(self, session_id: str) -> bool:
        """Delete chat session."""
        pass
