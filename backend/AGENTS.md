# AI News Hub Backend - AGENTS.md

**技术栈**: FastAPI + SQLAlchemy async + Pydantic + JWT + pytest-asyncio
**项目类型**: backend-service
**目标读者**: AI 编程助手优先，人类开发者次之

---

## 核心开发理念

### 1. 接口契约优先
- **必须**让 API 入参和出参通过 Pydantic schema 表达；路由返回裸 `dict` 只允许用于仍未成型的占位接口。
- **必须**让 `/api/v1` 下的路由、schema、测试一起变更；否则前端和 Swagger 会读到旧契约。
- **禁止**静默修改已有响应字段含义；认证、健康检查、webhook 已有测试依赖这些响应结构。

### 2. 路由薄、服务厚
- **必须**把业务流程放在 `app/services/`；路由只做依赖注入、调用服务、映射 HTTP 状态码。
- **必须**用 `app.services.exceptions` 中的 typed exception 表示可预期业务错误；否则路由无法稳定转换为 4xx。
- **禁止**在路由里散落密码哈希、JWT 生成、数据库编排；这些逻辑当前集中在 `AuthService`。

### 3. 运行时状态要真实
- **必须**让依赖健康检查执行真实探测；`/health/db` 已执行 `SELECT 1`，`/health/redis` 已执行 Redis `ping`。
- **禁止**在依赖不可用时仍返回 `"healthy"`；这会让 Docker healthcheck、部署探针和排障结果失真。
- **必须**让 webhook 签名基于原始 request body 校验；重序列化后的 JSON 会改变 HMAC 输入。

### 4. 小步演进，少写会腐烂的规则
- **必须**以当前代码为准写约定；不存在的 repository 层、迁移目录、队列任务不得写成已建立规范。
- **优先**记录边界、约束、验证命令，不维护完整文件清单；文件列表随 PR 演进很快过期。
- **必须**在新增跨模块公共规则时同步评估本文档；否则后续 AI 会继续按旧边界改代码。

## 项目背景与最高优先级原则

### 项目现状
- 后端是 AI News Hub 的 FastAPI 服务，当前覆盖认证、健康检查和内容接收占位能力。
- 数据层使用 SQLAlchemy 2.0 async ORM，生产默认指向 PostgreSQL，测试使用内存 SQLite。
- Redis 已用于健康检查连接验证，Qdrant / OpenAI / RAG 能力仍处于后续阶段，不能写成已落地业务。
- 目前没有 Alembic 迁移目录；`scripts/create_tables.py` 只适合本地初始化和早期开发。

### 最高优先级原则（红线）

#### 1. 技术栈强制对齐
- **必须**使用 `pyproject.toml` 中已配置的 FastAPI、SQLAlchemy async、Pydantic、python-jose、passlib、redis、pytest-asyncio、ruff、mypy。
- **禁止**为同一职责引入第二套框架或 ORM；例如 Django ORM、Tortoise ORM、Flask、Peewee 会制造双栈维护成本。
- **禁止**手写生产依赖版本到本文档；依赖版本以 `pyproject.toml` / `uv.lock` 为准，文档版本号会快速过期。

#### 2. API 入口与版本规则
- **必须**把 v1 API 注册在 `app/api/v1/router.py`，并通过 `app.main` 的 `app.include_router(api_router, prefix="/api/v1")` 暴露。
- **必须**按业务域拆分 `app/api/v1/*.py`；新域不要堆进 `router.py`，否则路由聚合层会承担业务细节。
- **禁止**绕过 `/api/v1` 增加业务接口；根路径 `/` 只用于基础 API metadata。

#### 3. 认证与用户上下文
- **必须**通过 `get_current_user` 获取认证上下文，并使用 `app.schemas.user.CurrentUser`；裸 `dict` 会丢失类型约束。
- **必须**让 access token 的 `type` 为 `"access"`，refresh token 的 `type` 为 `"refresh"`；`AuthService` 依赖该字段区分令牌用途。
- **禁止**把 `hashed_password`、token、secret 写入响应或日志；这会造成凭据泄露。
- **必须**从数据库确认用户仍存在且 `is_active=True`；仅信任 JWT payload 会让停用账号继续访问接口。

#### 4. 数据层与模型注册
- **必须**让新模型继承 `app.models.base.Base`，并从 `app/models/__init__.py` 导出；`Base.metadata.create_all` 依赖可发现的 metadata。
- **必须**使用 `AsyncSession` 和 SQLAlchemy async 查询；同步 Session 会阻塞 FastAPI async worker。
- **禁止**在服务层拼接不受控 raw SQL；必要 raw SQL 只能用于明确的基础设施探测，并使用 SQLAlchemy `text()`。
- **必须**使用 timezone-aware 时间；模型中的 instant 字段保持 `DateTime(timezone=True)` 和 `datetime.now(UTC)`。

