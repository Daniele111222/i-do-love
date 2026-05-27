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
- **必须**把业务流程放在 `app/services/`；路由只做依赖注入、签名/限流等入口校验、调用服务、映射 HTTP 状态码。
- **必须**用 `app.services.exceptions` 中的 typed exception 表示可预期业务错误；否则路由无法稳定转换为 4xx。
- **禁止**在路由里散落密码哈希、JWT 生成、数据库编排；这些逻辑当前集中在 `AuthService`。

### 3. 运行时状态要真实
- **必须**让依赖健康检查执行真实探测；`/health/db` 已执行 `SELECT 1`，`/health/redis` 已执行 Redis `ping`。
- **禁止**在依赖不可用时仍返回 `"healthy"`；这会让 Docker healthcheck、部署探针和排障结果失真。
- **必须**让 `/readyz` 聚合关键依赖状态；必需依赖失败返回 `503`，可选依赖未配置时返回 `skipped`。
- **必须**让 webhook 签名基于原始 request body 校验；重序列化后的 JSON 会改变 HMAC 输入。
- **必须**保留 `X-Request-ID` 响应头和统一错误 envelope；否则日志、客户端错误定位和跨服务排障会断链。
- **必须**在生产环境使用 JSON 日志格式；否则日志采集、检索和告警无法稳定解析结构化字段。

### 4. 小步演进，少写会腐烂的规则
- **必须**以当前代码为准写约定；不存在的 repository 层、迁移目录、队列任务不得写成已建立规范。
- **优先**记录边界、约束、验证命令，不维护完整文件清单；文件列表随 PR 演进很快过期。
- **必须**在新增跨模块公共规则时同步评估本文档；否则后续 AI 会继续按旧边界改代码。

## 项目背景与最高优先级原则

### 项目现状
- 后端是 AI News Hub 的 FastAPI 服务，当前覆盖认证、健康检查和 webhook 内容入库基础能力。
- 数据层使用 SQLAlchemy 2.0 async ORM，生产默认指向 PostgreSQL，测试使用内存 SQLite。
- Redis 已用于健康检查连接验证，Qdrant / OpenAI / RAG 能力仍处于后续阶段，不能写成已落地业务。
- Alembic 迁移体系已建立；`scripts/create_tables.py` 只保留为早期本地辅助，不代表生产迁移方案。

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
- **必须**持久化 refresh token session，并在刷新时撤销旧 token；无状态 refresh token 无法下线、无法审计、无法阻止重放。
- **必须**让 access token 携带当前 refresh session 的 `sid`，用于识别当前会话；禁止通过 URL 或日志传递 refresh token 明文。
- **必须**保留会话列表与批量撤销能力；账号异常时用户必须能一次性下线所有 refresh token session。
- **必须**为 refresh token session 保存 IP 和 User-Agent；账号安全审计需要知道会话来源。
- **必须**对登录和 refresh token 接口执行 Redis-backed 限流；暴力破解和 token 重放必须在进入业务逻辑前被挡住。
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
- **必须**让 `APP_ENV=production` 拒绝默认 `SECRET_KEY` 和 `WEBHOOK_SECRET`；默认密钥进入生产会让 token 和 webhook 校验失去意义。

#### 6. 文档同步规则
- **必须**在新增公共目录、跨模块服务、认证规则、数据库迁移机制、队列/RAG 基础设施后检查是否需要更新本文档。
- **禁止**把计划中的 Phase 能力写成当前事实；Qdrant、OpenAI、RAG 目前只能描述为预留或后续阶段，基础 webhook 入库除外。
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
| 运行时基础设施 | request id + request log + error envelope + readiness | 请求追踪、请求日志、稳定错误契约与部署探针 |

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
│   ├── db_init.py     # 早期开发用建表辅助，生产迁移使用 Alembic
│   └── main.py        # FastAPI app 与中间件注册
├── alembic/           # 数据库迁移环境与版本脚本
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
- webhook ingestion 必须通过 `IngestService` 持久化，不允许在路由里直接拼装 ORM 写库。

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
- ingestion schema 放在 `app/schemas/ingest.py`；不要继续在 `app/api/v1/ingest.py` 内定义请求/响应模型。
- ORM 到响应模型转换使用 `ConfigDict(from_attributes=True)` 和 `model_validate`。
- 响应 schema 禁止包含 `hashed_password`、secret、内部 token payload。
- `CurrentUser` 只保存请求上下文需要的最小字段；需要完整用户资料时通过服务重新查库。

