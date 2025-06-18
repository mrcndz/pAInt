"""
Authentication schemas.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field

from ..core.entities import Role


class UserBase(BaseModel):
    """Base user schema."""

    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr


class UserCreate(UserBase):
    """Schema for user creation."""

    password: str = Field(..., min_length=6)


class UserResponse(UserBase):
    """Schema for user response."""

    id: int
    role: Role
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token response schema."""

    access_token: str
    token_type: str
    user: UserResponse


class LoginRequest(BaseModel):
    """Login request schema."""

    username: str
    password: str