#### 5. 配置与密钥
- **必须**通过 `app/core/config.py` 的 `Settings` 读取配置；硬编码 URL、secret、算法会破坏环境隔离。
- **必须**让 `.env.example` 与 `Settings` 字段保持同步；缺失示例会让本地启动不可复现。
- **禁止**提交真实 `SECRET_KEY`、`WEBHOOK_SECRET`、`OPENAI_API_KEY`；泄露后无法通过代码修复补救。
- **必须**把 `ALLOWED_ORIGINS` 作为 JSON 数组或 Pydantic 可解析的列表传入；字符串拼接格式容易被误解析。

#### 6. 文档同步规则
- **必须**在新增公共目录、跨模块服务、认证规则、数据库迁移机制、队列/RAG 基础设施后检查是否需要更新本文档。
- **禁止**把计划中的 Phase 能力写成当前事实；Qdrant、OpenAI、RAG 目前只能描述为预留或后续阶段。
- **必须**发现本文档与代码冲突时以代码为准，并立即修正文档；错误规则比没有规则更危险。

## 技术栈与项目结构

<!-- 易过期内容：目录、工具和依赖清单变更时需要同步验证。依赖版本以 pyproject.toml / uv.lock 为准。 -->

### 核心技术栈

| 类别 | 技术选型 | 项目内用途 |
| --- | --- | --- |
| Web 框架 | FastAPI | HTTP API、依赖注入、OpenAPI 文档 |
| 数据访问 | SQLAlchemy async + asyncpg | PostgreSQL 异步 ORM 与连接池 |
| Schema | Pydantic v2 | 请求、响应、认证上下文模型 |
| 认证 | python-jose + passlib bcrypt | JWT 编解码与密码哈希 |
| 缓存/外部依赖 | redis.asyncio | Redis 连接与健康检查 |
| 测试 | pytest + pytest-asyncio + httpx | 异步 API 测试 |
| 质量工具 | Ruff + mypy strict | 风格、静态类型检查 |
| 包管理 | uv | 依赖同步和命令运行 |

### 目录结构

```text
backend/
├── app/
│   ├── api/v1/        # FastAPI v1 路由，按业务域拆分
│   ├── core/          # Settings、安全与密码/JWT 基础设施
│   ├── models/        # SQLAlchemy Base 与 ORM 模型
│   ├── schemas/       # Pydantic 请求、响应、上下文 schema
│   ├── services/      # 业务服务与 typed exceptions
│   ├── database.py    # async engine、session factory、get_db
│   ├── db_init.py     # 早期开发用建表辅助
│   └── main.py        # FastAPI app 与中间件注册
├── scripts/           # 本地维护脚本
├── tests/             # pytest-asyncio API 测试
├── pyproject.toml     # Python 依赖、pytest、ruff、mypy 配置
└── Dockerfile         # 后端镜像构建
```

## 接口与领域规范

### 路由层
- 路由模块放在 `app/api/v1/`，并由 `app/api/v1/router.py` 聚合。
- 路由函数使用 `Annotated[..., Depends(...)]` 注入依赖，保持当前 `auth.py` 的写法。
- 路由只捕获可预期的 service exception，并转换成 `HTTPException`；未知异常交给 FastAPI 默认 5xx 处理。
- 新增接口必须补对应测试；当前测试以 `httpx.AsyncClient` 直接请求 `/api/v1/...`。

### Service 层
- 业务服务放在 `app/services/`，构造函数接收 `AsyncSession`。
- 服务内部负责数据库读写、commit / refresh、业务异常抛出。
- 服务返回 Pydantic schema 或 ORM 对象时，路由必须明确 `response_model`，避免泄露模型内部字段。
- 预期错误使用 `ConflictError`、`AuthenticationError`、`PermissionDeniedError`、`NotFoundError`；新增错误先扩展 `app/services/exceptions.py`。

当前服务模式：

```python
class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def login(self, email: str, password: str) -> Token:
        user = await self.get_user_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password")
        return self._create_tokens(user)
```

当前路由映射模式：

```python
@router.post("/login", response_model=Token)
async def login(
    request: LoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> Token:
    try:
        return await auth_service.login(email=request.email, password=request.password)
    except AuthenticationError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
```

### Schema 层
- Pydantic schema 放在 `app/schemas/`，按领域拆分；用户和认证 schema 当前在 `app/schemas/user.py`。
- ORM 到响应模型转换使用 `ConfigDict(from_attributes=True)` 和 `model_validate`。
- 响应 schema 禁止包含 `hashed_password`、secret、内部 token payload。
- `CurrentUser` 只保存请求上下文需要的最小字段；需要完整用户资料时通过服务重新查库。

## 数据库与迁移

