# 后端架构优化总结与后续规划

**日期**: 2026-05-28  
**范围**: `backend/` FastAPI 后端服务  
**读者**: 产品负责人、后端开发者、运维/部署负责人、技术评审人员

## 1. 总体结论

在不继续推进“设备指纹”和更细粒度风控能力的前提下，当前后端已经达到生产级基础架构水准，可以作为后续业务功能、RAG 能力和运营后台能力的稳定底座。

本轮优化的重点不是重写业务，而是补齐一个后端服务进入生产环境前必须具备的基础能力：配置安全、统一错误契约、请求追踪、结构化日志、认证会话、限流、健康检查、数据库迁移、异步 ingestion 队列、worker 重试与锁机制、测试与静态质量门。

当前仍需要继续完善的内容主要集中在部署和运营层面，例如真实 PostgreSQL 集成测试接入 CI、worker 调度方式落地、日志采集告警规则配置、RAG 业务链路接入等。这些事项不影响当前后端基础架构是否达标，但会影响后续生产运行的可观测性和自动化程度。

## 2. 当前架构概览

后端保持 FastAPI + SQLAlchemy async + Pydantic 的分层架构：

```text
backend/
├── app/
│   ├── api/v1/      # HTTP 路由，按业务域拆分
│   ├── core/        # 配置、安全、错误处理、日志、中间件
│   ├── models/      # SQLAlchemy ORM 模型
│   ├── schemas/     # Pydantic 请求/响应模型
│   ├── services/    # 业务服务、依赖探测、限流、ingestion 编排
│   ├── database.py  # async engine、session factory、get_db
│   └── main.py      # FastAPI app、中间件和异常处理注册
├── alembic/         # 数据库迁移
├── scripts/         # 运维/worker 脚本
└── tests/           # pytest 异步测试
```

目前的架构边界是合理的：

- 路由层主要负责依赖注入、HTTP 状态码映射和入口校验。
- 业务流程集中在 `app/services/`，避免路由承担数据库编排。
- 数据模型和响应模型分离，降低内部字段泄露风险。
- 生产语义的数据结构变更已经通过 Alembic 管理。
- 横切能力集中在 `app/core/`，包括配置、安全、错误响应、请求 ID 和日志。

## 3. 已完成的架构优化

### 3.1 配置与环境安全

已完成：

- 增加 `APP_ENV`，区分 development、test、staging、production。
- 生产环境拒绝默认 `SECRET_KEY` 和 `WEBHOOK_SECRET`，避免默认密钥进入部署环境。
- `.env.example` 与配置项同步，降低本地启动和部署配置漂移。
- Qdrant、OpenAI 等后续能力以可选依赖方式进入 readiness，不阻塞基础 API 发布。

价值：

- 生产环境可以 fail fast，密钥错误会在启动阶段暴露。
- 配置来源集中在 `app/core/config.py`，后续新增环境变量有明确入口。

### 3.2 API 错误契约与请求追踪

已完成：

- 所有 HTTP 错误统一返回：

```json
{
  "error": {
    "code": "unauthorized",
    "message": "Invalid email or password",
    "request_id": "req-xxx"
  }
}
```

- 支持 `X-Request-ID` 入站透传；没有传入时自动生成。
- 错误响应和正常响应都会带回 `X-Request-ID`。
- readiness 这类需要结构化诊断的错误支持 `error.details`。

价值：

- 前端、日志、排障人员可以用同一个 request id 串起问题。
- 客户端不再需要兼容 FastAPI 默认错误格式和业务错误格式两套结构。

### 3.3 日志与审计

已完成：

- 建立 `app.request` 请求日志。
- 建立 `app.audit` 认证审计日志。
- 建立 `app.worker` 后台任务日志。
- 生产环境使用单行 JSON formatter，保留结构化 extra 字段。
- request log 记录 method、path、status_code、duration_ms、request_id。
- worker batch log 记录 claimed、succeeded、failed、processed_items。

价值：

- 日志结构已经适合接入 ELK、Loki、Datadog、CloudWatch 等采集系统。
- 认证事件和 worker 运行状态可以进一步配置告警。

### 3.4 数据库迁移体系

已完成：

- 建立 Alembic 迁移环境。
- 已覆盖 users、refresh token sessions、session metadata、ingestion tables、ingest job retry/lock 字段。
- 测试中验证 `alembic upgrade head` 可执行。

价值：

- 生产数据结构演进不再依赖 `Base.metadata.create_all`。
- 后续新增模型或字段有明确迁移路径。

### 3.5 认证与会话安全

已完成：

