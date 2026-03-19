# API 规范文档

> 版本: 1.0.0  
> 更新日期: 2026-03-19  
> 文档状态: 草稿

---

## 1. 概述

### 1.1 文档目的

本文档定义了 AI News Hub 平台的 API 接口规范,为前端开发、第三方集成以及 API 消费者提供清晰的接口定义和使用指南。

### 1.2 设计原则

我们的 API 设计遵循以下核心原则:

- **RESTful 风格**: 使用 HTTP 方法和 URL 路径清晰表达资源操作
- **面向资源**: 以名词为中心,避免使用动词定义 URL
- **一致性**: 保持命名、格式和行为的统一
- **可预测性**: 相同输入始终产生相同输出
- **版本控制**: 通过 URL 路径版本化,便于演进

### 1.3 基础信息

- **Base URL**: `https://api.ainewshub.com`
- **协议**: HTTPS (强制)
- **字符编码**: UTF-8
- **请求格式**: JSON
- **响应格式**: JSON
- **时区**: UTC

### 1.4 版本控制

API 版本通过 URL 路径体现:

```
/api/v1/{resource}
/api/v2/{resource}  # 未来版本
```

当前版本: `v1`

版本升级策略:
- 新增字段: 向后兼容,小版本更新
- 移除字段: 破坏性变更,大版本更新
- 提前 6 个月通知破坏性变更

---

## 2. 认证机制

### 2.1 认证方式

API 采用 JWT (JSON Web Token) 认证机制:

- **Access Token**: 短期有效(15分钟),用于 API 请求认证
- **Refresh Token**: 长期有效(7天),用于获取新的 Access Token

### 2.2 Token 获取

通过登录接口获取双 Token。

### 2.3 请求认证

在所有需要认证的请求中,在 HTTP Header 中包含 Access Token:

```http
Authorization: Bearer {access_token}
```

### 2.4 Token 刷新

当 Access Token 过期时(收到 401 响应),使用 Refresh Token 获取新的 Access Token:

```http
POST /api/v1/auth/refresh
Authorization: Bearer {refresh_token}
```

---

## 3. 错误处理

### 3.1 错误响应格式

所有错误响应采用统一格式:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "人类可读的错误描述",
    "details": {
      "field": "具体字段信息",
      "constraint": "约束条件"
    },
    "request_id": "req_abc123xyz",
    "timestamp": "2026-03-19T10:30:00Z"
  }
}
```

### 3.2 HTTP 状态码

| 状态码 | 含义 | 使用场景 |
|--------|------|----------|
| 200 | OK | 请求成功 |
| 201 | Created | 资源创建成功 |
| 204 | No Content | 删除成功,无返回内容 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 认证失败或 Token 过期 |
| 403 | Forbidden | 无权限访问 |
| 404 | Not Found | 资源不存在 |
| 409 | Conflict | 资源冲突(如重复创建) |
| 422 | Unprocessable Entity | 验证失败 |
| 429 | Too Many Requests | 请求频率超限 |
| 500 | Internal Server Error | 服务器内部错误 |
| 503 | Service Unavailable | 服务暂时不可用 |

### 3.3 错误码定义

#### 认证相关 (AUTH_*)

| 错误码 | 描述 | HTTP 状态 |
|--------|------|-----------|
| AUTH_INVALID_CREDENTIALS | 用户名或密码错误 | 401 |
| AUTH_TOKEN_EXPIRED | Token 已过期 | 401 |
| AUTH_TOKEN_INVALID | Token 格式无效 | 401 |
| AUTH_TOKEN_REVOKED | Token 已被撤销 | 401 |
| AUTH_REFRESH_FAILED | Refresh Token 无效 | 401 |
| AUTH_UNAUTHORIZED | 未提供认证信息 | 401 |
| AUTH_FORBIDDEN | 无权限执行操作 | 403 |

#### 用户相关 (USER_*)

| 错误码 | 描述 | HTTP 状态 |
|--------|------|-----------|
| USER_NOT_FOUND | 用户不存在 | 404 |
| USER_EMAIL_EXISTS | 邮箱已被注册 | 409 |
| USER_USERNAME_EXISTS | 用户名已被使用 | 409 |
| USER_INVALID_EMAIL | 邮箱格式无效 | 400 |
| USER_INVALID_PASSWORD | 密码不符合要求 | 400 |
| USER_PROFILE_UPDATE_FAILED | 资料更新失败 | 422 |

#### 内容相关 (CONTENT_*)

| 错误码 | 描述 | HTTP 状态 |
|--------|------|-----------|
| CONTENT_NOT_FOUND | 内容不存在 | 404 |
| CONTENT_ALREADY_EXISTS | 内容已存在 | 409 |
| CONTENT_INVALID_DATA | 内容数据无效 | 400 |
| CONTENT_PUBLISH_FAILED | 发布失败 | 422 |
| CONTENT_DELETE_FAILED | 删除失败 | 422 |

#### 接入相关 (INGEST_*)

| 错误码 | 描述 | HTTP 状态 |
|--------|------|-----------|
| INGEST_WEBHOOK_INVALID | Webhook 签名无效 | 400 |
| INGEST_SOURCE_NOT_FOUND | 接入源不存在 | 404 |
| INGEST_RATE_LIMITED | 接入频率超限 | 429 |
| INGEST_PARSE_FAILED | 内容解析失败 | 422 |
| INGEST_DUPLICATE_CONTENT | 重复内容 | 409 |

#### 系统相关 (SYSTEM_*)

| 错误码 | 描述 | HTTP 状态 |
|--------|------|-----------|
| SYSTEM_INTERNAL_ERROR | 内部服务器错误 | 500 |
| SYSTEM_SERVICE_UNAVAILABLE | 服务暂不可用 | 503 |
| SYSTEM_DATABASE_ERROR | 数据库错误 | 500 |
| SYSTEM_CACHE_ERROR | 缓存错误 | 500 |
| SYSTEM_RATE_LIMIT | 全局限流触发 | 429 |

---

## 4. 认证 API

### 4.1 用户注册

```http
POST /api/v1/auth/register
```

用户注册,创建新账户。

#### 请求参数

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| username | string | 是 | 用户名,3-20 个字符,仅支持字母、数字、下划线 |
| email | string | 是 | 邮箱地址,需符合邮箱格式 |
| password | string | 是 | 密码,至少 8 个字符,需包含大小写字母和数字 |

#### 请求示例

```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

