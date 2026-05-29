# 已开发功能清单

**日期:** 2026-05-29  
**范围:** 全项目（frontend / backend / codex_check / infra）

---

## 一、前端 (frontend/)

### 1.1 工程骨架
- [x] React 19 + Vite + TypeScript 严格模式
- [x] Tailwind CSS 4 样式系统
- [x] shadcn/ui 基础组件体系（Button、Badge、Card、Input、Tabs）
- [x] React Router v7 路由框架
- [x] 路径别名 `@/` → `src/`
- [x] vitest + @testing-library 测试环境
- [x] ESLint + eslint-plugin-react 代码规范

### 1.2 布局组件
- [x] `Layout` — Header + `<Outlet />` + Footer 三栏布局壳
- [x] `Header` — 顶部导航栏（Logo + 标题 + 状态标记）
- [x] `AppErrorBoundary` — React 错误边界，捕获异常后展示刷新按钮

### 1.3 服务层
- [x] `httpClient` — 通用 fetch 封装，支持 GET/POST/PUT/PATCH/DELETE
- [x] 统一错误处理（`HttpError` 类）
- [x] `credentials: 'include'` 跨域凭据
- [x] `204 No Content` 和 JSON/text 响应智能解析

### 1.4 页面
- [x] **首页 `/`** — 架构骨架展示页，3 张卡片描述前端分层设计

---

## 二、后端 (backend/)

### 2.1 应用入口与基础架构
- [x] FastAPI 应用实例（`app/main.py`）
- [x] API 版本化（`/api/v1` 前缀）
- [x] CORS 中间件，支持配置允许源
- [x] Request ID 中间件（入站透传 + 自动生成 + 响应头回传）
- [x] 结构化错误响应信封（`ErrorDetail` / `ErrorResponse`）
- [x] HTTPException、ValidationError、通用异常的统一处理
- [x] 异步数据库引擎 + session factory（SQLAlchemy 2.0 async）
- [x] `get_db` 依赖注入（FastAPI `Depends`）

### 2.2 配置与环境安全
- [x] `Settings` 类通过环境变量 / `.env` 文件加载（Pydantic Settings）
- [x] `APP_ENV` 区分 development/test/staging/production
- [x] 生产环境拒绝默认 `SECRET_KEY` 和 `WEBHOOK_SECRET`（fail-fast）
- [x] `.env.example` 与配置项同步

### 2.3 日志系统
- [x] `app.request` 请求日志（method / path / status_code / duration_ms / request_id）
- [x] `app.audit` 认证审计日志（注册/登录/刷新/登出/会话吊销）
- [x] `app.worker` 后台任务日志
- [x] 生产环境 JSON formatter（单行结构化日志）
- [x] 开发环境可读文本格式

### 2.4 认证系统
- [x] 用户注册（POST `/auth/register`）
- [x] 邮箱+密码登录（POST `/auth/login`）
- [x] JWT access token（15 分钟过期）+ refresh token（7 天过期）
- [x] Refresh token rotation（刷新时旧 token 吊销，不可重放）
- [x] Refresh token 持久化（数据库存 SHA-256 hash，不存明文）
- [x] 登出吊销（POST `/auth/logout`）
- [x] 会话列表查看（GET `/auth/sessions`）
- [x] 全会话吊销（DELETE `/auth/sessions`，踢出所有设备）
- [x] 当前用户信息查询（GET `/auth/me`）
- [x] 会话记录 IP 和 User-Agent
- [x] Access token 携带当前会话 sid
- [x] 密码 bcrypt 哈希
- [x] OAuth2PasswordBearer 依赖注入

### 2.5 限流
- [x] Redis-backed fixed-window 限流
- [x] 登录接口限流（默认 10 次/60s）
- [x] Refresh token 接口限流（默认 30 次/60s）
- [x] 被限流时返回 `429` + `Retry-After` 头
- [x] Redis 不可用时 fail-closed（不暴露认证接口）