### 当前数据库规则
- 生产默认数据库 URL 为 PostgreSQL asyncpg；测试通过 `tests/conftest.py` 覆盖为内存 SQLite。
- 新模型必须兼容 PostgreSQL 和当前测试 SQLite；若使用 PostgreSQL 专有类型，测试层需同步调整。
- `app/database.py` 是唯一 session factory 来源；不要在业务模块创建第二个 engine。
- `pool_pre_ping=True` 已用于生产 engine；不要移除，否则长期连接断开时更难定位。

### 迁移现状
- 项目依赖包含 Alembic，但当前未发现 `alembic.ini` 或迁移目录。
- 在迁移体系落地前，`scripts/create_tables.py` 只用于早期开发建表，不代表生产迁移方案。
- 一旦新增 Alembic，必须把迁移命令、目录、模型注册规则同步到本文档。

## 安全与外部输入

### JWT 与密码
- 密码哈希统一使用 `app/core/security.py` 的 `get_password_hash` 和 `verify_password`。
- JWT 创建统一使用 `create_access_token` / `create_refresh_token`，解码统一使用 `decode_token`。
- token subject 当前按 `str(user.id)` 写入，并在服务中转回 `int`；改主键类型时必须同步 token、schema、测试。

### Webhook
- `POST /api/v1/ingest/webhook` 必须校验 `X-Signature`。
- 签名格式为 `sha256=<hexdigest>`，算法为 HMAC-SHA256。
- 校验输入必须是 `await request.body()` 得到的原始字节；不能使用 Pydantic 模型重新序列化。
- 缺失或无效签名返回 `401`，不要返回 `403` 或 `200` 占位成功。

### 配置
- 新配置字段先加到 `Settings`，再同步 `.env.example`，最后更新相关测试或启动说明。
- `DEBUG` 只能影响本地调试行为，不允许改变认证、签名、权限等安全规则。

## 测试与验证机制

### 提交前检查清单
- [ ] **依赖同步**：`uv sync --extra dev`
- [ ] **测试**：`uv run pytest`
- [ ] **Lint**：`uv run ruff check .`
- [ ] **类型检查**：`uv run mypy app`
- [ ] **接口契约**：新增或变更 `/api/v1` 接口时，确认 `response_model`、schema、测试同步更新。
- [ ] **配置同步**：新增配置时，确认 `app/core/config.py` 与 `.env.example` 一致。

### 代码审查关注点

**架构层面**
- 路由是否只做编排，业务逻辑是否进入 service？
- 新领域是否有清晰 schema、service、测试边界？
- 是否引入了当前项目没有的第二套框架或数据访问方式？

**数据层面**
- 新模型是否继承 `Base` 并从 `app/models/__init__.py` 导出？
- 查询是否使用 `AsyncSession`，是否避免了业务层 raw SQL 拼接？
- 时间字段是否 timezone-aware？

**安全层面**
- 响应和日志是否避免泄露密码哈希、token、secret？
- 认证接口是否区分 access / refresh token？
- webhook 或外部输入是否保留了签名校验和 Pydantic 校验？

**测试层面**
- API 成功路径和失败路径是否都有测试？
- 测试是否通过 FastAPI dependency override 使用测试数据库？
- 需要 Redis / PostgreSQL 真实依赖的测试是否明确标记或隔离？

## 公共工具与约定

- **配置入口**：统一使用 `app/core/config.py` 的 `settings` 或 `get_settings()`；不要在模块内直接解析环境变量。
- **数据库会话**：统一使用 `app/database.py` 的 `get_db` 和 `AsyncSessionLocal`。
- **认证依赖**：统一使用 `app/dependencies.py` 的 `get_current_user` / `get_current_active_user`。
- **密码与 JWT**：统一使用 `app/core/security.py`，禁止在路由或服务中重复实现加密逻辑。
- **建表辅助**：`scripts/create_tables.py` 只用于早期本地开发；生产迁移方案落地后应改用 Alembic。

## 已知后续事项

- 建立 Alembic 迁移目录，并定义本地、测试、部署环境的迁移命令。
- 为 Article、Source、Feed、IngestJob 等内容域增加模型、schema、service 和测试后，再实现真实 ingestion。
- 为 refresh token 增加持久化、撤销和轮换策略；当前 refresh token 仍是无状态 JWT。
- 建立结构化日志和 request id；当前项目尚未形成统一日志模块，不要在文档中假设已有 logger。
- 为 Redis 之外的外部依赖（Qdrant、OpenAI）落地真实健康检查和超时策略。

## 本文档的维护规则

- AGENTS.md 中的每条规则必须能回答“违反它会导致什么具体后果”；无法回答的规则应删除。
- 能被 lint、CI、类型检查自动强制的规则不重复写入，除非需要解释项目级原因。
- 发现文档与代码不一致时，以代码为准，并更新文档。
- 新增公共组件、工具、目录或跨模块约定时，评估是否需要同步更新本文档。
- 不维护完整版本号和完整文件清单；这些内容以 `pyproject.toml`、`uv.lock`、`rg --files backend` 的当前结果为准。

<!-- last-verified: 2026-05-27 -->
