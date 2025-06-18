from typing import Any, Dict, List, Optional

from shared.models import ChatSessionModel, PaintProductModel, UserModel
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .entities import ChatSession, Environment, PaintProduct, Role, User
from .repositories_interfaces import (
    ChatSessionRepository,
    PaintProductRepository,
    UserRepository,
)


class SQLAlchemyPaintProductRepository(PaintProductRepository):
    """SQLAlchemy implementation of paint product repository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _model_to_entity(self, model: PaintProductModel) -> PaintProduct:
        """Convert SQLAlchemy model to domain entity."""
        return PaintProduct(
            id=model.id if model.id is not None else None,
            name=str(model.name) if model.name else "",
            color=str(model.color) if model.color else "",
            surface_types=list(model.surface_types) if model.surface_types else [],
            environment=(
                Environment(str(model.environment))
                if model.environment
                else Environment.INTERNAL
            ),
            finish_type=str(model.finish_type) if model.finish_type else "",
            features=list(model.features) if model.features else [],
            product_line=str(model.product_line) if model.product_line else "",
            price=model.price,
            ai_summary=str(model.ai_summary) if model.ai_summary else None,
            usage_tags=list(model.usage_tags) if model.usage_tags else [],
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _entity_to_model_data(self, entity: PaintProduct) -> dict[str, Any]:
        """Convert domain entity to model data dict."""
        return {
            "name": entity.name,
            "color": entity.color,
            "surface_types": entity.surface_types,
            "environment": (
                entity.environment.value
                if entity.environment
                else Environment.INTERNAL.value
            ),
            "finish_type": entity.finish_type,
            "features": entity.features,
            "product_line": entity.product_line,
            "price": entity.price,
            "ai_summary": entity.ai_summary,
            "usage_tags": entity.usage_tags,
        }

    async def create(self, product: PaintProduct) -> PaintProduct:
        """Create a new paint product."""
        model_data = self._entity_to_model_data(product)
        model = PaintProductModel(**model_data)

        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._model_to_entity(model)

    async def get_by_id(self, product_id: int) -> Optional[PaintProduct]:
        """Get paint product by ID."""
        result = await self.session.execute(
            select(PaintProductModel).where(PaintProductModel.id == product_id)
        )
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[PaintProduct]:
        """Get all paint products with pagination."""
        result = await self.session.execute(
            select(PaintProductModel).offset(skip).limit(limit)
        )
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def search(
        self, filters: Dict[str, Any], skip: int = 0, limit: int = 100
    ) -> List[PaintProduct]:
        """Search paint products with filters."""
        query = select(PaintProductModel)
        conditions = []

        if "color" in filters:
            conditions.append(PaintProductModel.color.ilike(f"%{filters['color']}%"))

        if "environment" in filters:
            conditions.append(
                PaintProductModel.environment == str(filters["environment"])
            )

        if "finish_type" in filters:
            conditions.append(
                PaintProductModel.finish_type == str(filters["finish_type"])
            )

        if "product_line" in filters:
            conditions.append(
                PaintProductModel.product_line == str(filters["product_line"])
            )

        if "surface_types" in filters:
            conditions.append(
                PaintProductModel.surface_types.contains(
                    [str(filters["surface_types"])]
                )
            )

        if "features" in filters:
            conditions.append(
                PaintProductModel.features.contains([str(filters["features"])])
            )

        if "usage_tags" in filters:
            conditions.append(
                PaintProductModel.usage_tags.contains([str(filters["usage_tags"])])
            )

        if "name" in filters:
            conditions.append(PaintProductModel.name.ilike(f"%{filters['name']}%"))

        if conditions:
            query = query.where(and_(*conditions))

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def update(
        self, product_id: int, product: PaintProduct
    ) -> Optional[PaintProduct]:
        """Update paint product."""
        result = await self.session.execute(
            select(PaintProductModel).where(PaintProductModel.id == product_id)
        )
        model = result.scalar_one_or_none()

        if not model:
            return None

        # Update fields with proper type conversion
        model.name = str(product.name)
        model.color = str(product.color)
        model.surface_types = product.surface_types
        model.environment = (
            product.environment.value
            if product.environment
            else Environment.INTERNAL.value
        )
        model.finish_type = str(product.finish_type)
        model.features = product.features
        model.product_line = str(product.product_line)
        model.price = product.price
        model.ai_summary = product.ai_summary
        model.usage_tags = product.usage_tags

        await self.session.commit()
        await self.session.refresh(model)
        return self._model_to_entity(model)

    async def delete(self, product_id: int) -> bool:
        """Delete paint product."""
        result = await self.session.execute(
            select(PaintProductModel).where(PaintProductModel.id == product_id)
        )
        model = result.scalar_one_or_none()

        if not model:
            return False

        await self.session.delete(model)
        await self.session.commit()
        return True


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of user repository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _model_to_entity(self, model: UserModel) -> User:
        """Convert SQLAlchemy model to domain entity."""
        return User(
            id=int(model.id) if model.id is not None else None,
            username=str(model.username) if model.username else "",
            email=str(model.email) if model.email else "",
            password_hash=str(model.password_hash) if model.password_hash else "",
            role=Role(str(model.role)) if model.role else Role.USER,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _entity_to_model_data(self, user: User) -> dict[str, Any]:
        """Convert domain entity to model data dict."""
        return {
            "username": user.username,
            "email": user.email,
            "password_hash": user.password_hash,
            "role": user.role.value if user.role else Role.USER.value,
        }

    async def create(self, user: User) -> User:
        """Create a new user."""
        model_data = self._entity_to_model_data(user)
        model = UserModel(**model_data)

        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._model_to_entity(model)

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.username == str(username))
        )
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == str(email))
        )
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def update(self, user_id: int, user: User) -> Optional[User]:
        """Update user."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()

        if not model:
            return None

        model.username = str(user.username)
        model.email = str(user.email)
        model.password_hash = str(user.password_hash)
        model.role = user.role.value if user.role else Role.USER.value

        await self.session.commit()
        await self.session.refresh(model)
        return self._model_to_entity(model)

    async def delete(self, user_id: int) -> bool:
        """Delete user."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()

        if not model:
            return False

        await self.session.delete(model)
        await self.session.commit()
        return True
