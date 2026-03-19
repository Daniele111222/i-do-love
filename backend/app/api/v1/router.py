"""API v1 路由汇总，注册所有子路由。"""

from fastapi import APIRouter
from app.api.v1 import auth, health, ingest

api_router = APIRouter()

# 注册子路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(health.router, tags=["健康检查"])
api_router.include_router(ingest.router, prefix="/ingest", tags=["内容接收"])
