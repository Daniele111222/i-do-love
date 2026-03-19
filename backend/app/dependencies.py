"""FastAPI 依赖项：认证、数据库会话等。"""

from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.security import decode_token

# OAuth2 密码流认证方案
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> dict:
    """从 JWT 令牌中获取当前已认证用户。"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    user_id: str | None = payload.get("sub")  # type: ignore[assignment]
    if user_id is None:
        raise credentials_exception

    return {"user_id": int(user_id), "role": payload.get("role", "user")}


async def get_current_active_user(
    current_user: Annotated[dict, Depends(get_current_user)],
) -> dict:
    """获取当前活跃（未禁用）用户。"""
    # TODO: 从数据库检查用户是否处于活跃状态
    return current_user