### 2.6 健康检查与就绪探针
- [x] 进程存活检查（GET `/health`）
- [x] 数据库连通性检查（GET `/health/db`）
- [x] Redis 连通性检查（GET `/health/redis`）
- [x] K8s 就绪探针（GET `/readyz`）
- [x] 聚合依赖：database（required）、redis（required）、qdrant（optional）、openai（optional）
- [x] `503` + `error.details` 结构化诊断

### 2.7 内容接入 (Ingestion)
- [x] Webhook 接收（POST `/ingest/webhook`）
- [x] HMAC-SHA256 签名校验
- [x] webhook 内容幂等 upsert（按 `source_url`）
- [x] Feed 入队（POST `/ingest/feed`）
- [x] RSS / Atom 解析
- [x] Feed 抓取（`httpx.AsyncClient`）
- [x] Feed 文章幂等 upsert
- [x] 接入统计（GET `/ingest/status`）
- [x] Worker 队列状态（GET `/ingest/queue`）
- [x] 任务重试机制（`attempt_count` / `next_retry_at` / `retrying` → `failed` 最大 3 次）
- [x] 任务认领（claim）+ 锁机制（`processing` + `locked_at`）
- [x] Stale lock 恢复（超时 processing 任务可重新领取）
- [x] PostgreSQL `FOR UPDATE SKIP LOCKED`（多 worker 不重复领取）
- [x] 单批次 worker CLI 入口（`scripts/run_feed_worker.py`）
- [x] Worker batch 日志（claimed / succeeded / failed / processed_items）

### 2.8 数据模型（5 张表）
- [x] `users` — 用户账号
- [x] `refresh_token_sessions` — Refresh token 会话持久化
- [x] `articles` — 已接入文章
- [x] `sources` — 内容来源（Feed / Webhook）
- [x] `ingest_jobs` — 抓取任务（含状态机、重试、锁）

### 2.9 数据库迁移
- [x] Alembic 迁移环境
- [x] 5 个迁移文件覆盖所有模型
- [x] 迁移测试（自动验证 `alembic upgrade head`）

### 2.10 测试覆盖（12 个文件，52 passed / 1 skipped）
- [x] 配置安全检查（`test_config.py`）
- [x] 认证流程（`test_auth.py`）
- [x] 错误处理与 Request ID（`test_error_handling.py`）
- [x] 健康检查 / Readiness（`test_health.py`、`test_readiness.py`）
- [x] 内容接入（`test_ingest.py`）
- [x] 日志格式化（`test_logging.py`）
- [x] 可观测性（`test_observability.py`）
- [x] 数据库迁移（`test_migrations.py`）
- [x] 限流（`test_rate_limit.py`）
- [x] Feed Worker 脚本（`test_feed_worker_script.py`）
- [x] PostgreSQL Worker Claim 集成测试（`test_postgres_worker_claims.py`）

### 2.11 静态类型检查
- [x] mypy strict 模式覆盖 `app/`、`scripts/`、关键测试文件
- [x] Ruff 代码规范检查

---

## 三、codex_check 工具

### 3.1 功能
- [x] CLI 入口（`__main__.py`）
- [x] 项目 `--project` 模式导出 Codex 会话
- [x] `--all` 全量导出
- [x] 会话导入
- [x] 导入前自动备份
- [x] 按 thread id 冲突检测（跳过 hash 相同、标记 hash 不同）
- [x] manifest.json 校验
- [x] session_index.jsonl 去重合并
- [x] .codex-global-state.json 白名单字段补丁
- [x] 同步盘 push/pull/status
- [x] rollback 恢复到导入前状态
- [x] 排除 auth.json、SQLite 等敏感/运行时文件
- [x] 导入报告生成
- [x] 单元测试 + 集成测试

### 3.2 工程化
- [x] pyproject.toml 打包配置
- [x] Windows 运行脚本（`.cmd` + `.ps1`）
- [x] USAGE.html / USAGE.md 使用文档

---

## 四、基础设施

- [x] Docker Compose（PostgreSQL + Redis + Qdrant）
- [x] Git ignore 配置
- [x] AGENTS.md 项目知识库（部分内容已过时）
- [x] 后端架构优化报告
- [x] Codex 会话同步设计文档
