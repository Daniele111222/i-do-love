# AI News Hub 开发指南

> 最后更新：2026-03-19
> 版本：v1.0.0

---

## 1. 开发环境准备

### 1.1 系统要求

| 要求 | 最低配置 | 推荐配置 |
|------|----------|----------|
| 操作系统 | Windows 10 / macOS 10.15 / Ubuntu 20.04 | Windows 11 / macOS 13 / Ubuntu 22.04 |
| 内存 | 8GB | 16GB+ |
| 存储 | 20GB 可用空间 | 50GB+ SSD |
| Node.js | 18.x | 20.x |
| Python | 3.11 | 3.12 |
| Git | 2.30+ | 最新 |

### 1.2 必需工具

```bash
# Node.js (前端)
# https://nodejs.org/
node --version  # >= 18.0.0

# Python (后端)
# https://www.python.org/
python --version  # >= 3.11

# Git
git --version  # >= 2.30

# Docker (可选，用于本地数据库)
# https://docker.com/
docker --version
```

### 1.3 开发工具推荐

| 工具 | 用途 | 平台 |
|------|------|------|
| VS Code | 代码编辑器 | 全平台 |
| PyCharm | Python IDE | 全平台 |
| DataGrip | 数据库客户端 | 全平台 |
| Postman | API 测试 | 全平台 |
| TablePlus | 数据库管理 | 全平台 |
| Figma | UI 设计协作 | Web |

---

## 2. 项目初始化

### 2.1 克隆项目

```bash
git clone https://github.com/your-org/ai-news-hub.git
cd ai-news-hub
```

### 2.2 前端初始化

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 复制环境变量
cp .env.example .env.local

# 启动开发服务器
npm run dev
```

### 2.3 后端初始化

```bash
# 新开终端，进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 复制环境变量
cp .env.example .env

# 启动开发服务器
uvicorn app.main:app --reload --port 8000
```

### 2.4 数据库启动（使用 Docker）

```bash
# 启动 PostgreSQL
docker run -d \
  --name ai_news_pg \
  -e POSTGRES_USER=ai_news \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=ai_news \
  -p 5432:5432 \
  postgres:16

# 启动 Redis
docker run -d \
  --name ai_news_redis \
  -p 6379:6379 \
  redis:7-alpine
```

### 2.5 数据库迁移

```bash
cd backend

# 运行迁移
alembic upgrade head

# 创建测试数据（可选）
python -m scripts.seed_db
```

---

## 3. 项目结构

### 3.1 目录概览

```
ai-news-hub/
├── frontend/                # React 前端
│   ├── src/
│   │   ├── components/     # 组件
│   │   ├── pages/          # 页面
│   │   ├── hooks/          # 自定义 Hooks
│   │   ├── stores/         # 状态管理
│   │   ├── services/       # API 服务
│   │   ├── types/          # TypeScript 类型
│   │   └── utils/          # 工具函数
│   └── tests/              # 测试
│
├── backend/                # FastAPI 后端
│   ├── app/
│   │   ├── api/           # API 路由
│   │   ├── core/          # 核心模块
│   │   ├── models/        # 数据库模型
│   │   ├── schemas/       # Pydantic 模型
│   │   └── services/      # 业务逻辑
│   └── tests/             # 测试
│
├── docs/                   # 文档
│   ├── requirements/       # 需求文档
│   └── *.md              # 其他文档
│
└── docker-compose.yml      # Docker 编排
```

---

## 4. 前端开发规范

### 4.1 代码规范

#### 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 组件 | PascalCase | `AuthBall.tsx` |
| Hooks | camelCase，use 前缀 | `useAuth.ts` |
| 工具函数 | camelCase | `formatDate.ts` |
| 常量 | UPPER_SNAKE_CASE | `MAX_PAGE_SIZE` |
| 类型/接口 | PascalCase，I 前缀 | `IUser` |

#### 组件规范

```tsx
// ✅ 正确示例
import { useState, useEffect } from 'react';
import type { FC } from 'react';
import { Button } from '@/components/common';

interface ArticleCardProps {
  title: string;
  summary: string;
  publishedAt: Date;
  onClick?: () => void;
}

export const ArticleCard: FC<ArticleCardProps> = ({
  title,
  summary,
  publishedAt,
  onClick,
}) => {
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Effect logic
  }, []);

  return (
    <div className="article-card" onClick={onClick}>
      <h3>{title}</h3>
      <p>{summary}</p>
      <span>{formatDate(publishedAt)}</span>
    </div>
  );
};
```

#### 样式规范

```tsx
// 使用 Tailwind CSS
// ✅ 正确
<div className="flex items-center gap-4 p-4">

// ❌ 错误
<div style={{ display: 'flex', padding: '16px' }}>
```

### 4.2 API 调用规范

```typescript
// services/api.ts - Axios 实例配置
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器
api.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    if (error.response?.status === 401) {
      // Token 过期处理
      await authService.refreshToken();
    }
    return Promise.reject(error);
  }
);

