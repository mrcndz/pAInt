import uuid

from sqlalchemy import (
    ARRAY,
    DECIMAL,
    TIMESTAMP,
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class UserModel(Base):
    """Model for users."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="user")
    created_at = Column(TIMESTAMP, default=func.current_timestamp())
    updated_at = Column(
        TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp()
    )

    # Relationships
    chat_sessions = relationship(
        "ChatSessionModel", back_populates="user", cascade="all, delete-orphan"
    )


class PaintProductModel(Base):
    """Model for paint products."""

    __tablename__ = "paint_products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    color = Column(String(100), nullable=False, index=True)
    surface_types = Column(ARRAY(Text), nullable=False, default=[])
    environment = Column(String(50), nullable=False, index=True)
    finish_type = Column(String(50), nullable=False, index=True)
    features = Column(ARRAY(Text), default=[])
    product_line = Column(String(100), nullable=False, index=True)
    price = Column(DECIMAL(10, 2))

    # AI-enriched fields
    ai_summary = Column(Text)
    usage_tags = Column(ARRAY(Text), default=[])

    # Metadata
    created_at = Column(TIMESTAMP, default=func.current_timestamp())
    updated_at = Column(
        TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp()
    )


class ChatSessionModel(Base):
    """Model for chat sessions."""

    __tablename__ = "chat_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    session_data = Column(JSONB, default={})
    last_activity = Column(TIMESTAMP, default=func.current_timestamp())
    created_at = Column(TIMESTAMP, default=func.current_timestamp())

    # Relationships
    user = relationship("UserModel", back_populates="chat_sessions")