#### 响应示例 (201 Created)

```json
{
  "user": {
    "id": "usr_abc123",
    "username": "johndoe",
    "email": "john@example.com",
    "created_at": "2026-03-19T10:30:00Z"
  },
  "tokens": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 900
  }
}
```

#### 错误响应

| HTTP 状态 | 错误码 | 说明 |
|-----------|--------|------|
| 400 | USER_INVALID_PASSWORD | 密码不符合要求 |
| 409 | USER_EMAIL_EXISTS | 邮箱已被注册 |
| 409 | USER_USERNAME_EXISTS | 用户名已被使用 |

---

### 4.2 用户登录

```http
POST /api/v1/auth/login
```

用户登录,获取访问令牌。

#### 请求参数

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| email | string | 是* | 邮箱地址 |
| username | string | 是* | 用户名 |
| password | string | 是 | 密码 |

*email 和 username 至少提供一个

#### 请求示例

```json
{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

#### 响应示例 (200 OK)

```json
{
  "user": {
    "id": "usr_abc123",
    "username": "johndoe",
    "email": "john@example.com",
    "last_login_at": "2026-03-19T10:30:00Z"
  },
  "tokens": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 900
  }
}
```

#### 错误响应

| HTTP 状态 | 错误码 | 说明 |
|-----------|--------|------|
| 401 | AUTH_INVALID_CREDENTIALS | 用户名/邮箱或密码错误 |
| 429 | SYSTEM_RATE_LIMIT | 登录尝试次数过多 |

---

### 4.3 刷新 Token

```http
POST /api/v1/auth/refresh
```

使用 Refresh Token 获取新的 Access Token。

#### 请求头

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| Authorization | string | 是 | `Bearer {refresh_token}` |

#### 响应示例 (200 OK)

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "expires_in": 900
}
```

#### 错误响应

| HTTP 状态 | 错误码 | 说明 |
|-----------|--------|------|
| 401 | AUTH_TOKEN_EXPIRED | Refresh Token 已过期 |
| 401 | AUTH_TOKEN_REVOKED | Refresh Token 已被撤销 |

---

### 4.4 用户登出

```http
POST /api/v1/auth/logout
```

用户登出,撤销当前 Refresh Token。

#### 请求头

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| Authorization | string | 是 | `Bearer {access_token}` |

#### 响应示例 (204 No Content)

无响应体

#### 错误响应

| HTTP 状态 | 错误码 | 说明 |
|-----------|--------|------|
| 401 | AUTH_UNAUTHORIZED | 未提供认证信息 |

---

## 5. 用户 API

### 5.1 获取当前用户信息

```http
GET /api/v1/users/me
```

获取当前登录用户的详细信息。

#### 请求头

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| Authorization | string | 是 | `Bearer {access_token}` |

#### 响应示例 (200 OK)

```json
{
  "id": "usr_abc123",
  "username": "johndoe",
  "email": "john@example.com",
  "avatar_url": "https://cdn.ainewshub.com/avatars/usr_abc123.jpg",
  "bio": "AI 爱好者,关注前沿技术",
  "role": "user",
  "preferences": {
    "language": "zh-CN",
    "timezone": "Asia/Shanghai",
    "email_notifications": true,
    "theme": "dark"
  },
  "stats": {
    "articles_read": 156,
    "bookmarks_count": 23,
    "following_count": 15
  },
  "created_at": "2026-01-15T08:00:00Z",
  "updated_at": "2026-03-19T10:30:00Z",
  "last_login_at": "2026-03-19T10:30:00Z"
}
```

