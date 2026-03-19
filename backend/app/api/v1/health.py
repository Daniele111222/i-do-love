"""健康检查 API 端点。"""

from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    """健康检查响应模式。"""

    status: str
    version: str


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
)
async def health_check() -> HealthResponse:
    """检查 API 健康状态。"""
    return HealthResponse(status="healthy", version="0.1.0")


@router.get(
    "/health/db",
    status_code=status.HTTP_200_OK,
)
async def health_check_db() -> dict:
    """检查数据库连接状态。"""
    # TODO: 实现真实的数据库健康检查
    return {"database": "healthy"}


@router.get(
    "/health/redis",
    status_code=status.HTTP_200_OK,
)
async def health_check_redis() -> dict:
    """检查 Redis 连接状态。"""
    # TODO: 实现真实的 Redis 健康检查
    return {"redis": "healthy"}
