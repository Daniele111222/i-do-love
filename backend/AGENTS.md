# AI News Hub - Backend

**技术栈**: Python 3.11+ + FastAPI + SQLAlchemy 2.0 + PostgreSQL + Redis + Qdrant
**项目类型**: REST API 后端服务
**分支**: main

---

## 🎯 核心开发理念

### 1. 分层架构设计

| 层级 | 目录 | 职责 |
|------|------|------|
| API 层 | `api/v1/` | 请求/响应处理，路由定义 |
| Service 层 | `services/` | 业务逻辑编排 |
| Model 层 | `models/` | 数据库模型定义 |
| Schema 层 | `schemas/` | 数据验证和序列化 |

**依赖方向**：API → Service → Model，禁止反向依赖，禁止在 API 层直接操作数据库。

### 2. 异步编程范式

- 所有数据库操作使用 `async/await` + `asyncpg`
- 避免同步阻塞调用
- 合理使用连接池

### 3. 代码质量

- 类型注解必须完整，mypy strict 检查
- 所有文件顶部必须 `from __future__ import annotations`（启用 PEP 563）
- 外部数据验证（Pydantic Schema）+ 边界条件处理

### 4. 日志规范

- 使用结构化日志，记录请求 ID、用户 ID、操作类型
- 日志级别：`DEBUG`（开发）、`INFO`（正常）、`WARNING`（警告）、`ERROR`（错误）
- **禁止**：打印 Token、密码、密钥等敏感信息
- 统一使用 `logging.getLogger(__name__)`

---

## ⚠️ 最高优先级原则（红线）

### 1. 分层强制执行
- **禁止**：在路由层直接操作数据库，必须通过 service 层
- **禁止**：在 API 层暴露数据库模型，必须转换为 schema
- **禁止**：返回裸 dict，必须使用 Pydantic schema 验证

### 2. 类型与配置规范
- **禁止**：硬编码配置，所有配置项通过 `core/config.py`
- **必须**：完整类型注解 + mypy strict 检查
- **必须**：返回值使用 Pydantic schema

### 3. 异步规范
- **禁止**：同步 ORM 调用阻塞事件循环
- **必须**：使用 `async_sessionmaker` 创建会话

### 4. 安全规范
- 密码存储：passlib + bcrypt
- JWT：python-jose + HS256
- **禁止**：在日志中打印 Token、密码等敏感数据

### 5. 代码审查同步
- 修改公共模块后需询问是否同步到 `AGENTS.md`

---

## 🛠 技术栈

### 核心技术栈

| 类别 | 技术选型 | 说明 |
|------|---------|------|
| **框架** | FastAPI 0.109+ | 高性能 ASGI 框架 |
| **语言** | Python 3.11+ | 类型注解严格模式 |
| **ORM** | SQLAlchemy 2.0+ | 异步 ORM |
| **数据库** | PostgreSQL + asyncpg | 异步驱动 |
| **验证** | Pydantic 2.5+ | 数据校验 |
| **配置** | pydantic-settings 2.1+ | 环境变量配置 |
| **认证** | python-jose + passlib | JWT + bcrypt |
| **代码格式** | ruff | line-length 100 |
| **缓存** | Redis 5.0+ | 会话、Token 缓存 |
| **向量数据库** | Qdrant | RAG 向量检索（Phase 3+） |

### Redis 使用场景

- 用户会话缓存
- JWT Token 黑名单（登出后失效）
- 频繁访问数据的缓存层

### Qdrant 使用场景（规划中）

- AI 新闻内容的向量嵌入存储
- 语义相似度搜索
- RAG（检索增强生成）支持

---

## 📋 API 与路由规范

### 路由注册流程

```
1. 在 api/v1/{module}.py 中定义路由
2. 在 api/v1/router.py 中 include_router 注册到 api_router
3. 在 main.py 中 include_router 注册到应用，prefix="/api/v1"
```

### 路由汇总示例

```python
from __future__ import annotations
from fastapi import APIRouter
from app.api.v1 import auth, health, ingest

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(health.router, tags=["健康检查"])
api_router.include_router(ingest.router, prefix="/ingest", tags=["内容接收"])
```

---

## 📐 数据模型规范

### 模型定义要点

```python
from __future__ import annotations
from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class User(Base):
    __tablename__ = "users"
    
    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # 索引字段
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
```

**要点**：
- 使用 `Mapped[type]` 注解 + `mapped_column` 定义列
- 主键/索引字段必须标注 `primary_key=True` / `index=True`
- 外键使用 `ForeignKey`，时间戳使用 `datetime.utcnow`
- 每个模型定义 `__repr__`

---

## 🔷 Pydantic Schema 规范

### Schema 分类与要点

| 类型 | 用途 | 特点 |
|------|------|------|
| Request Schema | 请求体验证 | 继承 BaseModel，Field 定义验证规则 |
| Response Schema | 响应序列化 | `model_config = ConfigDict(from_attributes=True)` |

**Schema 模板**：
```python
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserBase(BaseModel):
    email: EmailStr
    nickname: str | None = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_active: bool
    role: str
    created_at: datetime
    updated_at: datetime
```

**要点**：
- 使用 `EmailStr` 验证邮箱，`Field` 定义长度限制
- 类型使用 `str | None` 而非 `Optional[str]`
- 响应模式不暴露敏感字段（hashed_password 等）
- Token 等响应使用 `TokenResponse` 等明确命名

