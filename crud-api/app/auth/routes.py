from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_async_db
from ..core.security import get_auth_use_cases, get_current_user
from ..core.entities import User
from .schemas import LoginRequest, Token, UserCreate, UserResponse
from .services import AuthUseCases

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_data: UserCreate, auth_use_cases: AuthUseCases = Depends(get_auth_use_cases)
):
    """Register a new user."""
    try:
        user = await auth_use_cases.create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.id or not user.role or not user.username or not user.email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            created_at=user.created_at or datetime.now(),
            updated_at=user.updated_at or datetime.now(),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=Token)
async def login_user(
    login_data: LoginRequest, auth_use_cases: AuthUseCases = Depends(get_auth_use_cases)
):
    """Login user and return access token."""
    result = await auth_use_cases.login(
        username=login_data.username, password=login_data.password
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return Token(
        access_token=result["access_token"],
        token_type=result["token_type"],
        user=UserResponse(**result["user"]),
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """Get current user information."""
    user = current_user

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.id or not user.role or not user.username or not user.email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        created_at=user.created_at or datetime.now(),
        updated_at=user.updated_at or datetime.now(),
    )
