from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional


class Environment(str, Enum):
    """Paint environment suitability."""

    INTERNAL = "internal"
    EXTERNAL = "external"
    BOTH = "both"


class Role(str, Enum):
    """User roles."""

    USER = "user"
    ADMIN = "admin"


@dataclass
class PaintProduct:
    id: Optional[int] = None
    name: str = ""
    color: str = ""
    surface_types: List[str] = field(default_factory=list)
    environment: Environment = Environment.INTERNAL
    finish_type: str = ""
    features: List[str] = field(default_factory=list)
    product_line: str = ""
    price: Optional[Decimal] = None

    # AI-enriched fields
    ai_summary: Optional[str] = None
    usage_tags: List[str] = field(default_factory=list)

    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if not self.name:
            raise ValueError("Paint product name is required")
        if not self.color:
            raise ValueError("Paint color is required")
        if not self.finish_type:
            raise ValueError("Finish type is required")
        if not self.product_line:
            raise ValueError("Product line is required")


@dataclass
class User:
    id: Optional[int] = None
    username: str = ""
    email: str = ""
    password_hash: str = ""
    role: Role = Role.USER
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if not self.username:
            raise ValueError("Username is required")
        if not self.email:
            raise ValueError("Email is required")
        if "@" not in self.email:
            raise ValueError("Invalid email format")


@dataclass
class ChatSession:
    id: Optional[str] = None
    user_id: Optional[int] = None
    session_data: dict = field(default_factory=dict)
    last_activity: Optional[datetime] = None
    created_at: Optional[datetime] = None

