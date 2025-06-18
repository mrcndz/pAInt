from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from ..core.entities import Environment


class PaintProductBase(BaseModel):
    """Base paint product schema."""

    name: str = Field(..., min_length=1, max_length=255)
    color: str = Field(..., min_length=1, max_length=100)
    surface_types: List[str] = Field(default_factory=list)
    environment: Environment
    finish_type: str = Field(..., min_length=1, max_length=50)
    features: List[str] = Field(default_factory=list)
    product_line: str = Field(..., min_length=1, max_length=100)
    price: Optional[Decimal] = Field(None, ge=0)


class PaintProductCreate(PaintProductBase):
    """Schema for creating paint product."""

    ai_summary: Optional[str] = None
    usage_tags: List[str] = Field(default_factory=list)


class PaintProductUpdate(BaseModel):
    """Schema for updating paint product."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    color: Optional[str] = Field(None, min_length=1, max_length=100)
    surface_types: Optional[List[str]] = None
    environment: Optional[Environment] = None
    finish_type: Optional[str] = Field(None, min_length=1, max_length=50)
    features: Optional[List[str]] = None
    product_line: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[Decimal] = Field(None, ge=0)
    ai_summary: Optional[str] = None
    usage_tags: Optional[List[str]] = None


class PaintProductResponse(PaintProductBase):
    """Schema for paint product response."""

    id: int
    ai_summary: Optional[str] = None
    usage_tags: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaintProductFilters(BaseModel):
    """Paint product search filters."""

    color: Optional[str] = None
    environment: Optional[Environment] = None
    finish_type: Optional[str] = None
    product_line: Optional[str] = None
    surface_type: Optional[str] = None
    feature: Optional[str] = None
    usage_tag: Optional[str] = None
    name: Optional[str] = None
    min_price: Optional[Decimal] = Field(None, ge=0)
    max_price: Optional[Decimal] = Field(None, ge=0)
