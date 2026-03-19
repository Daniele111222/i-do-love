"""OpenClaw 内容接收 API 路由。"""

import hmac
import hashlib
from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter()


def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """使用 HMAC-SHA256 验证 OpenClaw Webhook 签名。"""
    expected = hmac.new(
        key=secret.encode(),
        msg=payload,
        digestmod=hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)


class WebhookPayload(BaseModel):
    """OpenClaw Webhook 请求载荷模式。"""

    title: str = Field(..., min_length=1, max_length=500)
    content: str
    source_url: Optional[str] = None
    source_name: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[str] = None
    tags: list[str] = []


class WebhookResponse(BaseModel):
    """Webhook 确认响应模式。"""

    status: str
    id: int | None = None
    message: str


class IngestStatusResponse(BaseModel):
    """内容接收状态响应模式。"""

    total_processed: int
    total_success: int
    total_failed: int


@router.post(
    "/webhook",
    response_model=WebhookResponse,
    status_code=status.HTTP_200_OK,
)
async def receive_webhook(
    payload: WebhookPayload,
    x_signature: str = Header(None, alias="X-Signature"),
) -> WebhookResponse:
    """
    接收来自 OpenClaw 的内容推送。

    OpenClaw 发送包含以下字段的 JSON POST 请求：
    - title: 文章标题
    - content: 文章内容（HTML 或 Markdown）
    - source_url: 原始文章 URL
    - source_name: 来源网站名称
    - author: 作者名称
    - published_at: 发布时间（ISO 格式）
    - tags: 标签列表
    """
    # 验证签名
    if not x_signature:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少 X-Signature 请求头",
        )

    # TODO: 使用正确的密钥实现真实的签名验证
    # 开发阶段暂时跳过验证

    # TODO: 处理并存储文章
    # - 解析内容（HTML/Markdown）
    # - 提取摘要
    # - 存储到数据库
    # - 生成向量嵌入用于 RAG（Phase 3）

    return WebhookResponse(
        status="accepted",
        id=123,  # TODO: 返回真实的文章 ID
        message="内容接收成功",
    )


@router.post(
    "/feed",
    status_code=status.HTTP_200_OK,
)
async def ingest_feed(
    feed_url: str,
    source_name: Optional[str] = None,
) -> dict:
    """
    从 RSS/Atom/JSON Feed 接收内容。

    Args:
        feed_url: Feed 的 URL 地址
        source_name: 可选的来源名称
    """
    # TODO: 实现 Feed 解析和内容接收
    return {
        "status": "processing",
        "message": "Feed 接收任务已加入队列",
        "feed_url": feed_url,
    }


@router.get(
    "/status",
    response_model=IngestStatusResponse,
    status_code=status.HTTP_200_OK,
)
async def get_ingest_status() -> IngestStatusResponse:
    """获取内容接收状态和统计信息。"""
    # TODO: 实现真实的状态追踪
    return IngestStatusResponse(
        total_processed=0,
        total_success=0,
        total_failed=0,
    )