---

## 🔌 Service 服务层规范

### Service 编写要点

```python
from __future__ import annotations
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import Token

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, email: str, password: str, ...) -> Token:
        # 使用 select() 构建查询
        result = await self.db.execute(select(User).where(...))
        user = result.scalar_one_or_none()
        # 异常使用 ValueError 或自定义异常
        if user:
            raise ValueError("邮箱已存在")
```

**要点**：
- 每个 Domain 一个 Service 类，`__init__` 注入 `AsyncSession`
- 使用 `result.scalar_one_or_none()` 获取单个结果
- 异常使用 `ValueError` 或自定义异常类
- 复杂逻辑添加文档字符串

---

## ⚙️ 错误处理规范

### 异常处理模式

| 场景 | 处理方式 |
|------|---------|
| 参数验证失败 | Pydantic Schema 自动返回 422 |
| 业务逻辑错误 | `raise HTTPException(status_code=400, detail="...")` |
| 未认证 | `raise HTTPException(status_code=401, ...)` |
| 无权限 | `raise HTTPException(status_code=403, ...)` |
| 资源不存在 | `raise HTTPException(status_code=404, ...)` |
| 服务端错误 | `raise HTTPException(status_code=500, detail="内部错误")` |

**要点**：
- Service 层抛出 `ValueError` 或自定义异常
- API 层捕获并转换为 `HTTPException`
- 错误详情不暴露内部实现细节

---

## ⚙️ 核心配置与安全

### 配置管理（core/config.py）

- 使用 `pydantic-settings` 的 `BaseSettings`
- `model_config = SettingsConfigDict(env_file=".env", ...)`
- `@lru_cache` 缓存配置实例

**必需环境变量**：
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
ALLOWED_ORIGINS=["http://localhost:3000"]
OPENAI_API_KEY=sk-...
```

### JWT 与密码安全（core/security.py）

| 函数 | 用途 |
|------|------|
| `verify_password()` | 验证密码 |
| `get_password_hash()` | 哈希密码 |
| `create_access_token()` | 创建访问令牌 |
| `create_refresh_token()` | 创建刷新令牌 |
| `decode_token()` | 解码验证令牌 |

**要点**：
- 使用 `CryptContext(schemes=["bcrypt"])` 哈希密码
- JWT 载荷包含 `exp`, `type`, `iat` 字段
- `decode_token` 捕获 `JWTError` 返回 `None`

---

## 🗄️ 数据库与会话管理

### 数据库连接（database.py）

```python
from __future__ import annotations
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True, pool_size=10)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
```

### 依赖注入模板

```python
from __future__ import annotations
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user

router = APIRouter()

@router.get("/example")
async def get_example(
    db: Annotated[AsyncSession, Depends(get_db)],              # 数据库会话
    current_user: Annotated[dict, Depends(get_current_user)],  # 当前用户
) -> UserResponse:
    """接口说明。"""
    # 直接使用 current_user["user_id"] 获取用户 ID
    pass

@router.get("/admin")
async def admin_endpoint(
    current_user: Annotated[dict, Depends(get_current_user)],
):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    pass
```

**依赖注入模式**：
- `Annotated[T, Depends(get_db)]` - 数据库会话
- `Annotated[dict, Depends(get_current_user)]` - 当前认证用户
- 所有依赖在 `dependencies.py` 中定义

---

## 🚀 应用入口（main.py）

```python
from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(title="AI News Hub API", version="0.1.0", docs_url="/docs")

app.add_middleware(CORSMiddleware, allow_origins=settings.ALLOWED_ORIGINS, ...)
app.include_router(api_router, prefix="/api/v1")
```

**要点**：
- CORS 配置从 `settings.ALLOWED_ORIGINS` 读取
- API 前缀统一为 `/api/v1`

---

## 🧪 测试规范

### pytest 配置要点

- `asyncio_mode = "auto"` in `pyproject.toml`
- 使用 `AsyncSession` 进行异步测试
- 使用 `httpx.AsyncClient` + `ASGITransport` 测试 FastAPI

---

## ✅ 检查与验证机制

### 提交前检查清单

- [ ] 类型检查：`uv run mypy` 通过
- [ ] 代码格式：`uv run ruff check` 通过
- [ ] 异步规范：所有 DB 操作使用 `async/await`
- [ ] Schema 验证：返回值使用 Pydantic schema
- [ ] 敏感数据：Token、密码不打印到日志

### API 设计规范

#### 状态码

| 状态码 | 用途 |
|--------|------|
| 200 | 成功获取资源 |
| 201 | 成功创建资源 |
| 400 | 请求参数错误 |
| 401 | 未认证/认证失败 |
| 403 | 无权限访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### 代码审查关注点

**架构**：分层清晰？无 API 层直接操作 DB？异步模式正确？

**安全**：密码哈希？JWT 配置？敏感数据暴露？

**性能**：无 N+1？连接池合理？无阻塞操作？

---

## 📚 参考资源

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 文档](https://docs.sqlalchemy.org/en/20/)
- [Pydantic 文档](https://docs.pydantic.dev/)
- [pytest 文档](https://docs.pytest.org/)
- [ruff 文档](https://docs.astral.sh/ruff/)

---
