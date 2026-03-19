# 架构设计文档 - AI News Hub / AI 资讯中心

## 1. 系统架构概览

AI News Hub 采用经典的分层架构设计，整体分为展示层、API 网关层、服务层、数据层四个主要层次。系统遵循"前后端分离"原则，前端使用 React + TypeScript 构建现代化用户界面，后端使用 Python FastAPI 提供高性能 RESTful API 服务。

系统核心设计理念是"Agents First"，即所有功能都考虑到 AI 智能体的访问需求，通过 OpenClaw 等标准协议实现机器友好的接口设计。同时，系统预留了向量数据库和 RAG 能力扩展槽位，为未来的智能问答和 Agent 编排功能奠定基础。

## 2. 架构图

```mermaid
graph TB
    subgraph 客户端层
        A1[Web 浏览器]
        A2[AI 智能体/OpenClaw]
    end

    subgraph 展示层
        B1[React SPA]
        B2[Three.js 3D 场景]
    end

    subgraph API 网关层
        C1[Traefik/Nginx]
        C2[API 路由]
        C3[OpenClaw 协议适配器]
    end

    subgraph 服务层
        D1[FastAPI 应用]
        D2[资讯服务]
        D3[用户服务]
        D4[OpenClaw 服务]
        D5[预留: RAG 服务]
        D6[预留: Agent 编排服务]
    end

    subgraph 数据层
        E1[(PostgreSQL)]
        E2[(Qdrant 向量数据库)]
        E3[Redis 缓存]
    end

    A1 --> B1
    A1 --> B2
    A2 --> C3
    B1 --> C1
    C1 --> C2
    C3 --> D4
    C2 --> D1
    D1 --> D2
    D1 --> D3
    D2 --> E1
    D2 --> E3
    D3 --> E1
    D4 --> E1
    D5 -.-> E2
    D6 -.-> E2

    style B2 fill:#e1f5fe
    style C3 fill:#fff3e0
    style D5 fill:#f3e5f5
    style D6 fill:#f3e5f5
    style E2 fill:#e8f5e9
```

## 3. 前端架构

### 3.1 目录结构

```
frontend/
├── public/                    # 静态资源
│   ├── models/               # 3D 模型文件
│   └── assets/               # 图片、字体等
├── src/
│   ├── components/           # 组件目录
│   │   ├── ui/              # 基础 UI 组件
│   │   ├── layout/          # 布局组件
│   │   ├── 3d/              # 3D 场景组件
│   │   ├── news/            # 资讯相关组件
│   │   └── common/          # 通用组件
│   ├── pages/               # 页面组件
│   ├── hooks/               # 自定义 Hooks
│   ├── stores/              # Zustand 状态管理
│   ├── api/                 # API 调用层
│   ├── utils/               # 工具函数
│   ├── types/               # TypeScript 类型定义
│   ├── constants/           # 常量定义
│   └── styles/              # 全局样式
├── index.html
├── vite.config.ts
├── tsconfig.json
└── package.json
```

### 3.2 状态管理方案

采用 **Zustand** 作为全局状态管理方案，理由如下：

1. **轻量级**：相比 Redux，Zustand 无需样板代码，API 简洁直观
2. **TypeScript 友好**：完整的类型推导支持
3. **性能优秀**：支持细粒度订阅，避免不必要的重渲染
4. **中间件生态**：支持持久化、日志、Devtools 等扩展

核心 Store 设计：

```typescript
// stores/newsStore.ts
interface NewsState {
  news: NewsItem[];
  currentCategory: string;
  isLoading: boolean;
  fetchNews: (category?: string) => Promise<void>;
  setCategory: (category: string) => void;
}

// stores/authStore.ts
interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  login: (credentials: LoginPayload) => Promise<void>;
  logout: () => void;
}

// stores/uiStore.ts
interface UIState {
  theme: 'light' | 'dark';
  sidebarOpen: boolean;
  activeModal: string | null;
  toggleTheme: () => void;
  toggleSidebar: () => void;
  openModal: (modalId: string) => void;
  closeModal: () => void;
}
```

### 3.3 动画架构

动画系统采用 **React Three Fiber (R3F) + Framer Motion** 双引擎架构：

#### 3.3.1 R3F 负责 3D 场景

- **角色展示**：拟人化 AI 助手的 3D 形象
- **环境渲染**：沉浸式资讯浏览空间
- **交互动画**：鼠标跟随、点击反馈等 3D 交互

核心组件设计：

