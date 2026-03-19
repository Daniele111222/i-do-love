# AI News Hub 系统设计详述

> 最后更新：2026-03-19
> 版本：v1.0.0

---

## 1. 系统概述

### 1.1 项目背景

AI News Hub 是一个 AI 资讯聚合与消息收录平台，支持 OpenClaw 等 AI 智能体集成，提供丰富的交互体验。

### 1.2 设计目标

| 目标 | 描述 |
|------|------|
| **可扩展性** | 支持未来 AI 功能扩展和用户增长 |
| **可维护性** | 代码清晰，模块解耦，易于维护 |
| **性能** | 前端 60fps，后端 99.9% 可用性 |
| **安全性** | 端到端安全，用户数据保护 |
| **开发者体验** | 良好的开发、测试、部署流程 |

---

## 2. 系统架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         客户端层                                 │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              React + TypeScript (SPA)                    │    │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │    │
│  │  │Router   │ │Zustand  │ │ R3F     │ │Axios    │       │    │
│  │  │         │ │State    │ │3D动画   │ │API调用  │       │    │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘       │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         网关层                                   │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Nginx     │  │   WAF       │  │   CDN       │              │
│  │  反向代理   │  │  Web应用    │  │  静态资源   │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         应用层                                   │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              FastAPI (Python)                            │    │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │    │
│  │  │APIRouter │ │Auth    │ │CRUD     │ │Ingest   │       │    │
│  │  │v1       │ │JWT     │ │Service  │ │Service  │       │    │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘       │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   PostgreSQL    │ │     Redis       │ │    Qdrant       │
│   主数据库      │ │   缓存/会话     │ │   向量存储      │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

### 2.2 前端架构

#### 技术栈

| 类别 | 技术 | 版本 | 用途 |
|------|------|------|------|
| 框架 | React | 18.x | UI 框架 |
| 语言 | TypeScript | 5.x | 类型安全 |
| 构建 | Vite | 5.x | 快速构建 |
| 路由 | React Router | 6.x | 页面路由 |
| 状态 | Zustand | 4.x | 轻量状态 |
| 3D | React Three Fiber | 8.x | 3D 渲染 |
| 动画 | Framer Motion | 11.x | 2D 动画 |
| 样式 | Tailwind CSS | 3.x | 原子化 CSS |
| HTTP | Axios | 1.x | API 调用 |
| 表单 | React Hook Form | 7.x | 表单管理 |
| 测试 | Vitest + RTL | 1.x | 单元测试 |

#### 目录结构

```
frontend/
├── public/                     # 静态资源
│   ├── favicon.ico
│   └── robots.txt
├── src/
│   ├── assets/                 # 图片、字体等
│   │   ├── images/
│   │   └── fonts/
│   ├── components/             # 公共组件
│   │   ├── common/             # 通用组件
│   │   │   ├── Button/
│   │   │   ├── Input/
│   │   │   └── Card/
│   │   ├── layout/             # 布局组件
│   │   │   ├── Header/
│   │   │   ├── Footer/
│   │   │   └── Sidebar/
│   │   └── AuthBall/           # 3D 球体组件 ⭐
│   │       ├── AuthBall.tsx     # 主组件
│   │       ├── Eye.tsx         # 眼球组件
│   │       ├── Hand.tsx        # 手部组件
│   │       └── expressions.ts  # 表情状态
│   ├── pages/                  # 页面组件
│   │   ├── Home/
│   │   ├── Login/
│   │   ├── Register/
│   │   ├── ArticleDetail/
│   │   └── Admin/
│   ├── hooks/                  # 自定义 Hooks
│   │   ├── useAuth.ts
│   │   ├── useArticles.ts
│   │   └── useMousePosition.ts
│   ├── stores/                 # Zustand Stores
│   │   ├── authStore.ts
│   │   ├── articleStore.ts
│   │   └── uiStore.ts
│   ├── services/               # API 服务层
│   │   ├── api.ts             # Axios 实例
│   │   ├── authService.ts
│   │   └── articleService.ts
│   ├── utils/                 # 工具函数
│   │   ├── formatDate.ts
│   │   └── validation.ts
│   ├── types/                  # TypeScript 类型
│   │   ├── api.ts
│   │   ├── article.ts
│   │   └── user.ts
│   ├── styles/                 # 全局样式
│   │   ├── globals.css
│   │   └── variables.css
│   ├── App.tsx                 # 根组件
│   └── main.tsx                # 入口文件
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

#### 状态管理设计

```typescript
// Zustand Store 示例
interface AuthStore {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  
  // Actions
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}

