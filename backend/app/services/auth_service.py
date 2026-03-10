"""Authentication service — password hashing, JWT creation, and user management."""

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.user import User
from app.schemas.user import TokenResponse, UserCreate

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service class for authentication and user management."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Password helpers ──────────────────────────────────────────────────

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)

    # ── User helpers ──────────────────────────────────────────────────────

    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create_user(self, payload: UserCreate) -> User:
        user = User(
            email=payload.email,
            full_name=payload.full_name,
            hashed_password=self.hash_password(payload.password),
            role=payload.role,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def authenticate(self, email: str, password: str) -> User | None:
        """Return the user if credentials are valid, otherwise None."""
        user = await self.get_user_by_email(email)
        if user is None or not user.is_active:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        # Update last login timestamp
        user.last_login_at = datetime.now(UTC)
        await self.db.flush()
        return user

    # ── Token helpers ─────────────────────────────────────────────────────

    @staticmethod
    def _create_token(data: dict[str, Any], expires_delta: timedelta) -> str:
        payload = data.copy()
        payload["exp"] = datetime.now(UTC) + expires_delta
        return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

    def create_tokens(self, user: User) -> TokenResponse:
        """Create access + refresh token pair for the given user."""
        access_token = self._create_token(
            {"sub": user.email, "role": user.role},
            timedelta(minutes=settings.access_token_expire_minutes),
        )
        refresh_token = self._create_token(
            {"sub": user.email, "type": "refresh"},
            timedelta(days=settings.refresh_token_expire_days),
        )
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def refresh_access_token(self, refresh_token: str) -> TokenResponse | None:
        """Validate a refresh token and issue a new token pair."""
        try:
            payload = jwt.decode(refresh_token, settings.secret_key, algorithms=[settings.algorithm])
            if payload.get("type") != "refresh":
                return None
            email: str = payload.get("sub", "")
        except JWTError:
            return None

        user = await self.get_user_by_email(email)
        if user is None or not user.is_active:
            return None
        return self.create_tokens(user)