#### 错误响应

| HTTP 状态 | 错误码 | 说明 |
|-----------|--------|------|
| 401 | AUTH_UNAUTHORIZED | 未登录 |

---

### 5.2 更新用户信息

```http
PUT /api/v1/users/me
```

更新当前登录用户的个人资料。

#### 请求头

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| Authorization | string | 是 | `Bearer {access_token}` |
| Content-Type | string | 是 | `application/json` |

#### 请求参数

| 参数 | 类型 | 必填 | 描述 | 约束 |
|------|------|------|------|------|
| username | string | 否 | 新用户名 | 3-20 个字符,仅支持字母、数字、下划线 |
| avatar_url | string | 否 | 头像 URL | 必须是有效的 URL |
| bio | string | 否 | 个人简介 | 最多 500 个字符 |
| preferences | object | 否 | 用户偏好设置 | 见下表 |

**preferences 对象:**

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| language | string | 否 | 语言代码,如 "zh-CN", "en-US" |
| timezone | string | 否 | 时区标识符 |
| email_notifications | boolean | 否 | 是否接收邮件通知 |
| theme | string | 否 | 主题: "light", "dark", "system" |

#### 请求示例

```json
{
  "bio": "AI 研究者,专注于 LLM 和 Agent 技术",
  "preferences": {
    "language": "zh-CN",
    "theme": "dark",
    "email_notifications": false
  }
}
```

#### 响应示例 (200 OK)

```json
{
  "id": "usr_abc123",
  "username": "johndoe",
  "email": "john@example.com",
  "avatar_url": "https://cdn.ainewshub.com/avatars/usr_abc123.jpg",
  "bio": "AI 研究者,专注于 LLM 和 Agent 技术",
  "role": "user",
  "preferences": {
    "language": "zh-CN",
    "timezone": "Asia/Shanghai",
    "email_notifications": false,
    "theme": "dark"
  },
  "updated_at": "2026-03-19T11:00:00Z"
}
```

#### 错误响应

| HTTP 状态 | 错误码 | 说明 |
|-----------|--------|------|
| 400 | USER_INVALID_EMAIL | 邮箱格式无效 |
| 401 | AUTH_UNAUTHORIZED | 未登录 |
| 409 | USER_USERNAME_EXISTS | 用户名已被使用 |
| 422 | USER_PROFILE_UPDATE_FAILED | 更新失败 |

---

## 6. 内容 API

### 6.1 获取资讯列表

```http
GET /api/v1/articles
```

获取资讯文章列表,支持分页、过滤和排序。

#### 请求参数 (Query)

| 参数 | 类型 | 必填 | 描述 | 默认值 |
|------|------|------|------|--------|
| page | integer | 否 | 页码,从 1 开始 | 1 |
| per_page | integer | 否 | 每页数量,最大 100 | 20 |
| category_id | string | 否 | 分类 ID,过滤特定分类 | - |
| tag | string | 否 | 标签名称,支持多个(逗号分隔) | - |
| status | string | 否 | 文章状态: "published", "draft" (管理员专用) | "published" |
| search | string | 否 | 搜索关键词(标题、内容) | - |
| sort | string | 否 | 排序方式: "created_at", "updated_at", "view_count", "published_at" | "published_at" |
| order | string | 否 | 排序方向: "asc", "desc" | "desc" |
| from_date | string | 否 | 起始日期 (ISO 8601) | - |
| to_date | string | 否 | 结束日期 (ISO 8601) | - |

#### 请求示例

```http
GET /api/v1/articles?page=1&per_page=20&category_id=cat_ai&sort=published_at&order=desc&search=GPT
```

#### 响应示例 (200 OK)

```json
{
  "data": [
    {
      "id": "art_123abc",
      "title": "GPT-5 即将发布:性能提升 10 倍",
      "slug": "gpt-5-release-performance-10x",
      "summary": "OpenAI 宣布 GPT-5 将在 Q2 发布,性能提升 10 倍...",
      "content": "...",
      "cover_image": "https://cdn.ainewshub.com/images/art_123abc.jpg",
      "author": {
        "id": "usr_def456",
        "username": "tech_reporter",
        "avatar_url": "https://cdn.ainewshub.com/avatars/usr_def456.jpg"
      },
      "category": {
        "id": "cat_ai",
        "name": "人工智能",
        "slug": "artificial-intelligence"
      },
      "tags": [
        {"id": "tag_gpt", "name": "GPT", "slug": "gpt"},
        {"id": "tag_openai", "name": "OpenAI", "slug": "openai"}
      ],
      "status": "published",
      "view_count": 1234,
      "like_count": 56,
      "comment_count": 12,
      "published_at": "2026-03-18T08:00:00Z",
      "created_at": "2026-03-18T07:30:00Z",
      "updated_at": "2026-03-19T09:00:00Z"
    }
  ],
  "pagination": {
    "current_page": 1,
    "per_page": 20,
    "total_pages": 10,
    "total_count": 200,
    "has_next": true,
    "has_prev": false
  },
  "meta": {
    "request_id": "req_xyz789",
    "timestamp": "2026-03-19T10:30:00Z"
  }
}
```

