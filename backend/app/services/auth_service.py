"""Authentication service."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.schemas.user import CurrentUser, Token
from app.services.exceptions import AuthenticationError, ConflictError, NotFoundError


class AuthService:
    """Business logic for registration, login, tokens, and current users."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(
        self,
        email: str,
        password: str,
        nickname: str | None = None,
    ) -> Token:
        existing_user = await self.get_user_by_email(email)
        if existing_user is not None:
            raise ConflictError("Email is already registered")

        user = User(
            email=email,
            nickname=nickname,
            hashed_password=get_password_hash(password),
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return self._create_tokens(user)

    async def login(self, email: str, password: str) -> Token:
        user = await self.get_user_by_email(email)

        if user is None or not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password")

        if not user.is_active:
            raise AuthenticationError("User account is disabled")

        return self._create_tokens(user)

    async def refresh_token(self, refresh_token: str) -> Token:
        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != "refresh":
            raise AuthenticationError("Invalid refresh token")

        subject = payload.get("sub")
        if subject is None:
            raise AuthenticationError("Invalid token payload")

        try:
            user_id = int(subject)
        except (TypeError, ValueError) as exc:
            raise AuthenticationError("Invalid token subject") from exc

        user = await self.get_active_user_by_id(user_id)
        return self._create_tokens(user)

    async def get_current_user_from_token(self, token: str) -> CurrentUser:
        payload = decode_token(token)
        if payload is None or payload.get("type") != "access":
            raise AuthenticationError("Invalid access token")

        subject = payload.get("sub")
        if subject is None:
            raise AuthenticationError("Invalid token payload")

        try:
            user_id = int(subject)
        except (TypeError, ValueError) as exc:
            raise AuthenticationError("Invalid token subject") from exc

        user = await self.get_active_user_by_id(user_id)
        return CurrentUser(user_id=user.id, role=user.role)

    async def get_active_user_by_id(self, user_id: int) -> User:
        user = await self.get_user_by_id(user_id)
        if user is None:
            raise NotFoundError("User was not found")
        if not user.is_active:
            raise AuthenticationError("User account is disabled")
        return user

    async def get_user_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    def _create_tokens(self, user: User) -> Token:
        return Token(
            access_token=create_access_token(data={"sub": str(user.id), "role": user.role}),
            refresh_token=create_refresh_token(data={"sub": str(user.id)}),
        )
