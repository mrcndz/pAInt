from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import ARRAY, DECIMAL, TIMESTAMP, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from ..core.database import Base


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

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp()
    )