#### 错误响应

| HTTP 状态 | 错误码 | 说明 |
|-----------|--------|------|
| 400 | CONTENT_INVALID_DATA | 无效的过滤参数 |
| 401 | AUTH_UNAUTHORIZED | 访问草稿状态需登录 |
| 403 | AUTH_FORBIDDEN | 无权限访问其他用户的草稿 |

---

### 6.2 获取资讯详情

```http
GET /api/v1/articles/{id}
```

获取单篇资讯的完整详情。

#### 路径参数

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| id | string | 是 | 资讯 ID (art_ 前缀) |

#### 请求参数 (Query)

| 参数 | 类型 | 必填 | 描述 | 默认值 |
|------|------|------|------|--------|
| include | string | 否 | 附加数据: "author", "category", "tags", "comments" (逗号分隔) | - |

#### 响应示例 (200 OK)

与列表接口中的文章对象格式相同,包含完整内容字段。

#### 错误响应

| HTTP 状态 | 错误码 | 说明 |
|-----------|--------|------|
| 404 | CONTENT_NOT_FOUND | 资讯不存在或已删除 |
| 403 | AUTH_FORBIDDEN | 无权限查看该状态的内容 |

---

### 6.3 创建资讯 (管理员)

```http
POST /api/v1/articles
```

创建新的资讯文章。需要管理员权限。

#### 请求头

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| Authorization | string | 是 | `Bearer {access_token}` |
| Content-Type | string | 是 | `application/json` |

#### 请求参数

| 参数 | 类型 | 必填 | 描述 | 约束 |
|------|------|------|------|------|
| title | string | 是 | 标题 | 5-200 个字符 |
| content | string | 是 | 正文内容 | 支持 Markdown,最少 100 个字符 |
| summary | string | 否 | 摘要 | 最多 500 个字符,默认自动生成 |
| category_id | string | 是 | 分类 ID | - |
| tag_ids | array | 否 | 标签 ID 数组 | - |
| cover_image | string | 否 | 封面图 URL | 有效的图片 URL |
| status | string | 否 | 状态 | "draft", "published",默认 "draft" |
| published_at | string | 否 | 发布时间 | ISO 8601 格式,仅 status=published 时有效 |
| seo_title | string | 否 | SEO 标题 | 最多 60 个字符 |
| seo_description | string | 否 | SEO 描述 | 最多 160 个字符 |

#### 请求示例

```json
{
  "title": "Claude 4 发布:多模态能力大幅提升",
  "content": "Anthropic 今日发布了 Claude 4...",
  "summary": "Anthropic 发布 Claude 4,在视觉理解和代码生成方面有显著提升",
  "category_id": "cat_ai",
  "tag_ids": ["tag_claude", "tag_anthropic", "tag_multimodal"],
  "cover_image": "https://cdn.ainewshub.com/images/claude4-cover.jpg",
  "status": "published"
}
```

#### 响应示例 (201 Created)

```json
{
  "id": "art_def456",
  "title": "Claude 4 发布:多模态能力大幅提升",
  "slug": "claude-4-release-multimodal",
  "summary": "Anthropic 发布 Claude 4...",
  "content": "Anthropic 今日发布了 Claude 4...",
  "cover_image": "https://cdn.ainewshub.com/images/claude4-cover.jpg",
  "author": {
    "id": "usr_admin001",
    "username": "admin",
    "avatar_url": "..."
  },
  "category": {
    "id": "cat_ai",
    "name": "人工智能",
    "slug": "artificial-intelligence"
  },
  "tags": [
    {"id": "tag_claude", "name": "Claude", "slug": "claude"},
    {"id": "tag_anthropic", "name": "Anthropic", "slug": "anthropic"}
  ],
  "status": "published",
  "view_count": 0,
  "like_count": 0,
  "comment_count": 0,
  "published_at": "2026-03-19T11:30:00Z",
  "created_at": "2026-03-19T11:30:00Z",
  "updated_at": "2026-03-19T11:30:00Z"
}
```

#### 错误响应

| HTTP 状态 | 错误码 | 说明 |
|-----------|--------|------|
| 400 | CONTENT_INVALID_DATA | 内容数据验证失败 |
| 401 | AUTH_UNAUTHORIZED | 未登录 |
| 403 | AUTH_FORBIDDEN | 非管理员无法创建 |
| 404 | CONTENT_NOT_FOUND | 指定的分类或标签不存在 |
| 409 | CONTENT_ALREADY_EXISTS | 标题已存在(同一slug) |

---

### 6.4 更新资讯

```http
PUT /api/v1/articles/{id}
```

更新现有资讯文章。需要管理员权限或文章作者权限。

#### 路径参数

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| id | string | 是 | 资讯 ID |