## 数据库与迁移

### 当前数据库规则
- 生产默认数据库 URL 为 PostgreSQL asyncpg；测试通过 `tests/conftest.py` 覆盖为内存 SQLite。
- 新模型必须兼容 PostgreSQL 和当前测试 SQLite；若使用 PostgreSQL 专有类型，测试层需同步调整。
- `app/database.py` 是唯一 session factory 来源；不要在业务模块创建第二个 engine。
- `pool_pre_ping=True` 已用于生产 engine；不要移除，否则长期连接断开时更难定位。

### 迁移规范
- 生产语义的 schema 变更必须通过 Alembic 迁移，不要依赖 `Base.metadata.create_all`。
- 迁移环境入口是 `alembic.ini` 和 `alembic/env.py`，版本脚本放在 `alembic/versions/`。
- 新增模型后必须同时新增迁移脚本，并用迁移测试证明 `alembic upgrade head` 可执行。

## 安全与外部输入

### JWT 与密码
- 密码哈希统一使用 `app/core/security.py` 的 `get_password_hash` 和 `verify_password`。
- JWT 创建统一使用 `create_access_token` / `create_refresh_token`，解码统一使用 `decode_token`。
- token subject 当前按 `str(user.id)` 写入，并在服务中转回 `int`；改主键类型时必须同步 token、schema、测试。
- refresh token 必须带 `jti`，并在 `refresh_token_sessions` 表中保存 SHA-256 hash；禁止保存明文 refresh token。
- access token 必须带 `sid` 指向当前 refresh token session 的 `jti`；会话列表依赖它标识 `is_current`。
- refresh token 只能使用一次；刷新成功后旧 session 必须写入 `revoked_at`，并返回新的 refresh token。
- `/api/v1/auth/logout` 必须撤销传入的 refresh token session；登出后该 token 不得再换取新凭据。
- `/api/v1/auth/sessions` 只能返回 `id`、时间字段和状态字段；禁止返回 `token_id`、`token_hash` 或 token 明文。
- `/api/v1/auth/sessions` 可以返回 `ip_address` 和 `user_agent`；这两个字段用于用户识别异常会话，不得包含 token、secret 或完整请求头。
- `DELETE /api/v1/auth/sessions` 必须撤销当前用户的全部未撤销 refresh token session。
- 认证关键事件必须写入 `app.audit` logger；至少覆盖注册成功、登录成功/失败、刷新成功、登出和批量撤销，且日志 extra 禁止包含原始 token、密码或 secret。
- `/api/v1/auth/login` 和 `/api/v1/auth/refresh` 必须先执行限流再调用 `AuthService`；被限流时返回 `429` 和 `Retry-After`。
- 限流器使用 Redis 固定窗口计数；Redis 不可用时必须 fail-closed，并写入 `app.audit` 的 `rate_limit_unavailable` 事件。

### Webhook
- `POST /api/v1/ingest/webhook` 必须校验 `X-Signature`。
- 签名格式为 `sha256=<hexdigest>`，算法为 HMAC-SHA256。
- 校验输入必须是 `await request.body()` 得到的原始字节；不能使用 Pydantic 模型重新序列化。
- 缺失或无效签名返回 `401`，不要返回 `403` 或 `200` 占位成功。
- 校验通过后必须调用 `IngestService.ingest_webhook()` 写入 `sources`、`articles`、`ingest_jobs`。
- `source_url` 存在时必须作为文章幂等键；重复 webhook 更新同一篇文章，而不是插入重复数据。
- `ingest_jobs.status` 当前使用 `"success"` 记录成功接收；后续异步解析失败必须写入失败 job 和 `error_message`。
- `POST /api/v1/ingest/feed` 必须创建持久化 `pending` job；禁止只返回内存占位响应。
- `GET /api/v1/ingest/status` 必须基于 `ingest_jobs` 数据库统计；禁止返回硬编码 0。

