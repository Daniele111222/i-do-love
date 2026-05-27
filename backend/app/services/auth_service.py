"""Authentication service."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import audit_logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    hash_token,
    verify_password,
)
from app.models.refresh_token_session import RefreshTokenSession
from app.models.user import User
from app.schemas.user import CurrentUser, RefreshTokenSessionResponse, Token
from app.services.exceptions import AuthenticationError, ConflictError, NotFoundError


def ensure_aware_utc(value: datetime) -> datetime:
    """Treat naive database datetimes as UTC for SQLite compatibility."""
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value


class AuthService:
    """Business logic for registration, login, tokens, and current users."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(
        self,
        email: str,
        password: str,
        nickname: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
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

        tokens = await self._create_tokens(
            user,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await self.db.commit()
        audit_logger.info(
            "auth_register_success",
            extra={"user_id": user.id, "email": user.email},
        )
        return tokens

    async def login(
        self,
        email: str,
        password: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> Token:
        user = await self.get_user_by_email(email)

        if user is None or not verify_password(password, user.hashed_password):
            audit_logger.info("auth_login_failed", extra={"email": email, "reason": "invalid"})
            raise AuthenticationError("Invalid email or password")

        if not user.is_active:
            audit_logger.info(
                "auth_login_failed",
                extra={"user_id": user.id, "email": email, "reason": "disabled"},
            )
            raise AuthenticationError("User account is disabled")

        tokens = await self._create_tokens(
            user,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await self.db.commit()
        audit_logger.info(
            "auth_login_success",
            extra={"user_id": user.id, "email": user.email},
        )
        return tokens

    async def refresh_token(
        self,
        refresh_token: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> Token:
        user_id, token_session = await self.validate_refresh_token_session(refresh_token)

        user = await self.get_active_user_by_id(user_id)
        token_session.revoked_at = datetime.now(UTC)
        tokens = await self._create_tokens(
            user,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await self.db.commit()
        audit_logger.info(
            "auth_refresh_success",
            extra={"user_id": user.id, "session_id": token_session.id},
        )
        return tokens

    async def logout(self, refresh_token: str) -> None:
        user_id, token_session = await self.validate_refresh_token_session(refresh_token)
        token_session.revoked_at = datetime.now(UTC)
        await self.db.commit()
        audit_logger.info(
            "auth_logout_success",
            extra={"user_id": user_id, "session_id": token_session.id},
        )

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
        session_id = payload.get("sid")
        return CurrentUser(
            user_id=user.id,
            role=user.role,
            session_id=str(session_id) if session_id is not None else None,
        )

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

    async def get_refresh_token_session(
        self,
        token_id: str,
        refresh_token: str,
    ) -> RefreshTokenSession | None:
        result = await self.db.execute(
            select(RefreshTokenSession).where(
                RefreshTokenSession.token_id == token_id,
                RefreshTokenSession.token_hash == hash_token(refresh_token),
            )
        )
        return result.scalar_one_or_none()

    async def list_refresh_token_sessions(
        self,
        user_id: int,
        current_session_id: str | None = None,
    ) -> list[RefreshTokenSessionResponse]:
        result = await self.db.execute(
            select(RefreshTokenSession)
            .where(RefreshTokenSession.user_id == user_id)
            .order_by(RefreshTokenSession.created_at.desc(), RefreshTokenSession.id.desc())
        )

        sessions = result.scalars().all()
        now = datetime.now(UTC)
        return [
            RefreshTokenSessionResponse(
                id=session.id,
                created_at=session.created_at,
                expires_at=session.expires_at,
                revoked_at=session.revoked_at,
                ip_address=session.ip_address,
                user_agent=session.user_agent,
                is_current=(
                    current_session_id is not None and session.token_id == current_session_id
                ),
                is_revoked=(
                    session.revoked_at is not None
                    or ensure_aware_utc(session.expires_at) <= now
                ),
            )
            for session in sessions
        ]

    async def revoke_all_refresh_token_sessions(self, user_id: int) -> None:
        revoked_at = datetime.now(UTC)
        await self.db.execute(
            update(RefreshTokenSession)
            .where(
                RefreshTokenSession.user_id == user_id,
                RefreshTokenSession.revoked_at.is_(None),
            )
            .values(revoked_at=revoked_at)
        )
        await self.db.commit()
        audit_logger.info("auth_sessions_revoked", extra={"user_id": user_id})

    async def validate_refresh_token_session(
        self,
        refresh_token: str,
    ) -> tuple[int, RefreshTokenSession]:
        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != "refresh":
            raise AuthenticationError("Invalid refresh token")

        subject = payload.get("sub")
        token_id = payload.get("jti")
        if subject is None or token_id is None:
            raise AuthenticationError("Invalid token payload")

        try:
            user_id = int(subject)
        except (TypeError, ValueError) as exc:
            raise AuthenticationError("Invalid token subject") from exc

        token_session = await self.get_refresh_token_session(token_id, refresh_token)
        if token_session is None:
            raise AuthenticationError("Invalid refresh token")
        if token_session.revoked_at is not None:
            raise AuthenticationError("Invalid refresh token")
        if ensure_aware_utc(token_session.expires_at) <= datetime.now(UTC):
            raise AuthenticationError("Invalid refresh token")
        if token_session.user_id != user_id:
            raise AuthenticationError("Invalid refresh token")

        return user_id, token_session

    async def _create_tokens(
        self,
        user: User,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> Token:
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        token = Token(access_token="", refresh_token=refresh_token)
        payload = decode_token(token.refresh_token)
        if payload is None or payload.get("jti") is None or payload.get("exp") is None:
            raise AuthenticationError("Invalid refresh token payload")

        expires_at = payload["exp"]
        if isinstance(expires_at, int | float):
            expires_at = datetime.fromtimestamp(expires_at, UTC)

        self.db.add(
            RefreshTokenSession(
                user_id=user.id,
                token_id=str(payload["jti"]),
                token_hash=hash_token(token.refresh_token),
                expires_at=expires_at,
                ip_address=ip_address,
                user_agent=user_agent,
            )
        )
        token.access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role, "sid": str(payload["jti"])}
        )
        return token
