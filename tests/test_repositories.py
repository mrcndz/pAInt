from typing import Any, Dict, List, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from libs.api.app.core.entities import Environment, PaintProduct, Role, User
from libs.api.app.core.repositories_interfaces import (
    PaintProductRepository,
    UserRepository,
)

from .test_models import PaintProductModel, UserModel


class SyncSQLAlchemyUserRepository(UserRepository):
    """Sync SQLAlchemy implementation of user repository for testing."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def _model_to_entity(self, model: UserModel) -> User:
        """Convert SQLAlchemy model to domain entity."""
        return User(
            id=model.id,
            username=str(model.username),
            email=str(model.email),
            password_hash=str(model.password_hash),
            role=Role(str(model.role)) if model.role else Role.USER,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _entity_to_model_data(self, entity: User) -> dict[str, Any]:
        """Convert domain entity to model data dict."""
        return {
            "username": entity.username,
            "email": entity.email,
            "password_hash": entity.password_hash,
            "role": entity.role.value if entity.role else Role.USER.value,
        }

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        model = self.session.query(UserModel).filter(UserModel.id == user_id).first()
        return self._model_to_entity(model) if model else None

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        model = (
            self.session.query(UserModel).filter(UserModel.username == username).first()
        )
        return self._model_to_entity(model) if model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        model = self.session.query(UserModel).filter(UserModel.email == email).first()
        return self._model_to_entity(model) if model else None

    async def create(self, user: User) -> User:
        """Create new user."""
        model_data = self._entity_to_model_data(user)
        model = UserModel(**model_data)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._model_to_entity(model)

    async def update(self, user_id: int, user: User) -> Optional[User]:
        """Update existing user."""
        model = self.session.query(UserModel).filter(UserModel.id == user_id).first()
        if not model:
            return None

        model.username = user.username
        model.email = user.email
        model.password_hash = user.password_hash
        model.role = user.role.value if user.role else Role.USER.value

        self.session.commit()
        self.session.refresh(model)
        return self._model_to_entity(model)

    async def delete(self, user_id: int) -> bool:
        """Delete user."""
        model = self.session.query(UserModel).filter(UserModel.id == user_id).first()
        if not model:
            return False

        self.session.delete(model)
        self.session.commit()
        return True