### 配置
- 新配置字段先加到 `Settings`，再同步 `.env.example`，最后更新相关测试或启动说明。
- `DEBUG` 只能影响本地调试行为，不允许改变认证、签名、权限等安全规则。
- `APP_ENV` 当前支持 `development`、`test`、`staging`、`production`；生产环境必须使用非默认密钥。
- `LOG_LEVEL` 控制 root logger 级别；生产默认推荐 `INFO`，不要通过代码硬编码环境差异。
- `QDRANT_URL` 和 `OPENAI_API_KEY` 当前属于 Phase 3+ 可选依赖；未配置时 readiness 必须标记为 `skipped`，不要阻止基础 API 发布。
- `AUTH_LOGIN_RATE_LIMIT`、`AUTH_REFRESH_RATE_LIMIT`、`AUTH_RATE_LIMIT_WINDOW_SECONDS` 控制认证限流；变更默认值必须同步风险评估和测试。

### 错误响应与请求追踪
- 所有 HTTP 错误必须返回 `{"error": {"code", "message", "request_id"}}` envelope。
- 需要结构化排障信息的错误可使用 `error.details`；普通错误不得额外返回 `details: null`，避免破坏既有响应契约。
- `X-Request-ID` 入站存在时必须原样透传；不存在时由中间件生成并写入响应头。
- 每个请求完成时必须通过 `app.request` logger 输出 `request_completed`，并带上 `request_id`、`method`、`path`、`status_code`、`duration_ms`。
- 新增全局异常处理时，不要绕过 `app/core/errors.py`；否则客户端会收到不一致的错误结构。
- `APP_ENV=production` 时必须使用 `JsonLogFormatter` 输出单行 JSON；字段至少包含 `timestamp`、`level`、`logger`、`message`，并保留 `extra` 中的结构化字段。

### 健康检查与部署探针
- `/api/v1/health` 只表示 API 进程可响应，不代表服务可接流量。
- `/api/v1/health/db` 和 `/api/v1/health/redis` 是单项依赖探测，失败必须返回 `503`。
- `/api/v1/readyz` 是部署就绪探针，必须聚合 database、redis、qdrant、openai 的状态。
- database 和 redis 是必需依赖；任何一个 `unavailable` 都必须让 `/readyz` 返回 `503`。
- qdrant 和 openai 在 RAG 未落地前是可选依赖；未配置返回 `skipped`，配置后执行轻量检查或配置检查。

## 测试与验证机制

### 提交前检查清单
- [ ] **依赖同步**：`uv sync --extra dev`
- [ ] **测试**：`uv run pytest`
- [ ] **Lint**：`uv run ruff check .`
- [ ] **类型检查**：`uv run mypy app`
- [ ] **接口契约**：新增或变更 `/api/v1` 接口时，确认 `response_model`、schema、测试同步更新。
- [ ] **配置同步**：新增配置时，确认 `app/core/config.py` 与 `.env.example` 一致。
- [ ] **错误契约**：确认新增错误路径仍返回统一 error envelope 和 `X-Request-ID`。
- [ ] **请求日志**：确认新增中间件或异常路径不会丢失 `app.request` 请求完成日志。
- [ ] **日志格式**：确认生产日志仍为单行 JSON，并保留 request/audit extra 字段。
- [ ] **部署探针**：确认新增外部依赖后同步 `/api/v1/readyz`，并区分 required / optional。
- [ ] **认证限流**：确认登录和 refresh token 仍先经过 Redis-backed rate limiter，并覆盖 `429` / `Retry-After` 测试。
- [ ] **会话审计**：确认 refresh token session 创建时写入 IP/User-Agent，且会话列表不暴露 `token_id`、`token_hash`、refresh token 明文。

### 代码审查关注点

**架构层面**
- 路由是否只做编排，业务逻辑是否进入 service？
- 新领域是否有清晰 schema、service、测试边界？
- 是否引入了当前项目没有的第二套框架或数据访问方式？

