import os
from datetime import datetime
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from shared.database import get_db
from shared.models import UserModel
from sqlalchemy.orm import Session

# Security
security = HTTPBearer()

# Environment variables (same as API service)
SECRET_KEY = os.getenv("JWT_SECRET", "super-secret-jwt-key")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


def decode_jwt_token(token: str) -> Optional[dict]:
    """
    Decode JWT token and extract user information.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> int:
    """
    Extract user ID from JWT token.

    Args:
        credentials: HTTP authorization credentials
        db: Database session

    Returns:
        User ID

    Raises:
        HTTPException: If token is invalid or user doesn't exist
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = decode_jwt_token(token)

        if payload is None:
            raise credentials_exception

        # Extract user info from token (check both user_id and sub for compatibility)
        user_id: Optional[int] = payload.get("user_id") or payload.get("sub")
        if user_id is None:
            raise credentials_exception

        # Convert to int if it's a string
        if isinstance(user_id, str):
            user_id = int(user_id)

        # Verify user exists in database
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if user is None:
            raise credentials_exception

        return user_id

    except Exception:
        raise credentials_exception


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> UserModel:
    """
    Get current authenticated user from JWT token.

    Args:
        credentials: HTTP authorization credentials
        db: Database session

    Returns:
        UserModel instance

    Raises:
        HTTPException: If token is invalid or user doesn't exist
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = decode_jwt_token(token)

        if payload is None:
            raise credentials_exception

        # Extract user info from token (check both user_id and sub for compatibility)
        user_id: Optional[int] = payload.get("user_id") or payload.get("sub")
        if user_id is None:
            raise credentials_exception

        # Convert to int if it's a string
        if isinstance(user_id, str):
            user_id = int(user_id)

        # Get user from database
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if user is None:
            raise credentials_exception

        return user

    except Exception:
        raise credentials_exception


def get_optional_current_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: Session = Depends(get_db),
) -> Optional[int]:
    """
    Get current user ID if authenticated, otherwise None.
    For optional authentication on endpoints.

    Args:
        credentials: Optional HTTP authorization credentials
        db: Database session

    Returns:
        User ID or None
    """
    if not credentials:
        return None

    try:
        token = credentials.credentials
        payload = decode_jwt_token(token)

        if payload is None:
            return None

        user_id: Optional[int] = payload.get("user_id")

        if user_id is None:
            return None

        # Verify user exists
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if user is None:
            return None

        return user_id

    except Exception:
        return None