#### 请求头

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| Authorization | string | 是 | `Bearer {access_token}` |
| Content-Type | string | 是 | `application/json` |

#### 请求参数

与创建接口相同,所有字段均为可选。提供的字段将被更新,未提供的字段保持不变。

额外支持字段:

| 参数 | 类型 | 描述 |
|------|------|------|
| regenerate_slug | boolean | 是否重新生成 slug(标题变更时) |

#### 响应示例 (200 OK)

```json
{
  "id": "art_def456",
  "title": "Claude 4 发布:多模态能力大幅提升(更新)",
  "slug": "claude-4-release-multimodal",
  "summary": "...",
  "content": "...",
  "status": "published",
  "updated_at": "2026-03-19T12:00:00Z"
}
```

#### 错误响应

| HTTP 状态 | 错误码 | 说明 |
|-----------|--------|------|
| 403 | AUTH_FORBIDDEN | 无权限修改此文章 |
| 404 | CONTENT_NOT_FOUND | 文章不存在 |
| 409 | CONTENT_ALREADY_EXISTS | 新标题冲突 |

---

### 6.5 删除资讯

```http
DELETE /api/v1/articles/{id}
```

删除资讯文章。需要管理员权限。

#### 路径参数

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| id | string | 是 | 资讯 ID |

#### 请求头

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| Authorization | string | 是 | `Bearer {access_token}` |

#### 查询参数

| 参数 | 类型 | 必填 | 描述 | 默认值 |
|------|------|------|------|--------|
| permanent | boolean | 否 | 是否永久删除(否则进入回收站) | false |

#### 响应示例 (204 No Content)

无响应体

#### 错误响应

| HTTP 状态 | 错误码 | 说明 |
|-----------|--------|------|
| 401 | AUTH_UNAUTHORIZED | 未登录 |
| 403 | AUTH_FORBIDDEN | 非管理员无法删除 |
| 404 | CONTENT_NOT_FOUND | 文章不存在或已删除 |
| 422 | CONTENT_DELETE_FAILED | 删除失败(有关联数据) |

---

## 7. OpenClaw 接入 API

### 7.1 概述

OpenClaw 是 AI News Hub 的核心接入组件,支持多种内容接入方式:

1. **Webhook 接入**: 实时接收来自内容源的推送
2. **Feed 接入**: 批量拉取 Feed 源内容
3. **API 接入**: 通过 API 主动推送内容

### 7.2 Webhook 接收端点

```http
POST /api/v1/ingest/webhook
```

接收来自外部系统的 Webhook 推送。支持内容创建、更新、删除事件。

#### 认证方式

Webhook 请求必须使用 HMAC-SHA256 签名验证:

```http
X-Webhook-Signature: sha256={signature}
X-Webhook-Id: {webhook_id}
X-Webhook-Timestamp: {unix_timestamp}
```

签名生成方式:
```
signature = HMAC-SHA256(
  webhook_secret,
  timestamp + "." + request_body
)
```

#### 请求头

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| Content-Type | string | 是 | `application/json` |
| X-Webhook-Signature | string | 是 | HMAC-SHA256 签名 |
| X-Webhook-Id | string | 是 | Webhook 唯一标识 |
| X-Webhook-Timestamp | integer | 是 | Unix 时间戳(秒) |
| X-Webhook-Event | string | 是 | 事件类型 |

#### 请求参数

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| event | string | 是 | 事件类型: "content.create", "content.update", "content.delete" |
| source | object | 是 | 来源信息 |
| content | object | 是 | 内容数据 |
| metadata | object | 否 | 附加元数据 |

**source 对象:**

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| id | string | 是 | 来源 ID |
| name | string | 是 | 来源名称 |
| type | string | 是 | 来源类型: "rss", "api", "webhook", "crawler" |
| url | string | 否 | 来源 URL |

**content 对象 (content.create / content.update):**

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| external_id | string | 条件 | 外部系统 ID,用于去重和更新 |
| title | string | 是 | 标题 |
| content | string | 是 | 正文内容 (HTML 或 Markdown) |
| summary | string | 否 | 摘要,不传则自动生成 |
| author | object | 否 | 作者信息 |
| published_at | string | 否 | 原始发布时间 (ISO 8601) |
| url | string | 否 | 原始 URL |
| cover_image | string | 否 | 封面图 URL |
| category | object | 否 | 分类信息 |
| tags | array | 否 | 标签列表 |
| language | string | 否 | 内容语言代码 |

#### 请求示例