**数据层面**
- 新模型是否继承 `Base` 并从 `app/models/__init__.py` 导出？
- 查询是否使用 `AsyncSession`，是否避免了业务层 raw SQL 拼接？
- 时间字段是否 timezone-aware？
- ingestion 新表是否有 Alembic 迁移，并通过迁移测试验证 `alembic upgrade head`？

**安全层面**
- 响应和日志是否避免泄露密码哈希、token、secret？
- 认证接口是否区分 access / refresh token？
- webhook 或外部输入是否保留了签名校验和 Pydantic 校验？
- 生产环境是否拒绝默认密钥？

**测试层面**
- API 成功路径和失败路径是否都有测试？
- 测试是否通过 FastAPI dependency override 使用测试数据库？
- 需要 Redis / PostgreSQL 真实依赖的测试是否明确标记或隔离？

## 公共工具与约定

- **配置入口**：统一使用 `app/core/config.py` 的 `settings` 或 `get_settings()`；不要在模块内直接解析环境变量。
- **错误响应**：统一使用 `app/core/errors.py` 的异常处理器；不要在局部路由自定义另一套错误 envelope。
- **请求追踪与日志**：统一使用 `app/core/middleware.py` 和 `app/core/logging.py`；不要在业务层手动生成独立请求 ID。
- **日志配置**：统一使用 `app.core.logging.configure_logging()`；不要在业务模块重复设置 root handler。
- **审计日志**：认证与账号安全事件统一使用 `app.core.logging.audit_logger`；事件名保持稳定，便于后续接入 SIEM 或日志告警。
- **限流服务**：统一使用 `app/services/rate_limit_service.py`；不要在路由里直接操作 Redis 计数。
- **数据库会话**：统一使用 `app/database.py` 的 `get_db` 和 `AsyncSessionLocal`。
- **认证依赖**：统一使用 `app/dependencies.py` 的 `get_current_user` / `get_current_active_user`。
- **密码与 JWT**：统一使用 `app/core/security.py`，禁止在路由或服务中重复实现加密逻辑。
- **Refresh token session**：统一使用 `app/models/refresh_token_session.py`；新增认证会话能力必须同步迁移和测试。
- **Ingestion**：统一使用 `app/services/ingest_service.py` 和 `app/schemas/ingest.py`；Source/Article/IngestJob 模型必须通过 Alembic 迁移演进。
- **建表辅助**：`scripts/create_tables.py` 只用于早期本地开发；生产迁移方案落地后应改用 Alembic。

## 已知后续事项

- 建立 Alembic 迁移目录，并定义本地、测试、部署环境的迁移命令。
- 为 feed ingestion 增加真实解析 worker 和失败重试；当前 feed 请求已支持 Source/IngestJob 持久化 pending 队列记录，webhook 已支持 Article 入库和 `source_url` 幂等写入。
- 为 refresh token session 增加设备指纹和审计查询；当前已支持持久化、轮换、单 token 登出撤销、会话列表、批量撤销、IP 和 User-Agent。
- 将 `app.request` 与 `app.audit` 接入实际部署环境的日志采集和告警；当前已建立 logger、结构化 extra 字段和生产 JSON formatter。
- 为 OpenAI 落地真实轻量健康检查和超时策略；当前 readiness 只确认 key 已配置，避免测试或健康探针产生付费调用。
- 为限流策略补充更细粒度的账号/IP 组合策略、灰名单或验证码联动；当前已覆盖登录和 refresh token 的固定窗口基础限流。

## 本文档的维护规则

- AGENTS.md 中的每条规则必须能回答“违反它会导致什么具体后果”；无法回答的规则应删除。
- 能被 lint、CI、类型检查自动强制的规则不重复写入，除非需要解释项目级原因。
- 发现文档与代码不一致时，以代码为准，并更新文档。
- 新增公共组件、工具、目录或跨模块约定时，评估是否需要同步更新本文档。
- 不维护完整版本号和完整文件清单；这些内容以 `pyproject.toml`、`uv.lock`、`rg --files backend` 的当前结果为准。

<!-- last-verified: 2026-05-27 -->