// services/articleService.ts - API 服务
import { api } from './api';
import type { Article, ArticleListResponse } from '@/types/article';

export const articleService = {
  getList: (params: { page?: number; pageSize?: number }) =>
    api.get<ArticleListResponse>('/articles', { params }),

  getById: (id: number) =>
    api.get<Article>(`/articles/${id}`),

  create: (data: CreateArticleDto) =>
    api.post<Article>('/articles', data),

  update: (id: number, data: UpdateArticleDto) =>
    api.put<Article>(`/articles/${id}`, data),

  delete: (id: number) =>
    api.delete(`/articles/${id}`),
};
```

### 4.3 状态管理规范

```typescript
// stores/authStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User } from '@/types/user';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      login: async (email, password) => {
        const response = await authService.login(email, password);
        set({
          user: response.user,
          token: response.access_token,
          isAuthenticated: true,
        });
      },

      logout: () => {
        set({ user: null, token: null, isAuthenticated: false });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        token: state.token,
        user: state.user,
      }),
    }
  )
);
```

### 4.4 3D 组件开发规范

```tsx
// components/AuthBall/AuthBall.tsx
import { Canvas } from '@react-three/fiber';
import { Suspense } from 'react';

export const AuthBall = () => {
  return (
    <div className="auth-ball-container" style={{ width: '100%', height: '400px' }}>
      <Canvas camera={{ position: [0, 0, 5], fov: 50 }}>
        <Suspense fallback={null}>
          {/* 场景内容 */}
        </Suspense>
      </Canvas>
    </div>
  );
};

// 组件拆分
// - BallBody.tsx: 球体本身
// - Eye.tsx: 眼球，包含跟随逻辑
// - Hand.tsx: 手部，包含捂眼动画
// - expressions.ts: 表情状态定义
```

---

## 5. 后端开发规范

### 5.1 代码规范

#### 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 模块 | snake_case | `article_service.py` |
| 类 | PascalCase | `ArticleService` |
| 函数 | snake_case | `get_article_by_id` |
| 常量 | UPPER_SNAKE_CASE | `MAX_PAGE_SIZE` |
| 类型 | PascalCase | `ArticleCreate` |

#### FastAPI 路由规范

```python
# app/api/v1/articles.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/articles", tags=["Articles"])


def get_db():
    """数据库依赖"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[ArticleResponse])
async def list_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取文章列表"""
    articles = await article_service.get_list(
        db=db,
        page=page,
        page_size=page_size,
        category_id=category_id,
    )
    return articles


@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: int,
    db: Session = Depends(get_db),
):
    """获取文章详情"""
    article = await article_service.get_by_id(db, article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在"
        )
    return article
```

#### Pydantic Schema 规范

```python
# app/schemas/article.py
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List


class ArticleBase(BaseModel):
    """基础 Schema"""
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    summary: Optional[str] = None
    source_url: Optional[str] = None


class ArticleCreate(ArticleBase):
    """创建文章 Schema"""
    category_id: Optional[int] = None
    tag_ids: List[int] = []


class ArticleUpdate(BaseModel):
    """更新文章 Schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = Field(None, min_length=1)
    category_id: Optional[int] = None


class ArticleResponse(ArticleBase):
    """响应 Schema"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime
    category: Optional["CategoryResponse"] = None
```

### 5.2 服务层规范

```python
# app/services/article_service.py
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.article import Article
from app.schemas.article import ArticleCreate, ArticleUpdate


class ArticleService:
    """文章服务"""
    
    async def get_list(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 20,
        category_id: Optional[int] = None,
    ) -> List[Article]:
        """获取文章列表"""
        query = db.query(Article)
        
        if category_id:
            query = query.filter(Article.category_id == category_id)
        
        offset = (page - 1) * page_size
        return query.offset(offset).limit(page_size).all()
    
    async def get_by_id(self, db: Session, article_id: int) -> Optional[Article]:
        """获取文章详情"""
        return db.query(Article).filter(Article.id == article_id).first()
    
    async def create(self, db: Session, article_data: ArticleCreate) -> Article:
        """创建文章"""
        article = Article(**article_data.model_dump())
        db.add(article)
        db.commit()
        db.refresh(article)
        return article


# 依赖注入
def get_article_service() -> ArticleService:
    return ArticleService()
```

### 5.3 认证中间件

```python
# app/core/security.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"
SECRET_KEY = os.getenv("SECRET_KEY")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """哈希密码"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """解码令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
```

---

## 6. Git 工作流

### 6.1 分支命名

| 类型 | 命名格式 | 示例 |
|------|----------|------|
| 功能分支 | feature/{issue-id}-{short-desc} | feature/23-add-login |
| 修复分支 | fix/{issue-id}-{short-desc} | fix/42-fix-auth-error |
| 热修复分支 | hotfix/{issue-id}-{short-desc} | hotfix/99-critical-bug |
| 发布分支 | release/{version} | release/v1.0.0 |

### 6.2 Commit 规范

```
{类型}({范围}): {描述}

