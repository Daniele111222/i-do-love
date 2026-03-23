# AI News Hub - 项目知识库

**Generated:** 2026-03-23
**Commit:** 0b53dcc
**Branch:** main

## OVERVIEW

AI 资讯聚合平台，前后端分离架构。前端 React 19 + 3D 动画，后端 FastAPI + 向量数据库，支持 RAG。

## STRUCTURE

```
i-do-love/
├── frontend/           # React 19 + Vite + TypeScript
│   ├── src/
│   │   ├── components/AuthBall/  # 3D 动画登录（特色功能）
│   │   ├── components/common/    # 通用组件
│   │   ├── pages/               # 页面
│   │   ├── hooks/               # 自定义 hooks
│   │   ├── services/            # API 服务层
│   │   ├── stores/              # Zustand 状态管理
│   │   └── routes/              # 路由配置
│   └── vitest.config.ts
├── backend/            # Python FastAPI + SQLAlchemy 2.0
│   ├── app/
│   │   ├── api/v1/      # API 路由 (auth, health, ingest)
│   │   ├── core/        # 配置、安全
│   │   ├── models/      # SQLAlchemy 模型
│   │   ├── schemas/     # Pydantic schemas
│   │   └── services/    # 业务逻辑
│   └── tests/           # pytest 测试
├── docker-compose.yml  # PostgreSQL + Redis + Qdrant
└── docs/               # 项目文档
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| 前端 3D 动画 | `frontend/src/components/AuthBall/` | React Three Fiber 实现 |
| 前端路由/状态 | `frontend/src/` | React Router v7 + Zustand |
| 后端 API | `backend/app/api/v1/` | FastAPI 路由 |
| 后端认证 | `backend/app/core/security.py` | JWT 令牌处理 |
| 数据模型 | `backend/app/models/` | SQLAlchemy 模型 |
| 本地服务 | `docker-compose.yml` | PostgreSQL/Redis/Qdrant |

## CODE MAP

| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `app` | FastAPI | `backend/app/main.py:8` | 根应用实例 |
| `api_router` | APIRouter | `backend/app/api/v1/router.py:6` | v1 路由汇总 |
| `get_current_user` | Function | `backend/app/dependencies.py:12` | JWT 认证依赖 |
| `AuthBall` | Component | `frontend/src/components/AuthBall/AuthBall.tsx` | 3D 登录组件 |
| `routes` | Array | `frontend/src/routes/index.tsx` | 前端路由配置 |
| `authStore` | Store | `frontend/src/stores/authStore.ts` | Zustand 状态 |

## CONVENTIONS

**Frontend:**
- TypeScript strict 模式 (`noUnusedLocals`, `noUnusedParameters`)
- 路径别名: `@/*` → `src/*`
- 样式: Tailwind CSS 4
- 测试: Vitest + @testing-library

**Backend:**
- Python 3.11+, 类型注解严格模式 (mypy strict)
- Ruff: line-length 100
- 异步模式: pytest-asyncio
- API 前缀: `/api/v1`

## ANTI-PATTERNS (THIS PROJECT)

- **前端**: 禁止 `any` 类型，使用 `unknown` + 类型守卫
- **后端**: TODO 未完成 (见下文)

## UNIQUE STYLES

- **3D 动画**: AuthBall 组件使用 React Three Fiber 实现眨眼、表情跟随鼠标等复杂动画
- **向量检索**: 后端预留 Qdrant 向量数据库支持，Phase 3+ RAG

## COMMANDS

```bash
# Frontend
cd frontend && npm run dev      # 开发服务器
npm run build                    # 生产构建
npm test                         # Vitest 测试

# Backend
cd backend && uv sync            # 安装依赖
uv run uvicorn app.main:app --reload  # 开发服务器
uv run pytest                    # 运行测试

# Docker (本地服务)
docker-compose up -d            # 启动 PostgreSQL/Redis/Qdrant
```

## NOTES

**后端 TODO (未实现):**
- `backend/app/dependencies.py:37` - 需从数据库检查用户活跃状态
- `backend/app/api/v1/ingest.py` - Feed 解析、内容接收、文章存储未实现
- `backend/app/api/v1/health.py` - 真实数据库/Redis 健康检查未实现