const useAuthStore = create<AuthStore>((set, get) => ({
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: !!localStorage.getItem('token'),
  
  login: async (email, password) => {
    const response = await authService.login(email, password);
    set({ 
      user: response.user, 
      token: response.token,
      isAuthenticated: true 
    });
    localStorage.setItem('token', response.token);
  },
  
  logout: () => {
    set({ user: null, token: null, isAuthenticated: false });
    localStorage.removeItem('token');
  },
}));
```

### 2.3 后端架构

#### 技术栈

| 类别 | 技术 | 版本 | 用途 |
|------|------|------|------|
| 框架 | FastAPI | 0.109+ | Web 框架 |
| 语言 | Python | 3.11+ | 后端语言 |
| ORM | SQLAlchemy | 2.0+ | 数据库 ORM |
| 验证 | Pydantic | 2.x | 数据验证 |
| 认证 | python-jose | 3.3+ | JWT 处理 |
| 密码 | bcrypt | 4.1+ | 密码哈希 |
| 缓存 | Redis | 7.x | 缓存/会话 |
| 数据库 | PostgreSQL | 16.x | 主数据库 |
| 向量 | Qdrant | 1.7+ | 向量存储 |
| 任务 | Celery | 5.x | 异步任务 |
| 测试 | pytest | 8.x | 单元测试 |

#### 目录结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用入口
│   ├── config.py               # 配置管理
│   ├── database.py             # 数据库连接
│   ├── dependencies.py         # 依赖注入
│   ├── api/                   # API 路由
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py       # 路由汇总
│   │       ├── auth.py         # 认证接口
│   │       ├── users.py        # 用户接口
│   │       ├── articles.py     # 资讯接口
│   │       └── ingest.py       # 接入接口
│   ├── core/                   # 核心模块
│   │   ├── __init__.py
│   │   ├── security.py         # 安全工具
│   │   └── config.py           # 配置
│   ├── models/                 # SQLAlchemy 模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── article.py
│   │   └── ingest.py
│   ├── schemas/               # Pydantic 模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── article.py
│   │   └── ingest.py
│   └── services/               # 业务逻辑
│       ├── __init__.py
│       ├── auth_service.py
│       ├── article_service.py
│       └── ingest_service.py
├── tests/                     # 测试
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   └── test_articles.py
├── alembic/                   # 数据库迁移
│   ├── env.py
│   └── versions/
├── pyproject.toml
├── Dockerfile
└── docker-compose.yml
```

#### API 分层设计

```
┌─────────────────────────────────────────────────────────────────┐
│                     API 请求处理流程                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  HTTP Request                                                   │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────┐                                                    │
│  │ Middleware │  (CORS, 日志, 错误处理)                          │
│  └────┬────┘                                                    │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────┐                                                    │
│  │ Router   │  (@router.post("/login"))                         │
│  └────┬────┘                                                    │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────┐                                                    │
│  │ Schema  │  请求体验证 (Pydantic)                              │
│  │ Validate│                                                    │
│  └────┬────┘                                                    │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────┐                                                    │
│  │Service  │  业务逻辑处理                                       │
│  └────┬────┘                                                    │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────┐                                                    │
│  │ Model   │  数据库操作 (SQLAlchemy)                            │
│  └────┬────┘                                                    │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────┐                                                    │
│  │ Response│  响应序列化                                        │
│  └────┬────┘                                                    │
│       │                                                         │
│       ▼                                                         │
│  HTTP Response                                                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. 组件设计

### 3.1 3D 拟人化球体组件

#### 组件结构

```
AuthBall
├── Scene (R3F Canvas)
│   ├── Lights (环境光 + 平行光)
│   ├── Ball (球体网格)
│   │   ├── Body (球体本身)
│   │   ├── Eyes (双眼)
│   │   │   ├── LeftEye
│   │   │   └── RightEye
│   │   ├── Mouth (嘴巴)
│   │   └── Cheeks (脸颊 - 害羞时)
│   ├── Hands (双手)
│   │   ├── LeftHand
│   │   └── RightHand
│   └── Environment (背景)
├── State (表情状态)
│   ├── DEFAULT
│   ├── LOOKING
│   ├── SHYING
│   ├── HAPPY
│   └── SAD
└── Controllers
    ├── MouseController (鼠标跟随)
    └── FocusController (焦点响应)