```typescript
// components/3d/AvatarScene.tsx
interface AvatarProps {
  emotion: 'neutral' | 'happy' | 'thinking' | 'surprised';
  isSpeaking: boolean;
  onInteract: (interactionType: string) => void;
}

// components/3d/NewsSpace.tsx
interface NewsSpaceProps {
  newsItems: NewsItem[];
  activeItemId: string | null;
  onItemSelect: (item: NewsItem) => void;
}
```

#### 3.3.2 Framer Motion 负责 UI 动画

- **页面过渡**：路由切换动画
- **组件动效**：卡片悬浮、按钮反馈、列表加载
- **手势交互**：拖拽、滑动、缩放等触摸操作

动画设计原则：

1. **意义性**：每个动画都应有明确的目的（引导注意力、提供反馈、建立空间关系）
2. **一致性**：同类元素使用相同的动画模式
3. **性能优先**：使用 CSS transform 和 opacity，避免触发重排
4. **可访问性**：支持 prefers-reduced-motion 媒体查询

### 3.4 API 调用层

采用分层架构设计 API 调用：

```typescript
// api/client.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器：添加认证令牌
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器：统一错误处理
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      // 处理未认证情况
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;

// api/services/newsApi.ts
import apiClient from '../client';
import type { NewsItem, NewsFilter, PaginatedResponse } from '@/types';

export const newsApi = {
  getNews: (params?: NewsFilter) =>
    apiClient.get<PaginatedResponse<NewsItem>>('/news', { params }),
  
  getNewsById: (id: string) =>
    apiClient.get<NewsItem>(`/news/${id}`),
  
  getCategories: () =>
    apiClient.get<string[]>('/news/categories'),
};

// api/services/openclawApi.ts
import apiClient from '../client';
import type { OpenClawManifest, OpenClawQuery, OpenClawResponse } from '@/types';

export const openclawApi = {
  getManifest: () =>
    apiClient.get<OpenClawManifest>('/.well-known/openclaw.json'),
  
  query: (data: OpenClawQuery) =>
    apiClient.post<OpenClawResponse>('/openclaw/query', data),
};
```

## 4. 后端架构

### 4.1 目录结构

```
backend/
├── alembic/                  # 数据库迁移
│   ├── versions/
│   └── env.py
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 配置管理
│   ├── dependencies.py      # 依赖注入
│   ├── core/                # 核心功能
│   │   ├── __init__.py
│   │   ├── security.py      # 安全相关
│   │   ├── exceptions.py    # 异常定义
│   │   └── logging.py       # 日志配置
│   ├── api/                 # API 路由层
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py    # v1 路由聚合
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── news.py
│   │   │   │   ├── users.py
│   │   │   │   ├── auth.py
│   │   │   │   └── openclaw.py
│   │   │   └── deps.py
│   │   └── well_known.py    # /.well-known 路由
│   ├── services/            # 服务层
│   │   ├── __init__.py
│   │   ├── news_service.py
│   │   ├── user_service.py
│   │   ├── auth_service.py
│   │   └── openclaw_service.py
│   ├── models/              # 数据模型层
│   │   ├── __init__.py
│   │   ├── base.py          # SQLAlchemy 基类
│   │   ├── user.py
│   │   ├── news.py
│   │   └── category.py
│   ├── schemas/             # Pydantic 模式
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── news.py
│   │   ├── auth.py
│   │   └── openclaw.py
│   └── db/                  # 数据库连接
│       ├── __init__.py
│       └── session.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   └── integration/
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── requirements.txt
├── requirements-dev.txt
└── pyproject.toml
```

### 4.2 API 分层设计

后端采用清晰的分层架构，职责分离明确：

#### 4.2.1 路由层 (Router Layer)

负责 HTTP 请求路由、参数校验和响应格式化。

```python
# app/api/v1/endpoints/news.py
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from app.schemas.news import NewsItem, NewsListResponse, NewsFilter
from app.services.news_service import NewsService
from app.api.v1.deps import get_news_service

router = APIRouter()

@router.get("/news", response_model=NewsListResponse)
async def list_news(
    category: Optional[str] = Query(None, description="资讯分类"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    service: NewsService = Depends(get_news_service)
) -> NewsListResponse:
    """获取资讯列表"""
    filter_params = NewsFilter(
        category=category,
        page=page,
        page_size=page_size
    )
    return await service.get_news_list(filter_params)

@router.get("/news/{news_id}", response_model=NewsItem)
async def get_news_detail(
    news_id: str,
    service: NewsService = Depends(get_news_service)
) -> NewsItem:
    """获取资讯详情"""
    return await service.get_news_by_id(news_id)
```

