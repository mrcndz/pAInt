from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from ..core.entities import Role, User
from ..core.repositories_interfaces import UserRepository


class AuthUseCases:
    """Use cases for authentication operations."""

    def __init__(
        self,
        user_repository: UserRepository,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_hours: int = 24,
    ):
        self.user_repository = user_repository
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_hours = access_token_expire_hours
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return self.pwd_context.verify(plain_password, hashed_password)

    def _get_password_hash(self, password: str) -> str:
        """Generate password hash."""
        return self.pwd_context.hash(password)

    def _create_access_token(self, data: dict) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(hours=self.access_token_expire_hours)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password."""
        user = await self.user_repository.get_by_username(username)
        if not user:
            return None
        if not self._verify_password(password, user.password_hash):
            return None
        return user

    async def create_user(self, username: str, email: str, password: str) -> User:
        """Create a new user."""
        # Check if user already exists
        existing_user = await self.user_repository.get_by_username(username)
        if existing_user:
            raise ValueError("Username already exists")

        existing_email = await self.user_repository.get_by_email(email)
        if existing_email:
            raise ValueError("Email already exists")

        # Create user entity
        user = User(
            username=username,
            email=email,
            password_hash=self._get_password_hash(password),
            role=Role.USER,
        )

        return await self.user_repository.create(user)

    async def login(self, username: str, password: str) -> Optional[dict]:
        """Login user and return access token."""
        user = await self.authenticate_user(username, password)
        if not user:
            return None

        access_token = self._create_access_token(
            data={
                "sub": str(user.id),
                "username": user.username,
                "role": user.role.value,
            }
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
            },
        }

    async def verify_token(self, token: str) -> Optional[dict]:
        """Verify JWT token and return user data."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id: str = str(payload.get("sub"))
            username: str = str(payload.get("username"))
            role: str = str(payload.get("role"))

            if user_id is None or username is None:
                return None

            return {"user_id": int(user_id), "username": username, "role": role}
        except JWTError:
            return None

    async def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from token."""
        token_data = await self.verify_token(token)
        if not token_data:
            return None

        user = await self.user_repository.get_by_id(token_data["user_id"])
        return user