[可选正文]

[可选页脚]
```

#### 类型

| 类型 | 描述 |
|------|------|
| feat | 新功能 |
| fix | 修复 bug |
| docs | 文档更新 |
| style | 代码格式（不影响功能） |
| refactor | 重构（不是新功能或修复） |
| test | 测试相关 |
| chore | 构建/工具相关 |

#### 示例

```
feat(auth): 添加 JWT 认证

- 实现 Access Token 和 Refresh Token
- 添加 Token 刷新接口
- 集成 Redis 黑名单

Closes #23
```

### 6.3 Pull Request 流程

1. 从 `develop` 创建功能分支
2. 开发完成后提交 Pull Request
3. 至少 1 人 Code Review
4. CI/CD 通过后合并到 `develop`
5. 发布时从 `develop` 合并到 `main`

---

## 7. 测试规范

### 7.1 前端测试

```bash
# 运行测试
npm run test

# 覆盖率
npm run test:coverage

# 监听模式
npm run test:watch
```

```tsx
// 组件测试示例
import { render, screen, fireEvent } from '@testing-library/react';
import { ArticleCard } from './ArticleCard';

describe('ArticleCard', () => {
  it('renders title and summary', () => {
    render(
      <ArticleCard
        title="Test Title"
        summary="Test Summary"
        publishedAt={new Date('2024-01-01')}
      />
    );
    
    expect(screen.getByText('Test Title')).toBeInTheDocument();
    expect(screen.getByText('Test Summary')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const onClick = jest.fn();
    render(<ArticleCard onClick={onClick} />);
    
    fireEvent.click(screen.getByRole('article'));
    expect(onClick).toHaveBeenCalledTimes(1);
  });
});
```

### 7.2 后端测试

```bash
# 运行测试
pytest

# 覆盖率
pytest --cov=app --cov-report=html

# 指定文件
pytest tests/test_articles.py -v
```

```python
# 测试示例
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_article():
    response = client.post(
        "/api/v1/articles",
        json={
            "title": "Test Article",
            "content": "Test Content",
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == 201
    assert response.json()["title"] == "Test Article"


def test_get_article_not_found():
    response = client.get("/api/v1/articles/99999")
    assert response.status_code == 404
```

---

## 8. 代码审查清单

### 8.1 PR 检查项

- [ ] 代码符合项目规范
- [ ] 有适当的测试覆盖
- [ ] 没有硬编码的秘密
- [ ] API 变更已更新文档
- [ ] 消除了所有 lint 错误
- [ ] 性能影响已评估

### 8.2 常见问题

| 问题 | 检查项 |
|------|--------|
| 安全 | 敏感数据、日志泄露、SQL 注入 |
| 性能 | N+1 查询、大循环、同步阻塞 |
| 可维护性 | 重复代码、过长函数、魔法数字 |
| 错误处理 | 空指针、异常吞没、无效输入 |

---

## 9. 调试技巧

### 9.1 前端调试

```typescript
// Redux DevTools (Zustand)
import { useStore } from './store';

// 在控制台
getState() // 获取当前状态
dispatch({ type: 'login' }) // 触发 action
```

### 9.2 后端调试

```python
# 使用 pdb
import pdb
pdb.set_trace()

# 使用日志
import logging
logger = logging.getLogger(__name__)
logger.debug("Variable: %s", variable)
```

### 9.3 API 调试

```bash
# 登录获取 token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'

# 使用 token 请求
curl http://localhost:8000/api/v1/articles \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 10. 常见问题

### 10.1 前端问题

| 问题 | 解决方案 |
|------|----------|
| 依赖安装失败 | 删除 node_modules 和 package-lock.json，重新 `npm install` |
| 类型错误 | 检查 import 路径，确保类型定义正确 |
| 样式不生效 | 确认 Tailwind 编译成功，检查 class 拼写 |

### 10.2 后端问题

| 问题 | 解决方案 |
|------|----------|
| 数据库连接失败 | 检查 PostgreSQL 是否运行，验证环境变量 |
| 迁移失败 | 检查数据库连接，确保版本兼容 |
| Import 错误 | 确认在正确的虚拟环境中 |

---

## 11. 资源链接

### 11.1 学习资源

| 资源 | 链接 |
|------|------|
| React 文档 | https://react.dev |
| TypeScript 手册 | https://www.typescriptlang.org/docs/ |
| FastAPI 文档 | https://fastapi.tiangolo.com |
| React Three Fiber | https://docs.pmnd.rs/react-three-fiber |

### 11.2 工具文档

| 工具 | 链接 |
|------|------|
| Tailwind CSS | https://tailwindcss.com/docs |
| Zustand | https://docs.pmnd.rs/zustand |
| SQLAlchemy | https://docs.sqlalchemy.org |
| Pydantic | https://docs.pydantic.dev |

---

*本指南将随着项目发展持续更新*