```

#### 核心逻辑

```typescript
// 眼睛跟随鼠标
function useEyeFollow() {
  const { viewport } = useThree();
  
  useFrame(() => {
    // 将鼠标位置映射到球体坐标系
    const targetX = (mouse.x * viewport.width / 2) * 0.5;
    const targetY = (mouse.y * viewport.height / 2) * 0.3;
    
    // 平滑插值
    eyeRef.current.rotation.x = lerp(eyeRef.current.rotation.x, targetY, 0.1);
    eyeRef.current.rotation.y = lerp(eyeRef.current.rotation.y, targetX, 0.1);
  });
}

// 捂眼动画状态机
type BallState = 'default' | 'looking' | 'shying' | 'happy' | 'sad';

function useBallState() {
  const [state, setState] = useState<BallState>('default');
  
  const handlePasswordFocus = () => setState('shying');
  const handlePasswordBlur = () => setState('default');
  const handleLoginSuccess = () => setState('happy');
  const handleLoginError = () => setState('sad');
  
  return { state, setState, handlePasswordFocus, handlePasswordBlur };
}
```

#### 性能优化

| 优化点 | 策略 |
|--------|------|
| 渲染 | 使用 `invalidate()` 控制渲染帧率 |
| 几何体 | 使用 BufferGeometry，减少顶点 |
| 材质 | 使用 MeshStandardMaterial，共享 |
| 动画 | 使用 `useFrame` 的 deltaTime |
| 卸载 | 不使用时调用 `dispose()` |

### 3.2 资讯管理模块

#### 数据模型

```python
# 文章模型
class Article(Base):
    __tablename__ = "articles"
    
    id: int = Column(Integer, primary_key=True, index=True)
    title: str = Column(String(500), nullable=False)
    summary: str = Column(Text, nullable=True)
    content: str = Column(Text, nullable=False)
    source_url: str = Column(String(1000), nullable=True)
    source_name: str = Column(String(200), nullable=True)
    author: str = Column(String(200), nullable=True)
    published_at: datetime = Column(DateTime, nullable=True)
    
    # 关系
    category_id: int = Column(Integer, ForeignKey("categories.id"))
    category: "Category" = relationship("Category", back_populates="articles")
    tags: List["Tag"] = relationship("Tag", secondary=article_tags, back_populates="articles")
    
    # 元数据
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_published: bool = Column(Boolean, default=True)
```

#### API 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/v1/articles | 获取列表（分页、过滤） |
| GET | /api/v1/articles/{id} | 获取详情 |
| POST | /api/v1/articles | 创建文章 |
| PUT | /api/v1/articles/{id} | 更新文章 |
| DELETE | /api/v1/articles/{id} | 删除文章 |

### 3.3 OpenClaw 接入模块

#### Webhook 处理流程

```python
@router.post("/ingest/webhook")
async def receive_webhook(
    payload: WebhookPayload,
    x_signature: str = Header(None),
):
    # 1. 验证签名
    if not verify_signature(payload, x_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # 2. 解析内容
    article = parse_webhook_payload(payload)
    
    # 3. 存储
    created = await article_service.create(article)
    
    # 4. 返回确认
    return {"status": "accepted", "id": created.id}
```

---

## 4. 数据流设计

### 4.1 用户认证流程

```
┌─────────────────────────────────────────────────────────────────┐
│                    用户认证流程                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  注册流程:                                                       │
│  ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐         │
│  │ 前端   │───▶│ 后端   │───▶│ 密码   │───▶│ 存储   │         │
│  │ 提交   │    │ 验证   │    │ 哈希   │    │ DB     │         │
│  └────────┘    └────────┘    └────────┘    └────────┘         │
│                                                                  │
│  登录流程:                                                       │
│  ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐         │
│  │ 前端   │───▶│ 后端   │───▶│ 验证   │───▶│ 返回   │         │
│  │ 提交   │    │ 查询   │    │ 密码   │    │ Token  │         │
│  └────────┘    └────────┘    └────────┘    └────────┘         │
│                                                                  │
│  Token 刷新:                                                    │
│  ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐         │
│  │ 前端   │───▶│ 后端   │───▶│ 验证   │───▶│ 返回   │         │
│  │ 请求   │    │ Refresh│    │ Refresh│   │ 新Token│         │
│  └────────┘    └────────┘    └────────┘    └────────┘         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 内容接入流程

```
┌─────────────────────────────────────────────────────────────────┐
│                    OpenClaw 内容接入流程                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  OpenClaw                                                    │
│     │                                                         │
│     │ 1. POST /api/v1/ingest/webhook                          │
│     │    Content-Type: application/json                       │
│     │    X-Signature: sha256=xxx                              │
│     │                                                         │
│     ▼                                                         │
│  ┌─────────────────┐                                          │
│  │ 签名验证        │                                          │
│  └────────┬────────┘                                          │
│           │                                                    │
│           ▼                                                    │
│  ┌─────────────────┐                                          │
│  │ Payload 解析   │                                          │
│  │ (title, url,   │                                          │
│  │  content, etc) │                                          │
│  └────────┬────────┘                                          │
│           │                                                    │
│           ▼                                                    │
│  ┌─────────────────┐     ┌─────────────────┐                  │
│  │ 去重检查        │────▶│ URL Hash 比对   │                  │
│  └────────┬────────┘     └─────────────────┘                  │
│           │                                                    │
│           ▼                                                    │
│  ┌─────────────────┐                                          │
│  │ 内容处理        │                                          │
│  │ (Markdown转换,  │                                          │
│  │  摘要提取)      │                                          │
│  └────────┬────────┘                                          │
│           │                                                    │
│           ▼                                                    │
│  ┌─────────────────┐                                          │
│  │ 存储 PostgreSQL │                                          │
│  └────────┬────────┘                                          │
│           │                                                    │
│           ▼                                                    │
│  ┌─────────────────┐                                          │
│  │ 返回确认        │                                          │
│  │ { "id": 123 }   │                                          │
│  └─────────────────┘                                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. 接口设计

### 5.1 统一响应格式

```typescript
// 成功响应
interface SuccessResponse<T> {
  data: T;
  message?: string;
  meta?: {
    page: number;
    page_size: number;
    total: number;
    total_pages: number;
  };
}

// 错误响应
interface ErrorResponse {
  error: {
    code: string;
    message: string;
    details?: Record<string, any>;
  };
}
```

### 5.2 认证接口

```typescript
// POST /api/v1/auth/register
interface RegisterRequest {
  email: string;
  password: string;
  nickname?: string;
}

interface RegisterResponse {
  user: {
    id: number;
    email: string;
    nickname: string;
  };
  access_token: string;
  refresh_token: string;
}

// POST /api/v1/auth/login
interface LoginRequest {
  email: string;
  password: string;
}

interface LoginResponse {
  user: User;
  access_token: string;
  refresh_token: string;
}
```

---

## 6. 非功能性设计

### 6.1 性能目标

| 指标 | 目标值 |
|------|--------|
| 前端首屏加载 | < 2s (3G) |
| 前端帧率 | 60fps |
| API P99 延迟 | < 200ms |
| API 可用性 | 99.9% |
| 数据库查询 | < 50ms |

### 6.2 可靠性设计

- **数据库主从复制**：读写分离
- **Redis 缓存**：热点数据缓存
- **CDN 加速**：静态资源全球分发
- **健康检查**：自动故障检测
- **自动扩缩容**：应对流量峰值

### 6.3 可观测性

| 维度 | 工具 |
|------|------|
| 日志 | ELK Stack |
| 监控 | Prometheus + Grafana |
| 链路追踪 | Jaeger |
| 错误追踪 | Sentry |

---

## 7. 技术选型理由

### 7.1 前端框架

| 选择 | 理由 |
|------|------|
| React | 生态丰富，社区活跃 |
| TypeScript | 类型安全，减少 bug |
| Vite | 极速开发体验 |
| Zustand | 轻量、简洁、无样板代码 |
| R3F | React 风格的 3D 开发 |
| Tailwind | 快速开发，减少 CSS 文件 |

### 7.2 后端框架

| 选择 | 理由 |
|------|------|
| FastAPI | 异步、高性能、自动文档 |
| SQLAlchemy | 成熟 ORM，类型安全 |
| Pydantic | 数据验证，类型提示 |
| PostgreSQL | 关系型数据，功能强大 |
| Redis | 缓存、会话、消息队列 |

---

## 8. 附录

### 8.1 环境变量

```bash
# .env.example
# Backend
DATABASE_URL=postgresql://user:pass@localhost:5432/ai_news
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15

# Frontend
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### 8.2 第三方服务

| 服务 | 用途 | 费用 |
|------|------|------|
| Vercel | 前端部署 | 免费 |
| Railway | 后端部署 | 按需 |
| Supabase | PostgreSQL | 免费/付费 |
| Upstash | Redis | 免费/付费 |
| Qdrant Cloud | 向量数据库 | 免费/付费 |
| OpenAI | LLM/Embedding | 按量 |

---

*本文档将随着系统演进持续更新*
