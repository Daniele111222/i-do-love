# V1 产品设计文档

**日期:** 2026-05-29
**版本:** 1.0
**状态:** 待开发

---

## 1. 产品定位

| 维度 | 决策 |
|------|------|
| 目标用户 | 小范围共享（邀请制，不开放公众注册） |
| UI 风格 | 极简信息流 — 白色背景、文字为主、高信息密度，类似 Hacker News / Lobsters |
| 内容模式 | 摘要 + 原文链接 — 列表展示标题和内容摘要，点击跳转原文 |
| AI 能力 | 后期再说 — V1 不做 AI 摘要和 RAG 问答 |
| 首版范围 | 完整最小闭环 — 信息流 + 文章详情 + 搜索 + 来源管理 + 登录注册 + 用户中心 |

---

## 2. 前端页面（7 个）

| # | 页面 | 路由 | 核心功能 | 需认证 |
|---|------|------|----------|--------|
| 1 | 首页信息流 | `/` | 文章卡片列表、按时间降序、标签筛选、分页加载 | 否 |
| 2 | 文章详情 | `/articles/:id` | 标题/摘要/元信息（作者/时间/来源）、跳转原文按钮 | 否 |
| 3 | 搜索 | `/search` | 关键词输入、搜索结果列表、分页 | 否 |
| 4 | 来源管理 | `/sources` | 来源列表（含文章数）、添加 RSS/Atom 源、删除来源 | 是 |
| 5 | 登录 | `/auth/login` | 邮箱 + 密码表单 | 否 |
| 6 | 注册 | `/auth/register` | 邮箱 + 密码 + 昵称表单 | 否 |
| 7 | 用户中心 | `/user` | 查看/修改个人资料、修改密码、会话管理（列表+吊销） | 是 |

### 2.1 路由结构

```
/                              → 首页（公开）
/articles/:id                  → 文章详情（公开）
/search                        → 搜索（公开）
/sources                       → 来源管理（需登录）
/auth/login                    → 登录（未登录用户）
/auth/register                 → 注册（未登录用户）
/user                          → 用户中心（需登录，含资料/密码/会话 tab）
```

### 2.2 导航结构

- **公开导航**: 首页 | 搜索
- **登录后导航**: 首页 | 搜索 | 来源管理 | 用户中心（下拉菜单: 资料/会话/登出）
- **Footer**: © 2026 AI News Hub

### 2.3 组件树（按页面）

**首页 `/`**
```
HomePage
├── Header (Logo + 导航 + 用户状态)
├── TagFilterBar (标签横向滚动选择器)
├── ArticleList
│   └── ArticleCard × N (标题 + 摘要前200字 + 来源 + 时间 + 标签)
├── Pagination
└── Footer
```

**文章详情 `/articles/:id`**
```
ArticleDetailPage
├── Header
├── ArticleMeta (来源名称、作者、发布时间)
├── ArticleTitle
├── ArticleTags
├── ArticleSummary (文章摘要/描述)
├── ExternalLinkButton ("阅读原文 →")
└── Footer
```

**搜索 `/search`**
```
SearchPage
├── Header
├── SearchInput (搜索框 + 提交按钮)
├── SearchResultList
│   └── ArticleCard × N
├── Pagination
└── Footer
```

**来源管理 `/sources`**
```
SourcesPage (需登录)
├── Header
├── SourceAddForm (URL 输入 + 名称输入 + 提交)
├── SourceList
│   └── SourceRow × N (名称、URL、文章数、删除按钮)
└── Footer
```

**登录 `/auth/login`**
```
LoginPage
├── Header
├── LoginForm (email + password + 提交 + 错误提示)
├── Link to /auth/register
└── Footer
```

**注册 `/auth/register`**
```
RegisterPage
├── Header
├── RegisterForm (email + password + nickname + 提交 + 错误提示)
├── Link to /auth/login
└── Footer
```

**用户中心 `/user`**
```
UserPage (需登录)
├── Header
├── Tabs
│   ├── Tab: 个人资料 → ProfileForm (昵称修改)
│   ├── Tab: 修改密码 → PasswordForm (旧密码 + 新密码 + 确认)
│   └── Tab: 会话管理 → SessionList → SessionRow × N (设备/IP/时间/当前标记/吊销按钮)
└── Footer
```