```json
{
  "event": "content.create",
  "source": {
    "id": "src_openai_blog",
    "name": "OpenAI Blog",
    "type": "rss",
    "url": "https://openai.com/blog/rss.xml"
  },
  "content": {
    "external_id": "openai_2026_03_18_gpt5",
    "title": "Introducing GPT-5",
    "content": "<p>We are excited to announce GPT-5...</p>",
    "summary": "OpenAI introduces GPT-5 with significant improvements...",
    "author": {
      "name": "OpenAI Team",
      "url": "https://openai.com"
    },
    "published_at": "2026-03-18T10:00:00Z",
    "url": "https://openai.com/blog/gpt-5",
    "cover_image": "https://openai.com/images/gpt5-cover.jpg",
    "category": {
      "name": "Research",
      "slug": "research"
    },
    "tags": ["GPT-5", "LLM", "Research"],
    "language": "en"
  },
  "metadata": {
    "ingest_id": "ing_123456",
    "received_at": "2026-03-19T10:30:00Z"
  }
}
```

#### 响应示例 (202 Accepted)

```json
{
  "success": true,
  "data": {
    "ingest_id": "ing_789abc",
    "content_id": "art_new123",
    "status": "processing",
    "message": "Content accepted for processing"
  },
  "meta": {
    "request_id": "req_xyz789",
    "timestamp": "2026-03-19T10:30:01Z"
  }
}
```

#### 错误响应

| HTTP 状态 | 错误码 | 说明 |
|-----------|--------|------|
| 400 | INGEST_WEBHOOK_INVALID | Webhook 签名验证失败 |
| 400 | CONTENT_INVALID_DATA | 请求数据格式错误 |
| 401 | AUTH_UNAUTHORIZED | Webhook 认证失败 |
| 409 | INGEST_DUPLICATE_CONTENT | 重复内容(external_id 已存在) |
| 422 | INGEST_PARSE_FAILED | 内容解析失败 |
| 429 | INGEST_RATE_LIMITED | 请求频率超限 |

---

### 7.3 Feed 批量接入

```http
POST /api/v1/ingest/feed
```

主动拉取 Feed 源内容。用于批量导入 RSS/Atom Feed、JSON Feed 等。

#### 认证方式

需要管理员 API Key:

```http
Authorization: Bearer {admin_api_key}
```

#### 请求头

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| Authorization | string | 是 | `Bearer {admin_api_key}` |
| Content-Type | string | 是 | `application/json` |

#### 请求参数

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| source_id | string | 条件 | 已配置的接入源 ID,与下面参数二选一 |
| source | object | 条件 | 临时接入源配置,不保存到数据库 |
| options | object | 否 | 拉取选项 |

**source 对象(临时配置):**

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| name | string | 是 | 来源名称 |
| type | string | 是 | "rss", "atom", "json_feed", "sitemap" |
| url | string | 是 | Feed URL |
| category_mapping | object | 否 | 分类映射规则 |
| default_category_id | string | 否 | 默认分类 ID |

**options 对象:**

| 参数 | 类型 | 必填 | 描述 | 默认值 |
|------|------|------|------|--------|
| max_items | integer | 否 | 最大拉取数量 | 100 |
| since | string | 否 | 只拉取该时间之后的内容 | - |
| dry_run | boolean | 否 | 仅模拟,不实际保存 | false |
| auto_publish | boolean | 否 | 自动发布 | false |
| deduplication | string | 否 | 去重策略: "url", "title", "content_hash" | "url" |

#### 请求示例

```json
{
  "source": {
    "name": "TechCrunch AI",
    "type": "rss",
    "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "default_category_id": "cat_ai"
  },
  "options": {
    "max_items": 50,
    "since": "2026-03-01T00:00:00Z",
    "dry_run": false,
    "auto_publish": false,
    "deduplication": "url"
  }
}
```

#### 响应示例 (202 Accepted)

```json
{
  "success": true,
  "data": {
    "job_id": "job_abc123",
    "status": "queued",
    "source": {
      "name": "TechCrunch AI",
      "type": "rss",
      "url": "https://techcrunch.com/..."
    },
    "options": {
      "max_items": 50,
      "dry_run": false
    },
    "queued_at": "2026-03-19T10:30:00Z",
    "estimated_completion": "2026-03-19T10:32:00Z"
  },
  "meta": {
    "request_id": "req_def456",
    "timestamp": "2026-03-19T10:30:00Z"
  }
}
```

#### 错误响应

| HTTP 状态 | 错误码 | 说明 |
|-----------|--------|------|
| 400 | INGEST_PARSE_FAILED | Feed URL 无法解析 |
| 401 | AUTH_UNAUTHORIZED | API Key 无效 |
| 403 | AUTH_FORBIDDEN | 无管理员权限 |
| 404 | INGEST_SOURCE_NOT_FOUND | 指定的 source_id 不存在 |
| 422 | INGEST_PARSE_FAILED | Feed 格式不兼容 |

---

### 7.4 接入状态查询

```http
GET /api/v1/ingest/status
```

查询内容接入任务的状态和统计信息。

#### 认证方式

需要管理员 API Key 或登录用户(查看自己的任务)。

#### 请求头

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| Authorization | string | 是 | `Bearer {token}` |

#### 请求参数 (Query)

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| job_id | string | 条件 | 查询特定任务 |
| source_id | string | 条件 | 查询特定来源的所有任务 |
| status | string | 否 | 过滤状态: "pending", "running", "completed", "failed" |
| from_date | string | 否 | 起始日期 |
| to_date | string | 否 | 结束日期 |
| page | integer | 否 | 页码,默认 1 |
| per_page | integer | 否 | 每页数量,默认 20 |

