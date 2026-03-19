"""用户相关的 Pydantic 数据校验模式。"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ============================================
# 用户基础模式
# ============================================


class UserBase(BaseModel):
    """用户基础模式，包含公共字段。"""

    email: EmailStr
    nickname: str | None = None


class UserCreate(UserBase):
    """创建新用户的请求模式。"""

    password: str = Field(..., min_length=8, max_length=128)


class UserUpdate(BaseModel):
    """更新用户信息的请求模式。"""

    nickname: str | None = None
    password: str | None = Field(None, min_length=8, max_length=128)


class UserResponse(UserBase):
    """用户响应模式（不含敏感数据）。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    role: str
    created_at: datetime
    updated_at: datetime


# ============================================
# 认证相关模式
# ============================================


class Token(BaseModel):
    """JWT 令牌响应模式。"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """JWT 令牌载荷模式。"""

    sub: str | None = None
    exp: datetime | None = None
    type: str | None = None


class LoginRequest(BaseModel):
    """登录请求模式。"""

    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """注册请求模式。"""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    nickname: str | None = None


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求模式。"""

    refresh_token: str
