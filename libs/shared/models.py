import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import ARRAY, DECIMAL, TIMESTAMP, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class UserModel(Base):
    """Model for users."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="user")
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp()
    )

    # Relationships
    chat_sessions: Mapped[List["ChatSessionModel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class PaintProductModel(Base):
    """Model for paint products."""

    __tablename__ = "paint_products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    color: Mapped[str] = mapped_column(String(100), index=True)
    surface_types: Mapped[List[str]] = mapped_column(ARRAY(Text), default=list)
    environment: Mapped[str] = mapped_column(String(50), index=True)
    finish_type: Mapped[str] = mapped_column(String(50), index=True)
    features: Mapped[List[str]] = mapped_column(ARRAY(Text), default=list)
    product_line: Mapped[str] = mapped_column(String(100), index=True)
    price: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2))

    # AI-enriched fields
    ai_summary: Mapped[Optional[str]] = mapped_column(Text)
    usage_tags: Mapped[List[str]] = mapped_column(ARRAY(Text), default=list)
    
    # Vector embedding for semantic search (1536 dimensions for OpenAI ada-002)
    embedding: Mapped[Optional[List[float]]] = mapped_column(Vector(1536))

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp()
    )


class ChatSessionModel(Base):
    """Model for chat sessions."""

    __tablename__ = "chat_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    session_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    last_activity: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=func.current_timestamp()
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=func.current_timestamp()
    )

    # Relationships
    user: Mapped["UserModel"] = relationship(back_populates="chat_sessions")
