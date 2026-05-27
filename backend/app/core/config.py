"""应用程序配置，从环境变量加载。"""

from functools import lru_cache
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用程序配置类，通过环境变量或 .env 文件加载。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # 应用基础配置
    APP_NAME: str = "AI News Hub"
    APP_ENV: Literal["development", "test", "staging", "production"] = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # 数据库配置
    DATABASE_URL: str = "postgresql+asyncpg://ai_news:ai_news_secret@localhost:5432/ai_news"

    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"

    # 安全配置
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    AUTH_LOGIN_RATE_LIMIT: int = 10
    AUTH_REFRESH_RATE_LIMIT: int = 30
    AUTH_RATE_LIMIT_WINDOW_SECONDS: int = 60

    # CORS 配置
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # OpenAI 配置
    OPENAI_API_KEY: str = ""

    # Qdrant 配置 (Phase 3+)
    QDRANT_URL: str = ""

    # Webhook 配置
    WEBHOOK_SECRET: str = "change-me-in-production"

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        """Reject placeholder secrets in production-like runtime."""
        if self.APP_ENV != "production":
            return self

        if self.SECRET_KEY == "change-me-in-production":
            raise ValueError("SECRET_KEY must be changed in production")

        if self.WEBHOOK_SECRET == "change-me-in-production":
            raise ValueError("WEBHOOK_SECRET must be changed in production")

        return self


@lru_cache
def get_settings() -> Settings:
    """获取缓存的配置实例。"""
    return Settings()


settings = get_settings()
