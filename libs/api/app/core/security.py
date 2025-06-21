import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from shared.database import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.services import AuthUseCases
from .entities import User
from .repositories import SQLAlchemyUserRepository

# Security
security = HTTPBearer()

# Environment variables
SECRET_KEY = os.getenv("JWT_SECRET", "super-secret-jwt-key")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))


def create_access_token(data: dict, expires_delta: Optional[int] = None) -> str:
    """Create JWT access token for testing and direct use."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + timedelta(hours=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_auth_use_cases(db: AsyncSession = Depends(get_async_db)) -> AuthUseCases:
    """Get authentication use cases."""
    user_repository = SQLAlchemyUserRepository(db)
    return AuthUseCases(
        user_repository=user_repository,
        secret_key=SECRET_KEY,
        algorithm=ALGORITHM,
        access_token_expire_hours=ACCESS_TOKEN_EXPIRE_HOURS,
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_use_cases: AuthUseCases = Depends(get_auth_use_cases),
) -> User:
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        user = await auth_use_cases.get_current_user(token)
        if user is None:
            raise credentials_exception
        return user
    except Exception:
        raise credentials_exception


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user (for future use if we add user activation)."""
    return current_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role."""
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return current_user


# for public endpoints
async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: AsyncSession = Depends(get_async_db),
) -> Optional[User]:
    """Get current user if authenticated, otherwise None."""
    if not credentials:
        return None

    try:
        auth_use_cases = AuthUseCases(
            user_repository=SQLAlchemyUserRepository(db),
            secret_key=SECRET_KEY,
            algorithm=ALGORITHM,
            access_token_expire_hours=ACCESS_TOKEN_EXPIRE_HOURS,
        )
        user = await auth_use_cases.get_current_user(credentials.credentials)
        return user
    except Exception:
        return None