#### 响应示例 (200 OK)

**单个任务详情 (提供 job_id):**

```json
{
  "data": {
    "job_id": "job_abc123",
    "type": "feed_import",
    "status": "completed",
    "source": {
      "id": "src_techcrunch",
      "name": "TechCrunch AI",
      "type": "rss"
    },
    "options": {
      "max_items": 50,
      "auto_publish": false
    },
    "progress": {
      "total_items": 50,
      "processed": 50,
      "succeeded": 48,
      "failed": 2,
      "percentage": 100
    },
    "results": {
      "created": 30,
      "updated": 18,
      "skipped": 2,
      "failed": 2
    },
    "errors": [
      {
        "index": 15,
        "url": "https://techcrunch.com/...",
        "error": "内容解析失败",
        "code": "INGEST_PARSE_FAILED"
      }
    ],
    "timings": {
      "queued_at": "2026-03-19T10:30:00Z",
      "started_at": "2026-03-19T10:30:05Z",
      "completed_at": "2026-03-19T10:35:20Z",
      "duration_seconds": 315
    },
    "triggered_by": {
      "user_id": "usr_admin001",
      "username": "admin"
    }
  },
  "meta": {
    "request_id": "req_ghi789",
    "timestamp": "2026-03-19T12:00:00Z"
  }
}
```

**任务列表 (不提供 job_id):**

```json
{
  "data": [
    {
      "job_id": "job_abc123",
      "type": "feed_import",
      "status": "completed",
      "source_name": "TechCrunch AI",
      "progress": {
        "total": 50,
        "processed": 50,
        "percentage": 100
      },
      "created_at": "2026-03-19T10:30:00Z"
    }
  ],
  "pagination": {
    "current_page": 1,
    "per_page": 20,
    "total_pages": 5,
    "total_count": 100
  }
}
```

#### 错误响应

| HTTP 状态 | 错误码 | 说明 |
|-----------|--------|------|
| 401 | AUTH_UNAUTHORIZED | 未登录 |
| 403 | AUTH_FORBIDDEN | 无权限查看此任务 |
| 404 | INGEST_SOURCE_NOT_FOUND | 指定的 source_id 不存在 |

---

## 8. AI API (预留)

以下 API 为 AI 功能预留接口,将在后续版本中实现。

### 8.1 智能问答

```http
POST /api/v1/ai/query
```

基于资讯内容的智能问答系统。

#### 功能规划

- 基于向量检索的语义搜索
- 支持多轮对话上下文
- 答案引用原文出处
- 支持自定义知识库范围

#### 请求/响应格式

(待定)

---

### 8.2 向量化接口

```http
POST /api/v1/ai/embed
```

将文本内容转换为向量表示。

#### 功能规划

- 支持多种嵌入模型
- 批量处理
- 向量存储到 Qdrant
- 支持自定义元数据

#### 请求/响应格式

(待定)

---

## 9. Rate Limiting 策略

### 9.1 限流规则

API 采用分级限流策略:

#### 公共接口 (无需认证)

| 端点 | 限流规则 | 说明 |
|------|----------|------|
| GET /api/v1/articles | 100/分钟/IP | 资讯列表 |
| GET /api/v1/articles/{id} | 60/分钟/IP | 资讯详情 |

#### 认证接口 (普通用户)

