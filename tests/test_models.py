import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import DECIMAL, TIMESTAMP, ForeignKey, String, Text, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sqlalchemy.ext.declarative import declarative_base

# Create a separate Base for testing to avoid conflicts
TestBase = declarative_base()


class UserModel(TestBase):
    """Test model for users (SQLite compatible)."""

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


class PaintProductModel(TestBase):
    """Test model for paint products (SQLite compatible)."""

    __tablename__ = "paint_products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    color: Mapped[str] = mapped_column(String(100), index=True)
    # Store as JSON string instead of ARRAY for SQLite compatibility
    surface_types: Mapped[Optional[str]] = mapped_column(Text, default="[]")
    environment: Mapped[str] = mapped_column(String(50), index=True)
    finish_type: Mapped[str] = mapped_column(String(50), index=True)
    # Store as JSON string instead of ARRAY for SQLite compatibility
    features: Mapped[Optional[str]] = mapped_column(Text, default="[]")
    product_line: Mapped[str] = mapped_column(String(100), index=True)
    price: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2))

    # AI-enriched fields
    ai_summary: Mapped[Optional[str]] = mapped_column(Text)
    # Store as JSON string instead of ARRAY for SQLite compatibility
    usage_tags: Mapped[Optional[str]] = mapped_column(Text, default="[]")
    
    # Vector embedding stored as JSON string for SQLite compatibility
    embedding: Mapped[Optional[str]] = mapped_column(Text)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp()
    )


class ChatSessionModel(TestBase):
    """Test model for chat sessions (SQLite compatible)."""

    __tablename__ = "chat_sessions"

    # Use string UUID for SQLite compatibility
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_uuid: Mapped[str] = mapped_column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    # Store as JSON for SQLite compatibility
    session_data: Mapped[Optional[str]] = mapped_column(Text, default="{}")
    last_activity: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=func.current_timestamp()
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp()
    )

    # Relationships
    user: Mapped["UserModel"] = relationship(back_populates="chat_sessions")