---

## 3. 后端 API（V1 新增 8 个接口）

全部挂载在 `/api/v1` 下。

### 3.1 内容相关（4 个）

| 方法 | 路径 | 说明 | 认证 | 查询参数 |
|------|------|------|------|----------|
| `GET` | `/articles` | 文章分页列表 | 否 | `?page=1&size=20&tag=xxx&source_id=N` |
| `GET` | `/articles/{id}` | 文章详情 | 否 | — |
| `GET` | `/articles/search` | 全文搜索 | 否 | `?q=keyword&page=1&size=20` |
| `GET` | `/tags` | 标签列表+文章计数 | 否 | — |

### 3.2 来源管理（3 个）

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| `GET` | `/sources` | 来源列表+文章计数 | 是 |
| `POST` | `/sources` | 添加 RSS/Atom 来源 | 是 |
| `DELETE` | `/sources/{id}` | 删除来源及关联文章 | 是 |

### 3.3 用户相关（1 个）

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| `PUT` | `/auth/me` | 更新昵称和/或密码 | 是 |

### 3.4 请求/响应 Schema

#### `GET /articles`

**请求：**
```
?page=1&size=20&tag=AI&source_id=1
```

**响应：**
```json
{
  "items": [
    {
      "id": 1,
      "title": "OpenAI 发布 GPT-5",
      "summary": "内容前 200 字符...",
      "source_name": "TechCrunch",
      "source_id": 1,
      "author": "John Doe",
      "source_url": "https://techcrunch.com/...",
      "published_at": "2026-05-29T10:00:00Z",
      "tags": ["AI", "OpenAI"],
      "created_at": "2026-05-29T10:05:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "size": 20
}
```

#### `GET /articles/search`

**请求：**
```
?q=GPT-5&page=1&size=20
```

**响应：** 同 `/articles` 的分页结构

#### `POST /sources`

**请求：**
```json
{
  "url": "https://techcrunch.com/feed/",
  "name": "TechCrunch"
}
```

**响应：**
```json
{
  "id": 1,
  "name": "TechCrunch",
  "url": "https://techcrunch.com/feed/",
  "article_count": 0,
  "created_at": "2026-05-29T10:00:00Z"
}
```

#### `GET /sources`

**响应：**
```json
{
  "items": [
    {
      "id": 1,
      "name": "TechCrunch",
      "url": "https://techcrunch.com/feed/",
      "article_count": 42,
      "created_at": "2026-05-29T10:00:00Z"
    }
  ]
}
```

#### `PUT /auth/me`

**请求（部分更新即可）：**
```json
{
  "nickname": "新昵称",
  "password": "新密码（可选）"
}
```

**响应：** `UserResponse`（现有 schema）

#### `GET /tags`

**响应：**
```json
{
  "items": [
    { "name": "AI", "article_count": 45 },
    { "name": "OpenAI", "article_count": 12 }
  ]
}
```

---

## 4. 数据流

### 4.1 内容入库流程（已实现）

```
RSS源 ─→ POST /ingest/feed ─→ IngestJob(pending) ─→ Worker 抓取 ─→ Article 入库
Webhook ─→ POST /ingest/webhook ─→ HMAC 校验 ─→ Article 入库
```

### 4.2 内容消费流程（V1 新增）

```
用户访问 / ─→ GET /articles(分页) ─→ ArticleCard 列表渲染
用户点标题 ─→ /articles/:id ─→ GET /articles/:id ─→ 详情页渲染
用户点"阅读原文" ─→ 新标签页跳转 source_url
用户搜索 ─→ /search ─→ GET /articles/search?q= ─→ 结果列表渲染
```

### 4.3 来源管理流程（V1 新增）

```
管理员 ─→ /sources ─→ GET /sources ─→ 来源列表
管理员 ─→ 输入URL+名称 ─→ POST /sources ─→ 刷新列表
管理员 ─→ 点删除 ─→ DELETE /sources/:id ─→ 刷新列表
```