- access token / refresh token 区分用途。
- refresh token 增加 `jti`，数据库只保存 SHA-256 hash，不保存明文。
- refresh token session 持久化。
- refresh token 刷新时进行轮换，旧 token 被撤销，不能重复使用。
- access token 携带当前会话 `sid`。
- 支持 logout 撤销当前 refresh token。
- 支持查看当前用户会话列表。
- 支持撤销当前用户全部 refresh token session。
- 会话记录保存 IP 和 User-Agent。
- 关键认证事件写入审计日志，避免记录 token、密码或 secret。

价值：

- 用户异常登录后可以下线全部会话。
- refresh token 重放风险明显降低。
- 后续做账号安全中心、设备管理、异常登录告警时已有数据基础。

### 3.6 认证限流

已完成：

- 登录接口接入 Redis-backed fixed-window 限流。
- refresh token 接口接入 Redis-backed fixed-window 限流。
- 被限流时返回 `429` 和 `Retry-After`。
- Redis 不可用时采用 fail-closed，避免限流系统失效后认证接口裸奔。

价值：

- 对暴力破解、refresh token 重放有基础防护。
- 策略集中在 `app/services/rate_limit_service.py`，后续可演进为账号/IP 组合策略。

### 3.7 健康检查与 readiness

已完成：

- `/api/v1/health` 表示 API 进程可响应。
- `/api/v1/health/db` 执行真实数据库探测。
- `/api/v1/health/redis` 执行真实 Redis ping。
- `/api/v1/readyz` 聚合 database、redis、qdrant、openai。
- database 和 redis 是 required dependency，失败返回 `503`。
- qdrant 和 openai 当前是 optional dependency，未配置时返回 `skipped`。
- OpenAI 配置后使用 `GET {OPENAI_BASE_URL}/models` 做轻量探测。

价值：

- 部署探针可以区分“进程活着”和“服务可接流量”。
- RAG 依赖尚未正式落地时，不会阻塞基础服务发布。

### 3.8 Ingestion 与 Feed Worker

已完成：

- 建立 `Source`、`Article`、`IngestJob` 模型。
- webhook 请求通过签名校验后持久化入库。
- `source_url` 支持幂等 upsert，避免重复文章。
- feed 请求创建持久化 `pending` job。
- `/api/v1/ingest/status` 基于数据库统计。
- `/api/v1/ingest/queue` 暴露 worker backlog 和可领取任务数量。
- RSS/Atom feed worker 已支持解析、文章 upsert、状态落库。
- 失败任务支持 `attempt_count`、`next_retry_at`、retrying、failed。
- worker claim 阶段使用 `processing` 和 `locked_at`。
- stale lock 可恢复。
- PostgreSQL 路径使用 `FOR UPDATE SKIP LOCKED`，避免多 worker 重复领取。
- `scripts/run_feed_worker.py` 是单批次 worker 入口，业务逻辑仍在 service 层。

价值：

- ingestion 已从占位接口升级为可恢复、可观测、可重试的持久化队列。
- 后续只需要在部署层接入调度器，就可以持续消费 feed。

### 3.9 测试与质量门

已完成：

- 覆盖配置、安全、认证、限流、错误响应、日志、健康检查、readiness、migration、ingestion、worker 的测试。
- mypy strict 方向已覆盖 app、scripts 和关键测试文件。
- Ruff 已纳入质量检查。
- PostgreSQL worker claim 有可选集成测试，未配置 `POSTGRES_TEST_DATABASE_URL` 时默认跳过。

最近一次完整验证结果：

```text
uv run pytest
52 passed, 1 skipped

uv run ruff check .
All checks passed

uv run mypy app
Success: no issues found

uv run mypy scripts tests/test_ingest.py tests/test_observability.py tests/test_feed_worker_script.py tests/test_postgres_worker_claims.py
Success: no issues found

git diff --check -- backend docs
通过；仅出现 Git 读取全局 ignore 权限相关 warning，不影响代码内容
```

## 4. 当前判断：是否还需要继续优化架构

从“生产级基础架构”角度看，当前后端架构已经合理，不建议继续做大规模重构。

原因：

- 当前分层边界清晰，路由、service、schema、model、core 的职责没有明显错位。
- 关键横切能力已经集中实现，未散落在业务代码中。
- 数据迁移、错误契约、request id、日志、readiness、限流、会话安全等基础能力已形成闭环。
- ingestion worker 已具备持久化、重试、锁、并发领取和观测基础。
- 测试覆盖已经能保护主要架构约束。

更值得投入的不是继续抽象，而是把当前能力接入真实部署环境、监控体系和业务链路。过早新增 repository 层、消息队列框架、复杂风控模块或 RAG 抽象层，反而会增加维护成本。

