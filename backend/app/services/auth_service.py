"""
认证服务层
处理用户注册、登录、Token 管理等业务逻辑
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    decode_token,
)
from app.models.user import User
from app.schemas.user import Token


class AuthService:
    """认证服务"""

    def __init__(self, db: AsyncSession):
        """初始化认证服务"""
        self.db = db

    async def register(
        self,
        email: str,
        password: str,
        nickname: Optional[str] = None,
    ) -> Token:
        """
        用户注册

        Args:
            email: 邮箱
            password: 密码
            nickname: 昵称（可选）

        Returns:
            Token: JWT 令牌

        Raises:
            ValueError: 邮箱已存在
        """
        # 检查邮箱是否已注册
        result = await self.db.execute(select(User).where(User.email == email))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise ValueError("该邮箱已被注册")

        # 哈希密码
        hashed_password = get_password_hash(password)

        # 创建用户
        new_user = User(
            email=email,
            nickname=nickname,
            hashed_password=hashed_password,
        )

        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

        # 生成 Token
        return self._create_tokens(new_user)

    async def login(self, email: str, password: str) -> Token:
        """
        用户登录

        Args:
            email: 邮箱
            password: 密码

        Returns:
            Token: JWT 令牌

        Raises:
            ValueError: 凭证无效或用户未激活
        """
        # 查找用户
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        # 验证密码
        if not user or not verify_password(password, user.hashed_password):
            raise ValueError("邮箱或密码错误")

        # 检查用户是否激活
        if not user.is_active:
            raise ValueError("用户已被禁用")

        # 生成 Token
        return self._create_tokens(user)

    async def refresh_token(self, refresh_token: str) -> Token:
        """
        刷新访问令牌

        Args:
            refresh_token: 刷新令牌

        Returns:
            Token: 新的 JWT 令牌

        Raises:
            ValueError: 无效的刷新令牌
        """
        # 解码刷新令牌
        payload = decode_token(refresh_token)

        if payload is None or payload.get("type") != "refresh":
            raise ValueError("无效的刷新令牌")

        user_id = payload.get("sub")
        if user_id is None:
            raise ValueError("无效的令牌载荷")

        # 获取用户
        result = await self.db.execute(select(User).where(User.id == int(user_id)))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise ValueError("用户不存在或已被禁用")

        # 生成新 Token
        return self._create_tokens(user)

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        根据 ID 获取用户

        Args:
            user_id: 用户 ID

        Returns:
            Optional[User]: 用户对象或 None
        """
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        根据邮箱获取用户

        Args:
            email: 邮箱

        Returns:
            Optional[User]: 用户对象或 None
        """
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    def _create_tokens(self, user: User) -> Token:
        """
        创建访问令牌和刷新令牌

        Args:
            user: 用户对象

        Returns:
            Token: JWT 令牌
        """
        # 访问令牌
        access_token = create_access_token(data={"sub": str(user.id), "role": user.role})

        # 刷新令牌
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
        )
