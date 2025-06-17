from sqlalchemy import ARRAY, DECIMAL, TIMESTAMP, Column, Integer, String, Text
from sqlalchemy.sql import func

from ..core.database import Base


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