#### 4.2.2 服务层 (Service Layer)

封装业务逻辑，协调多个数据访问操作，提供事务管理。

```python
# app/services/news_service.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.news import NewsArticle
from app.schemas.news import NewsItem, NewsListResponse, NewsFilter
from app.repositories.news_repository import NewsRepository
from app.core.cache import cache_manager
from app.core.exceptions import NewsNotFoundException

class NewsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = NewsRepository(db)
    
    async def get_news_list(
        self, 
        filter_params: NewsFilter
    ) -> NewsListResponse:
        """获取资讯列表（带缓存）"""
        cache_key = f"news_list:{filter_params.category}:{filter_params.page}"
        
        # 尝试从缓存获取
        cached = await cache_manager.get(cache_key)
        if cached:
            return NewsListResponse.parse_raw(cached)
        
        # 从数据库查询
        news_items, total = await self.repository.get_list(
            category=filter_params.category,
            page=filter_params.page,
            page_size=filter_params.page_size
        )
        
        response = NewsListResponse(
            items=[NewsItem.from_orm(item) for item in news_items],
            total=total,
            page=filter_params.page,
            page_size=filter_params.page_size
        )
        
        # 写入缓存（5 分钟）
        await cache_manager.set(cache_key, response.json(), ttl=300)
        
        return response
    
    async def get_news_by_id(self, news_id: str) -> NewsItem:
        """获取资讯详情"""
        news = await self.repository.get_by_id(news_id)
        if not news:
            raise NewsNotFoundException(f"资讯 {news_id} 不存在")
        return NewsItem.from_orm(news)
```

#### 4.2.3 数据访问层 (Repository Layer)

封装数据库访问逻辑，提供数据持久化操作。

```python
# app/repositories/news_repository.py
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.news import NewsArticle

class NewsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_list(
        self, 
        category: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[NewsArticle], int]:
        """分页查询资讯列表"""
        query = select(NewsArticle)
        
        if category:
            query = query.where(NewsArticle.category == category)
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar()
        
        # 分页查询
        query = query.order_by(NewsArticle.published_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        return result.scalars().all(), total
    
    async def get_by_id(self, news_id: str) -> Optional[NewsArticle]:
        """根据 ID 查询资讯"""
        query = select(NewsArticle).where(NewsArticle.id == news_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
```

## 5. 部署架构

### 5.1 容器化部署

采用 Docker 容器化部署方案，实现环境一致性和快速扩缩容：

```yaml
# docker-compose.yml
version: '3.8'

services:
  # 前端服务
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
    environment:
      - VITE_API_BASE_URL=http://api:8000
    depends_on:
      - api

  # 后端 API 服务
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/ainews
      - REDIS_URL=redis://redis:6379
      - QDRANT_URL=http://qdrant:6333
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      - postgres
      - redis
      - qdrant

  # PostgreSQL 数据库
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=ainews
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  # Redis 缓存
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"

  # Qdrant 向量数据库
  qdrant:
    image: qdrant/qdrant:latest
    volumes:
      - qdrant_data:/qdrant/storage
    ports:
      - "6333:6333"

volumes:
  postgres_data:
  redis_data:
  qdrant_data:
```

### 5.2 负载均衡与高可用

生产环境部署架构：

```
                    +------------------+
                    |   Cloudflare     |
                    |   CDN + DNS      |
                    +--------+---------+
                             |
                    +--------v---------+
                    |   Traefik LB     |
                    |   (SSL + 路由)    |
                    +--------+---------+
                             |
            +----------------v----------------+
            |                                 |
   +--------v---------+           +---------v--------+
   |  Frontend Pod 1  |           |  Frontend Pod 2  |
   |  (Nginx + SPA) |           |  (Nginx + SPA) |
   +--------+--------+           +---------+--------+
            |                                 |
            +----------------v----------------+
                             |
                    +--------v---------+
                    |   API Gateway    |
                    |   (Rate Limit)   |
                    +--------+---------+
                             |
            +----------------v----------------+
            |                                 |
   +--------v---------+           +---------v--------+
   |   API Pod 1      |           |   API Pod 2      |
   |   (FastAPI)      |           |   (FastAPI)      |
   +--------+---------+           +---------+--------+
            |                                 |
            +----------------v----------------+
                             |
            +----------------v----------------+
            |                                 |
   +--------v---------+           +---------v--------+
   |   PostgreSQL     |           |     Redis        |
   |   (Primary)      |           |   (Cluster)      |
   +------------------+           +------------------+
```

## 6. 数据流设计

### 6.1 资讯浏览流程