## 5. 仍需继续完善的事项

### P0：部署前必须确认

1. 真实 PostgreSQL 集成测试进入 CI

当前已有 `tests/test_postgres_worker_claims.py`，但默认需要 `POSTGRES_TEST_DATABASE_URL` 才会运行。建议在 CI 中启动 PostgreSQL，并执行：

```bash
POSTGRES_TEST_DATABASE_URL="postgresql+asyncpg://..." uv run pytest tests/test_postgres_worker_claims.py -q
```

目的：

- 验证多 worker 并发 claim 在真实 PostgreSQL 上确实不会重复领取。
- 避免只依赖 SQLite 测试推断 PostgreSQL 锁语义。

2. Alembic 迁移流程进入部署脚本

建议部署时明确执行：

```bash
uv run alembic upgrade head
```

目的：

- 确保新版本应用启动前数据库结构已经到位。
- 避免运行时因为缺字段或缺表失败。

3. Worker 调度方式落地

当前已有单批次入口：

```bash
uv run python -m scripts.run_feed_worker --limit 10
```

还需要在部署层选择一种调度方式：

- cron
- 容器定时任务
- 独立 worker 进程
- 云平台 scheduler

建议先采用简单的定时批处理，等吞吐压力明确后再考虑更重的队列系统。

### P1：上线后优先完善

1. 日志采集和告警

应用内已经输出结构化 request、audit、worker 日志，但还需要在部署环境完成采集和告警规则。

建议优先建立：

- 5xx 错误率告警
- 登录失败突增告警
- rate limit unavailable 告警
- worker failed 数量告警
- `/readyz` required dependency unavailable 告警

2. 指标系统

当前日志已经能支撑基础排障。若后续运行频率提高，建议增加 Prometheus/OpenTelemetry 指标：

- HTTP 请求耗时分位数
- 认证成功/失败次数
- rate limit 命中次数
- feed worker 吞吐
- feed job retry/failed 数量
- ingestion queue backlog

3. OpenAPI / 前后端契约检查

建议在 CI 中导出或校验 OpenAPI schema，避免后端响应模型变化后前端未同步。

### P2：业务增长后再做

1. 更细粒度认证风控

当前已具备 refresh session、IP、User-Agent、审计日志、基础限流。设备指纹、灰名单、验证码联动、账号/IP 组合限流可以作为后续安全增强，不属于当前必须完成项。

2. RAG / Qdrant / OpenAI 业务接入

当前 readiness 已为 Qdrant 和 OpenAI 预留探测能力，但业务链路还没有真正进入 RAG 阶段。后续接入时建议新增明确的 service 边界，而不是把向量检索逻辑直接写入路由。

3. 更完整的后台任务平台

如果 feed worker 未来需要更高吞吐、失败补偿、延迟任务、任务优先级，可以评估 Celery、RQ、Arq、Dramatiq 或云原生队列。但当前阶段已有持久化 job 表和 claim lock，不需要为了架构完整性提前引入重型队列。

## 6. 日常维护建议

### 开发检查命令

在 `backend/` 目录执行：

```bash
uv run pytest
uv run ruff check .
uv run mypy app
```

如果修改了 worker 脚本或关键测试类型：

```bash
uv run mypy scripts tests/test_ingest.py tests/test_observability.py tests/test_feed_worker_script.py tests/test_postgres_worker_claims.py
```

如果修改了数据库模型或迁移：

```bash
uv run pytest tests/test_migrations.py -q
```

如果修改了 PostgreSQL worker claim 逻辑：

```bash
POSTGRES_TEST_DATABASE_URL="postgresql+asyncpg://..." uv run pytest tests/test_postgres_worker_claims.py -q
```

### 文档维护方式

- `backend/AGENTS.md` 面向 AI 编程助手，记录强约束、红线和协作规则。
- 本文档面向人类读者，记录架构现状、优化成果、风险和后续路线。
- 新增跨模块基础设施、认证规则、迁移机制、worker 状态机或部署约定后，应同步检查这两份文档是否需要更新。
- 如果文档与代码冲突，以代码为准，并及时修正文档。

## 7. 推荐下一步

短期建议按以下顺序推进：

1. 将 PostgreSQL 集成测试接入 CI。
2. 在部署流程中固定 Alembic upgrade step。
3. 确定 feed worker 调度方案，并记录运行频率、批大小和失败处理方式。
4. 接入日志采集，并为 request、audit、worker 三类日志建立基础告警。
5. 等 RAG 业务明确后，再设计 Qdrant/OpenAI 的业务 service 边界。

这个顺序可以最大化复用当前已经完成的架构基础，同时避免为了未来不确定需求提前引入过重的抽象。