| 端点 | 限流规则 | 说明 |
|------|----------|------|
| POST /api/v1/auth/* | 5/分钟/用户 | 登录相关 |
| GET /api/v1/users/me | 60/分钟/用户 | 用户信息 |
| PUT /api/v1/users/me | 10/分钟/用户 | 更新资料 |

#### 管理接口 (管理员)

| 端点 | 限流规则 | 说明 |
|------|----------|------|
| POST /api/v1/articles | 100/小时 | 创建资讯 |
| PUT /api/v1/articles/* | 200/小时 | 更新资讯 |
| DELETE /api/v1/articles/* | 50/小时 | 删除资讯 |

#### OpenClaw 接入接口

| 端点 | 限流规则 | 说明 |
|------|----------|------|
| POST /api/v1/ingest/webhook | 1000/小时/Source | Webhook 接收 |
| POST /api/v1/ingest/feed | 10/小时 | Feed 拉取 |
| GET /api/v1/ingest/status | 60/分钟 | 状态查询 |

### 9.2 限流响应

当触发限流时,返回 429 状态码:

```json
{
  "error": {
    "code": "SYSTEM_RATE_LIMIT",
    "message": "Rate limit exceeded. Try again in 45 seconds.",
    "details": {
      "limit": 100,
      "window": "1m",
      "retry_after": 45
    },
    "request_id": "req_rate123",
    "timestamp": "2026-03-19T10:30:00Z"
  }
}
```

响应头包含限流信息:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1710845445
Retry-After: 45
```

### 9.3 限流豁免

以下情况可申请限流豁免:

1. **内部服务**: 内部微服务间的调用
2. **合作伙伴**: 签署了 SLA 的合作伙伴
3. **批量导入**: 历史数据迁移任务

申请方式: 联系管理员申请 API Key 白名单

---

## 10. 附录

### 10.1 标准响应格式

#### 成功响应

列表响应:
```json
{
  "data": [...],
  "pagination": {
    "current_page": 1,
    "per_page": 20,
    "total_pages": 10,
    "total_count": 200
  },
  "meta": {...}
}
```

单对象响应:
```json
{
  "data": {...},
  "meta": {...}
}
```

#### 错误响应

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "...",
    "details": {...},
    "request_id": "...",
    "timestamp": "..."
  }
}
```

### 10.2 数据类型定义

#### 时间戳格式

所有时间戳采用 ISO 8601 格式:
- 格式: `YYYY-MM-DDTHH:mm:ssZ`
- 示例: `2026-03-19T10:30:00Z`
- 时区: 始终使用 UTC

#### ID 格式

- 用户 ID: `usr_{alphanumeric}`  
- 文章 ID: `art_{alphanumeric}`
- 分类 ID: `cat_{alphanumeric}`
- 标签 ID: `tag_{alphanumeric}`
- 任务 ID: `job_{alphanumeric}`
- 来源 ID: `src_{alphanumeric}`

ID 使用 nanoid 生成,长度 12-16 位。

#### 枚举值

**文章状态 (status):**
- `draft`: 草稿
- `published`: 已发布
- `archived`: 已归档
- `deleted`: 已删除(软删除)

**用户角色 (role):**
- `user`: 普通用户
- `editor`: 编辑
- `admin`: 管理员

**接入类型 (source_type):**
- `rss`: RSS Feed
- `atom`: Atom Feed
- `json_feed`: JSON Feed
- `api`: REST API
- `webhook`: Webhook
- `crawler`: 爬虫

### 10.3 分页规范

#### 请求参数

- `page`: 页码,从 1 开始
- `per_page`: 每页数量,默认 20,最大 100

#### 响应结构

```json
{
  "pagination": {
    "current_page": 1,
    "per_page": 20,
    "total_pages": 10,
    "total_count": 200,
    "has_next": true,
    "has_prev": false
  }
}
```

#### 游标分页 (备选)

对于大数据集,支持游标分页:

```http
GET /api/v1/articles?cursor=eyJpZCI6ImFydF94eXoifQ&per_page=20
```

响应包含:
```json
{
  "pagination": {
    "cursor": "eyJpZCI6ImFydF9hYmMifQ",
    "has_more": true
  }
}
```

### 10.4 Webhook 签名验证示例

#### Node.js

```javascript
const crypto = require('crypto');

function verifyWebhookSignature(payload, signature, secret) {
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(payload, 'utf8')
    .digest('hex');
  
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expectedSignature)
  );
}

// 使用示例
app.post('/webhook', (req, res) => {
  const signature = req.headers['x-webhook-signature'];
  const payload = JSON.stringify(req.body);
  
  if (!verifyWebhookSignature(payload, signature, WEBHOOK_SECRET)) {
    return res.status(400).json({ error: 'Invalid signature' });
  }
  
  // 处理 webhook
  processWebhook(req.body);
  res.status(202).json({ success: true });
});
```

#### Python

```python
import hmac
import hashlib
import json

from flask import Flask, request, jsonify

app = Flask(__name__)
WEBHOOK_SECRET = "your-webhook-secret"

def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

@app.route('/webhook', methods=['POST'])
def webhook():
    signature = request.headers.get('X-Webhook-Signature', '').replace('sha256=', '')
    payload = request.get_data()
    
    if not verify_webhook_signature(payload, signature, WEBHOOK_SECRET):
        return jsonify({'error': 'Invalid signature'}), 400
    
    data = request.get_json()
    process_webhook(data)
    
    return jsonify({'success': True}), 202

if __name__ == '__main__':
    app.run(debug=True)
```

---

## 11. 变更日志

### 版本历史

#### v1.0.0 (2026-03-19)

初始版本发布,包含:

- RESTful API 基础框架
- 认证 API (注册、登录、刷新、登出)
- 用户 API (用户信息管理)
- 内容 API (资讯 CRUD)
- OpenClaw 接入 API (Webhook、Feed、状态查询)
- AI API 预留接口
- 完整的错误处理和限流策略

---

## 12. 联系方式

如有 API 相关问题或建议,请通过以下方式联系我们:

- **技术支持邮箱**: api-support@ainewshub.com
- **开发者论坛**: https://dev.ainewshub.com
- **API 状态页**: https://status.ainewshub.com
- **文档反馈**: 本文档底部"反馈"按钮

---

**文档维护**: AI News Hub 技术团队  
**最后更新**: 2026-03-19  
**文档版本**: v1.0.0