```
用户打开首页
    |
    v
Frontend: 调用 API GET /api/v1/news
    |
    v
API Gateway: 路由到 News Service
    |
    v
News Service: 
  1. 检查 Redis 缓存
  2. 缓存未命中，查询 PostgreSQL
  3. 写入 Redis 缓存（TTL: 5 分钟）
  4. 返回分页结果
    |
    v
Frontend: 渲染资讯列表
    |
    v
用户点击某条资讯
    |
    v
Frontend: 调用 API GET /api/v1/news/{id}
    |
    v
News Service: 查询详情并返回
    |
    v
Frontend: 渲染详情页
```

### 6.2 OpenClaw 智能体查询流程

```
AI 智能体发起请求
    |
    v
OpenClaw Protocol Adapter:
  1. 解析 OpenClaw 标准请求格式
  2. 转换为内部 API 调用
    |
    v
News Service: 执行查询逻辑
    |
    v
OpenClaw Protocol Adapter:
  1. 格式化响应为 OpenClaw 标准格式
  2. 添加机器可读元数据
    |
    v
返回给 AI 智能体
```

### 6.3 用户认证流程

```
用户输入用户名/密码
    |
    v
Frontend: POST /api/v1/auth/login
    |
    v
Auth Service:
  1. 查询用户表验证密码
  2. 生成 JWT Token (Access + Refresh)
  3. 返回 Token 给客户端
    |
    v
Frontend: 存储 Token (LocalStorage)
    |
    v
后续请求:
  Header: Authorization: Bearer {token}
    |
    v
API Gateway: 验证 JWT Token
    |
    v
Token 有效: 继续处理请求
Token 无效/过期: 返回 401
```

## 7. 技术选型理由

### 7.1 前端技术栈

| 技术 | 选型理由 |
|------|----------|
| **React 18** | 成熟的组件化框架，庞大的生态，Hooks 带来更清晰的逻辑复用 |
| **TypeScript** | 静态类型检查，提升代码可维护性，IDE 智能提示 |
| **Vite** | 极速冷启动，ESM 原生支持，优秀的开发体验 |
| **React Three Fiber** | React 生态内的 Three.js 封装，声明式 3D 场景描述 |
| **Framer Motion** | React 友好的动画库，声明式 API，性能优秀 |
| **Zustand** | 极简状态管理，无样板代码，TypeScript 支持完美 |

### 7.2 后端技术栈

| 技术 | 选型理由 |
|------|----------|
| **Python 3.11+** | AI 生态最丰富的语言，大量 ML/AI 库支持 |
| **FastAPI** | 高性能异步框架，自动生成 OpenAPI 文档，类型注解驱动 |
| **SQLAlchemy 2.0** | ORM 标杆，支持异步操作，强大的查询构建器 |
| **Alembic** | SQLAlchemy 官方迁移工具，版本化管理数据库结构 |
| **Pydantic** | 数据验证和序列化，FastAPI 原生集成 |
| **Uvicorn** | ASGI 服务器，支持异步，性能优秀 |

### 7.3 数据库与存储

| 技术 | 选型理由 |
|------|----------|
| **PostgreSQL 15** | 功能最强大的开源关系数据库，支持 JSON、全文搜索，稳定性佳 |
| **Qdrant** | 开源向量数据库，Rust 编写高性能，支持混合搜索 |
| **Redis** | 内存数据库，用作缓存和会话存储，极高性能 |

### 7.4 部署与运维

| 技术 | 选型理由 |
|------|----------|
| **Docker** | 容器化标准，保证环境一致性 |
| **Docker Compose** | 本地开发和测试环境编排 |
| **Traefik** | 云原生边缘路由器，自动服务发现和 SSL |
| **Nginx** | 高性能 Web 服务器，静态资源服务 |

### 7.5 为何不使用某些流行技术

| 未选技术 | 原因 |
|----------|------|
| **Next.js** | 项目需要复杂的 3D 交互，Next.js 的服务端渲染优势不明显，反而增加复杂度 |
| **tRPC** | 团队已有 REST API 经验，tRPC 的学习成本和生态锁定不如标准 REST 开放 |
| **GraphQL** | 项目数据结构相对固定，GraphQL 的灵活性和复杂性不适合当前阶段 |
| **Django** | 太重，不符合轻量、高性能的需求，FastAPI 更适合微服务架构 |
| **MongoDB** | 数据关系明确，PostgreSQL 的关系模型和 ACID 特性更合适 |

---

**文档版本**: 1.0  
**最后更新**: 2025年3月19日  
**维护者**: 技术团队