---

## 5. 需改动的文件

### 5.1 后端

| 文件 | 操作 | 说明 |
|------|------|------|
| `app/api/v1/router.py` | 修改 | 注册新路由 |
| `app/api/v1/articles.py` | **新增** | 文章列表/详情/搜索 API |
| `app/api/v1/sources.py` | **新增** | 来源 CRUD API |
| `app/api/v1/auth.py` | 修改 | 新增 `PUT /auth/me` |
| `app/schemas/article.py` | **新增** | 文章请求/响应 schema |
| `app/schemas/source.py` | **新增** | 来源请求/响应 schema |
| `app/services/article_service.py` | **新增** | 文章业务逻辑（列表/搜索/详情） |
| `app/services/source_service.py` | **新增** | 来源业务逻辑（CRUD + 文章计数） |
| `tests/test_articles.py` | **新增** | 文章 API 测试 |
| `tests/test_sources.py` | **新增** | 来源 API 测试 |
| `tests/test_auth.py` | 修改 | 补 `PUT /auth/me` 测试 |
| `app/core/config.py` | 修改 | 新增分页默认配置 |
| `app/models/article.py` | 不改 | 已有关键词搜索可能需加 GIN 索引迁移 |

### 5.2 前端

| 文件 | 操作 | 说明 |
|------|------|------|
| `src/routes/index.tsx` | 修改 | 注册所有新路由 |
| `src/pages/Home/index.tsx` | 重写 | 信息流页面 |
| `src/pages/ArticleDetail/index.tsx` | **新增** | 文章详情页 |
| `src/pages/Search/index.tsx` | **新增** | 搜索页 |
| `src/pages/Sources/index.tsx` | **新增** | 来源管理页 |
| `src/pages/Login/index.tsx` | **新增** | 登录页 |
| `src/pages/Register/index.tsx` | **新增** | 注册页 |
| `src/pages/User/index.tsx` | **新增** | 用户中心页 |
| `src/components/Header/Header.tsx` | 修改 | 完整导航 + 用户状态 |
| `src/components/ArticleCard.tsx` | **新增** | 文章卡片组件 |
| `src/components/ArticleList.tsx` | **新增** | 文章列表容器 |
| `src/components/TagFilterBar.tsx` | **新增** | 标签筛选栏 |
| `src/components/Pagination.tsx` | **新增** | 分页组件 |
| `src/components/ProtectedRoute.tsx` | **新增** | 登录守卫 |
| `src/services/articleService.ts` | **新增** | 文章 API 封装 |
| `src/services/sourceService.ts` | **新增** | 来源 API 封装 |
| `src/services/authService.ts` | **新增** | 认证 API 封装 + token 管理 |
| `src/stores/authStore.ts` | **新增** | 认证状态管理（Zustand） |
| `src/components/EmptyState.tsx` | **新增** | 空状态组件 |
| `src/components/ErrorState.tsx` | **新增** | 错误状态组件 |
| `src/components/LoadingSpinner.tsx` | **新增** | 加载状态组件 |

---

## 6. 技术决策

| 决策点 | 选择 | 理由 |
|------|------|------|
| 分页策略 | 传统 offset 分页（`?page=&size=`） | 文章数量可控，比游标分页更简单 |
| 搜索实现 | PostgreSQL `tsvector` + GIN 索引 | 已有 PG 基础设施，不引入 Elasticsearch |
| 摘要字段 | 复用 Article.content 截取前 200 字符 | 不做 AI 摘要，不需要新字段 |
| 认证状态 | Zustand store + localStorage token | 轻量，不需要引入 Redux |
| 路由守卫 | `ProtectedRoute` 包裹组件 + 重定向 | React Router 标准模式 |
| 标签存储 | 复用 Article.tags (JSON 字段) | 已有，无需改模型 |

---

## 7. 不在 V1 范围内的

- AI 摘要生成
- RAG 问答
- 文章收藏 / 稍后读
- 阅读历史
- 深色模式
- 管理后台（Admin）
- 用户头像
- 邮箱验证
- OAuth 第三方登录
- 3D 动画效果
