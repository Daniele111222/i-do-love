# 数据库设计文档

> 版本: 1.0.0  
> 更新日期: 2026-03-19  
> 文档状态: 草稿

---

## 1. 概述

### 1.1 数据库选型

AI News Hub 采用多数据库架构:

#### PostgreSQL (主数据库)

- **用途**: 结构化数据存储
- **版本**: PostgreSQL 16+
- **选择理由**:
  - 成熟稳定,ACID 事务支持
  - 优秀的 JSON/JSONB 支持,灵活存储半结构化数据
  - 丰富的数据类型和索引类型
  - 良好的全文搜索能力
  - 完善的权限管理和扩展生态

#### Qdrant (向量数据库)

- **用途**: 向量数据存储和相似度搜索
- **版本**: Qdrant 1.8+
- **选择理由**:
  - 高性能向量相似度搜索
  - 支持过滤搜索(Filtered Search)
  - 分布式部署支持
  - 与 PostgreSQL 形成互补

#### Redis (缓存层)

- **用途**: 会话缓存、热点数据缓存、限流计数
- **版本**: Redis 7+
- **选择理由**:
  - 高性能内存存储
  - 丰富的数据结构
  - 内置限流原语(Redis Cell)

### 1.2 数据库架构图

```
┌─────────────────────────────────────────────────────────────┐
│                         AI News Hub                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Client    │    │   Client    │    │   Client    │     │
│  │   (Web)     │    │   (App)     │    │   (API)     │     │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘     │
│         │                  │                  │             │
│         └──────────────────┼──────────────────┘             │
│                            │                                │
│                   ┌────────▼────────┐                       │
│                   │   API Gateway   │                       │
│                   │   (Kong/AWS)    │                       │
│                   └────────┬────────┘                       │
│                            │                                │
│  ┌─────────────────────────┼─────────────────────────┐     │
│  │                         │                         │     │
│  ▼                         ▼                         ▼     │
│ ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│ │  PostgreSQL │    │   Qdrant    │    │    Redis    │     │
│ │  (主数据)   │    │  (向量数据)  │    │   (缓存)    │     │
│ └─────────────┘    └─────────────┘    └─────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 命名规范

#### 表名规范

- 使用小写字母和下划线(snake_case)
- 使用复数形式: `users`, `articles`
- 关联表使用双方表名: `article_tags`

#### 字段名规范

- 使用小写字母和下划线
- 主键统一使用 `id`
- 外键格式: `{table}_id`, 如 `user_id`
- 时间戳字段: `created_at`, `updated_at`, `deleted_at`
- 布尔字段前缀: `is_`, `has_`, `can_`, 如 `is_active`

#### 索引命名规范

- 主键: `pk_{table}`
- 唯一索引: `uk_{table}_{field}`
- 普通索引: `idx_{table}_{field}`
- 复合索引: `idx_{table}_{field1}_{field2}`
- 全文索引: `ft_{table}_{field}`

---

## 2. PostgreSQL 表设计

### 2.1 用户表 (users)

存储平台用户的基本信息。

#### 表结构

```sql
CREATE TABLE users (
    -- 主键
    id VARCHAR(24) PRIMARY KEY,
    
    -- 基本信息
    username VARCHAR(20) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    
    -- 个人资料
    avatar_url VARCHAR(500),
    bio TEXT,
    
    -- 角色和状态
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- 偏好设置 (JSONB)
    preferences JSONB DEFAULT '{}',
    
    -- 统计信息 (JSONB)
    stats JSONB DEFAULT '{}',
    
    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login_at TIMESTAMPTZ,
    deleted_at TIMESTAMPTZ,
    
    -- 约束
    CONSTRAINT chk_username_format CHECK (username ~ '^[a-zA-Z0-9_]{3,20}$'),
    CONSTRAINT chk_email_format CHECK (email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT chk_role CHECK (role IN ('user', 'editor', 'admin'))
);
```

#### 字段说明

| 字段名 | 类型 | 可空 | 默认值 | 描述 |
|--------|------|------|--------|------|
| id | VARCHAR(24) | NO | - | 主键,nanoid 生成 |
| username | VARCHAR(20) | NO | - | 用户名,3-20 字符,字母数字下划线 |
| email | VARCHAR(255) | NO | - | 邮箱地址,唯一 |
| password_hash | VARCHAR(255) | NO | - | bcrypt 哈希后的密码 |
| avatar_url | VARCHAR(500) | YES | NULL | 头像图片 URL |
| bio | TEXT | YES | NULL | 个人简介 |
| role | VARCHAR(20) | NO | 'user' | 角色: user/editor/admin |
| is_active | BOOLEAN | NO | TRUE | 账号是否激活 |
| is_email_verified | BOOLEAN | NO | FALSE | 邮箱是否验证 |
| preferences | JSONB | NO | {} | 用户偏好设置 |
| stats | JSONB | NO | {} | 用户统计数据 |
| created_at | TIMESTAMPTZ | NO | NOW() | 创建时间 |
| updated_at | TIMESTAMPTZ | NO | NOW() | 更新时间 |
| last_login_at | TIMESTAMPTZ | YES | NULL | 最后登录时间 |
| deleted_at | TIMESTAMPTZ | YES | NULL | 软删除时间 |

#### 索引设计

```sql
-- 主键
ALTER TABLE users ADD CONSTRAINT pk_users PRIMARY KEY (id);

-- 唯一索引
CREATE UNIQUE INDEX uk_users_username ON users(username) WHERE deleted_at IS NULL;
CREATE UNIQUE INDEX uk_users_email ON users(email) WHERE deleted_at IS NULL;

-- 普通索引
CREATE INDEX idx_users_role ON users(role) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_is_active ON users(is_active) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_created_at ON users(created_at DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_last_login_at ON users(last_login_at DESC) WHERE deleted_at IS NULL;

-- 部分索引(软删除)
CREATE INDEX idx_users_deleted_at ON users(deleted_at) WHERE deleted_at IS NOT NULL;

-- GIN 索引(JSONB 查询)
CREATE INDEX idx_users_preferences_gin ON users USING GIN(preferences);
CREATE INDEX idx_users_stats_gin ON users USING GIN(stats);
```

#### 外键关系

用户表无外键(作为被引用表),是以下表的外键引用目标:

- `articles.author_id` -> `users.id`
- `ingest_logs.created_by` -> `users.id`
- `refresh_tokens.user_id` -> `users.id`

---

### 2.2 资讯表 (articles)

存储平台资讯文章内容。

#### 表结构

```sql
CREATE TABLE articles (
    -- 主键
    id VARCHAR(24) PRIMARY KEY,
    
    -- 基本信息
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(220) NOT NULL,
    summary TEXT,
    content TEXT NOT NULL,
    
    -- 媒体
    cover_image VARCHAR(500),
    
    -- 作者和归属
    author_id VARCHAR(24) NOT NULL,
    source_name VARCHAR(100),
    source_url VARCHAR(500),
    
    -- 分类和标签
    category_id VARCHAR(24),
    tags JSONB DEFAULT '[]',
    
    -- 状态
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    
    -- SEO
    seo_title VARCHAR(60),
    seo_description VARCHAR(160),
    
    -- 接入信息
    ingest_source_id VARCHAR(24),
    ingest_metadata JSONB DEFAULT '{}',
    
    -- 统计
    view_count INTEGER NOT NULL DEFAULT 0,
    like_count INTEGER NOT NULL DEFAULT 0,
    comment_count INTEGER NOT NULL DEFAULT 0,
    share_count INTEGER NOT NULL DEFAULT 0,
    
    -- 时间戳
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    
    -- 约束
    CONSTRAINT chk_article_status CHECK (status IN ('draft', 'published', 'archived', 'deleted')),
    CONSTRAINT chk_article_slug CHECK (slug ~ '^[a-z0-9-]+$')
);
```

#### 字段说明

| 字段名 | 类型 | 可空 | 默认值 | 描述 |
|--------|------|------|--------|------|
| id | VARCHAR(24) | NO | - | 主键 |
| title | VARCHAR(200) | NO | - | 标题,5-200 字符 |
| slug | VARCHAR(220) | NO | - | URL 友好的标识符 |
| summary | TEXT | YES | NULL | 摘要,最多 500 字符 |
| content | TEXT | NO | - | 正文内容,支持 Markdown/HTML |
| cover_image | VARCHAR(500) | YES | NULL | 封面图 URL |
| author_id | VARCHAR(24) | NO | - | 作者用户 ID |
| source_name | VARCHAR(100) | YES | NULL | 原始来源名称 |
| source_url | VARCHAR(500) | YES | NULL | 原始来源 URL |
| category_id | VARCHAR(24) | YES | NULL | 分类 ID |
| tags | JSONB | NO | [] | 标签列表 |
| status | VARCHAR(20) | NO | 'draft' | 状态 |
| seo_title | VARCHAR(60) | YES | NULL | SEO 标题 |
| seo_description | VARCHAR(160) | YES | NULL | SEO 描述 |
| ingest_source_id | VARCHAR(24) | YES | NULL | 接入源 ID |
| ingest_metadata | JSONB | NO | {} | 接入元数据 |
| view_count | INTEGER | NO | 0 | 浏览次数 |
| like_count | INTEGER | NO | 0 | 点赞次数 |
| comment_count | INTEGER | NO | 0 | 评论数 |
| share_count | INTEGER | NO | 0 | 分享次数 |
| published_at | TIMESTAMPTZ | YES | NULL | 发布时间 |
| created_at | TIMESTAMPTZ | NO | NOW() | 创建时间 |
| updated_at | TIMESTAMPTZ | NO | NOW() | 更新时间 |
| deleted_at | TIMESTAMPTZ | YES | NULL | 软删除时间 |

#### 索引设计

```sql
-- 主键
ALTER TABLE articles ADD CONSTRAINT pk_articles PRIMARY KEY (id);

-- 唯一索引
CREATE UNIQUE INDEX uk_articles_slug ON articles(slug) WHERE deleted_at IS NULL;

-- 普通索引
CREATE INDEX idx_articles_status ON articles(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_articles_author_id ON articles(author_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_articles_category_id ON articles(category_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_articles_ingest_source_id ON articles(ingest_source_id) WHERE deleted_at IS NULL;

-- 时间索引
CREATE INDEX idx_articles_published_at ON articles(published_at DESC) WHERE status = 'published' AND deleted_at IS NULL;
CREATE INDEX idx_articles_created_at ON articles(created_at DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_articles_updated_at ON articles(updated_at DESC) WHERE deleted_at IS NULL;

-- 统计字段索引(用于排序)
CREATE INDEX idx_articles_view_count ON articles(view_count DESC) WHERE status = 'published' AND deleted_at IS NULL;
CREATE INDEX idx_articles_like_count ON articles(like_count DESC) WHERE status = 'published' AND deleted_at IS NULL;

-- 全文搜索索引
CREATE INDEX idx_articles_title_search ON articles USING gin(to_tsvector('simple', title));
CREATE INDEX idx_articles_content_search ON articles USING gin(to_tsvector('simple', content));

-- 组合索引
CREATE INDEX idx_articles_status_category ON articles(status, category_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_articles_status_published_at ON articles(status, published_at DESC) WHERE deleted_at IS NULL;

-- 软删除索引
CREATE INDEX idx_articles_deleted_at ON articles(deleted_at) WHERE deleted_at IS NOT NULL;

-- GIN 索引(JSONB)
CREATE INDEX idx_articles_tags_gin ON articles USING GIN(tags);
CREATE INDEX idx_articles_ingest_metadata_gin ON articles USING GIN(ingest_metadata);
```

#### 外键关系

```sql
-- 作者外键
ALTER TABLE articles 
    ADD CONSTRAINT fk_articles_author 
    FOREIGN KEY (author_id) 
    REFERENCES users(id) 
    ON DELETE RESTRICT 
    ON UPDATE CASCADE;

-- 分类外键
ALTER TABLE articles 
    ADD CONSTRAINT fk_articles_category 
    FOREIGN KEY (category_id) 
    REFERENCES categories(id) 
    ON DELETE SET NULL 
    ON UPDATE CASCADE;

-- 接入源外键
ALTER TABLE articles 
    ADD CONSTRAINT fk_articles_ingest_source 
    FOREIGN KEY (ingest_source_id) 
    REFERENCES ingest_sources(id) 
    ON DELETE SET NULL 
    ON UPDATE CASCADE;
```

---

### 2.3 分类表 (categories)

存储资讯分类信息。

#### 表结构

```sql
CREATE TABLE categories (
    -- 主键
    id VARCHAR(24) PRIMARY KEY,
    
    -- 基本信息
    name VARCHAR(50) NOT NULL,
    slug VARCHAR(60) NOT NULL,
    description TEXT,
    
    -- 层级
    parent_id VARCHAR(24),
    level INTEGER NOT NULL DEFAULT 0,
    path VARCHAR(500),
    
    -- 媒体
    icon VARCHAR(500),
    cover_image VARCHAR(500),
    
    -- SEO
    seo_title VARCHAR(60),
    seo_description VARCHAR(160),
    
    -- 状态
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    sort_order INTEGER NOT NULL DEFAULT 0,
    
    -- 统计
    article_count INTEGER NOT NULL DEFAULT 0,
    
    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    
    -- 约束
    CONSTRAINT chk_category_slug CHECK (slug ~ '^[a-z0-9-]+$'),
    CONSTRAINT chk_category_level CHECK (level >= 0 AND level <= 3)
);
```

#### 字段说明

| 字段名 | 类型 | 可空 | 默认值 | 描述 |
|--------|------|------|--------|------|
| id | VARCHAR(24) | NO | - | 主键 |
| name | VARCHAR(50) | NO | - | 分类名称 |
| slug | VARCHAR(60) | NO | - | URL 标识符 |
| description | TEXT | YES | NULL | 分类描述 |
| parent_id | VARCHAR(24) | YES | NULL | 父分类 ID |
| level | INTEGER | NO | 0 | 层级深度(0-3) |
| path | VARCHAR(500) | YES | NULL | 层级路径 |
| icon | VARCHAR(500) | YES | NULL | 图标 URL |
| cover_image | VARCHAR(500) | YES | NULL | 封面图 URL |
| seo_title | VARCHAR(60) | YES | NULL | SEO 标题 |
| seo_description | VARCHAR(160) | YES | NULL | SEO 描述 |
| is_active | BOOLEAN | NO | TRUE | 是否启用 |
| sort_order | INTEGER | NO | 0 | 排序序号 |
| article_count | INTEGER | NO | 0 | 文章数量统计 |
| created_at | TIMESTAMPTZ | NO | NOW() | 创建时间 |
| updated_at | TIMESTAMPTZ | NO | NOW() | 更新时间 |
| deleted_at | TIMESTAMPTZ | YES | NULL | 软删除时间 |

#### 索引设计

```sql
-- 主键
ALTER TABLE categories ADD CONSTRAINT pk_categories PRIMARY KEY (id);

-- 唯一索引
CREATE UNIQUE INDEX uk_categories_slug ON categories(slug) WHERE deleted_at IS NULL;

-- 层级索引
CREATE INDEX idx_categories_parent_id ON categories(parent_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_categories_level ON categories(level) WHERE deleted_at IS NULL;

-- 状态索引
CREATE INDEX idx_categories_is_active ON categories(is_active) WHERE deleted_at IS NULL;
CREATE INDEX idx_categories_sort_order ON categories(sort_order) WHERE deleted_at IS NULL AND is_active = TRUE;

-- 时间索引
CREATE INDEX idx_categories_created_at ON categories(created_at DESC) WHERE deleted_at IS NULL;

-- 软删除索引
CREATE INDEX idx_categories_deleted_at ON categories(deleted_at) WHERE deleted_at IS NOT NULL;
```

#### 外键关系

```sql
-- 自引用外键(层级)
ALTER TABLE categories 
    ADD CONSTRAINT fk_categories_parent 
    FOREIGN KEY (parent_id) 
    REFERENCES categories(id) 
    ON DELETE SET NULL 
    ON UPDATE CASCADE;
```

#### 示例数据

```sql
-- 插入示例分类
INSERT INTO categories (id, name, slug, description, level, sort_order) VALUES
('cat_ai', '人工智能', 'artificial-intelligence', '人工智能相关资讯', 0, 1),
('cat_llm', '大语言模型', 'large-language-models', 'LLM 技术资讯', 1, 1),
('cat_agent', '智能体', 'ai-agents', 'AI Agent 相关资讯', 1, 2),
('cat_robotics', '机器人', 'robotics', '机器人技术', 0, 2),
('cat_research', '研究论文', 'research-papers', '学术论文解读', 0, 3);
```

---

### 2.4 标签表 (tags)

存储资讯标签信息。

#### 表结构

```sql
CREATE TABLE tags (
    -- 主键
    id VARCHAR(24) PRIMARY KEY,
    
    -- 基本信息
    name VARCHAR(50) NOT NULL,
    slug VARCHAR(60) NOT NULL,
    description TEXT,
    
    -- 统计
    article_count INTEGER NOT NULL DEFAULT 0,
    
    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    
    -- 约束
    CONSTRAINT chk_tag_slug CHECK (slug ~ '^[a-z0-9-]+$')
);
```

#### 索引设计

```sql
-- 主键
ALTER TABLE tags ADD CONSTRAINT pk_tags PRIMARY KEY (id);

-- 唯一索引
CREATE UNIQUE INDEX uk_tags_slug ON tags(slug) WHERE deleted_at IS NULL;

-- 普通索引
CREATE INDEX idx_tags_name ON tags(name) WHERE deleted_at IS NULL;
CREATE INDEX idx_tags_article_count ON tags(article_count DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_tags_created_at ON tags(created_at DESC) WHERE deleted_at IS NULL;

-- 软删除索引
CREATE INDEX idx_tags_deleted_at ON tags(deleted_at) WHERE deleted_at IS NOT NULL;
```

---

### 2.5 资讯标签关联表 (article_tags)

关联资讯和标签的多对多关系。

#### 表结构

```sql
CREATE TABLE article_tags (
    -- 关联字段
    article_id VARCHAR(24) NOT NULL,
    tag_id VARCHAR(24) NOT NULL,
    
    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- 主键(复合)
    PRIMARY KEY (article_id, tag_id)
);
```

#### 索引设计

```sql
-- 主键已创建 (article_id, tag_id)

-- 反向查询索引
CREATE INDEX idx_article_tags_tag_id ON article_tags(tag_id);

-- 时间索引
CREATE INDEX idx_article_tags_created_at ON article_tags(created_at);
```

#### 外键关系

```sql
-- 外键: 文章
ALTER TABLE article_tags 
    ADD CONSTRAINT fk_article_tags_article 
    FOREIGN KEY (article_id) 
    REFERENCES articles(id) 
    ON DELETE CASCADE 
    ON UPDATE CASCADE;

-- 外键: 标签
ALTER TABLE article_tags 
    ADD CONSTRAINT fk_article_tags_tag 
    FOREIGN KEY (tag_id) 
    REFERENCES tags(id) 
    ON DELETE CASCADE 
    ON UPDATE CASCADE;
```

---

### 2.6 接入源表 (ingest_sources)

存储内容接入源的配置信息。

#### 表结构

```sql
CREATE TABLE ingest_sources (
    -- 主键
    id VARCHAR(24) PRIMARY KEY,
    
    -- 基本信息
    name VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- 接入类型和配置
    source_type VARCHAR(20) NOT NULL,
    source_config JSONB NOT NULL DEFAULT '{}',
    
    -- 内容映射配置
    field_mapping JSONB DEFAULT '{}',
    category_mapping JSONB DEFAULT '{}',
    default_category_id VARCHAR(24),
    
    -- 认证信息 (加密存储)
    credentials JSONB,
    
    -- 调度配置
    schedule_type VARCHAR(20) DEFAULT 'manual',
    schedule_config JSONB DEFAULT '{}',
    
    -- 状态
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_ingest_at TIMESTAMPTZ,
    last_ingest_status VARCHAR(20),
    last_error_message TEXT,
    
    -- 统计
    total_ingested INTEGER NOT NULL DEFAULT 0,
    total_failed INTEGER NOT NULL DEFAULT 0,
    
    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by VARCHAR(24),
    
    -- 约束
    CONSTRAINT chk_source_type CHECK (source_type IN ('rss', 'atom', 'json_feed', 'api', 'webhook', 'crawler', 'sitemap')),
    CONSTRAINT chk_schedule_type CHECK (schedule_type IN ('manual', 'interval', 'cron', 'webhook')),
    CONSTRAINT chk_last_ingest_status CHECK (last_ingest_status IN ('success', 'partial', 'failed', 'running'))
);
```

#### 字段说明

| 字段名 | 类型 | 可空 | 默认值 | 描述 |
|--------|------|------|--------|------|
| id | VARCHAR(24) | NO | - | 主键 |
| name | VARCHAR(100) | NO | - | 接入源名称 |
| description | TEXT | YES | NULL | 描述 |
| source_type | VARCHAR(20) | NO | - | 类型: rss/atom/json_feed/api/webhook/crawler/sitemap |
| source_config | JSONB | NO | {} | 接入配置 |
| field_mapping | JSONB | YES | {} | 字段映射 |
| category_mapping | JSONB | YES | {} | 分类映射 |
| default_category_id | VARCHAR(24) | YES | NULL | 默认分类 |
| credentials | JSONB | YES | NULL | 认证信息(加密) |
| schedule_type | VARCHAR(20) | YES | 'manual' | 调度类型 |
| schedule_config | JSONB | YES | {} | 调度配置 |
| is_active | BOOLEAN | NO | TRUE | 是否启用 |
| last_ingest_at | TIMESTAMPTZ | YES | NULL | 最后接入时间 |
| last_ingest_status | VARCHAR(20) | YES | NULL | 最后接入状态 |
| last_error_message | TEXT | YES | NULL | 最后错误信息 |
| total_ingested | INTEGER | NO | 0 | 总计接入数 |
| total_failed | INTEGER | NO | 0 | 总计失败数 |
| created_at | TIMESTAMPTZ | NO | NOW() | 创建时间 |
| updated_at | TIMESTAMPTZ | NO | NOW() | 更新时间 |
| created_by | VARCHAR(24) | YES | NULL | 创建者用户 ID |

#### 索引设计

```sql
-- 主键
ALTER TABLE ingest_sources ADD CONSTRAINT pk_ingest_sources PRIMARY KEY (id);

-- 普通索引
CREATE INDEX idx_ingest_sources_type ON ingest_sources(source_type);
CREATE INDEX idx_ingest_sources_is_active ON ingest_sources(is_active);
CREATE INDEX idx_ingest_sources_default_category ON ingest_sources(default_category_id);
CREATE INDEX idx_ingest_sources_last_ingest_at ON ingest_sources(last_ingest_at DESC);
CREATE INDEX idx_ingest_sources_last_ingest_status ON ingest_sources(last_ingest_status);
CREATE INDEX idx_ingest_sources_created_by ON ingest_sources(created_by);

-- GIN 索引
CREATE INDEX idx_ingest_sources_config_gin ON ingest_sources USING GIN(source_config);
CREATE INDEX idx_ingest_sources_field_mapping_gin ON ingest_sources USING GIN(field_mapping);
CREATE INDEX idx_ingest_sources_category_mapping_gin ON ingest_sources USING GIN(category_mapping);
CREATE INDEX idx_ingest_sources_schedule_config_gin ON ingest_sources USING GIN(schedule_config);
```

#### 外键关系

```sql
-- 默认分类外键
ALTER TABLE ingest_sources 
    ADD CONSTRAINT fk_ingest_sources_default_category 
    FOREIGN KEY (default_category_id) 
    REFERENCES categories(id) 
    ON DELETE SET NULL 
    ON UPDATE CASCADE;

-- 创建者外键
ALTER TABLE ingest_sources 
    ADD CONSTRAINT fk_ingest_sources_created_by 
    FOREIGN KEY (created_by) 
    REFERENCES users(id) 
    ON DELETE SET NULL 
    ON UPDATE CASCADE;
```

#### source_config 示例

**RSS 类型:**
```json
{
  "url": "https://openai.com/blog/rss.xml",
  "feed_type": "rss2.0",
  "timeout": 30,
  "encoding": "utf-8",
  "user_agent": "AI-News-Hub-Bot/1.0"
}
```

**API 类型:**
```json
{
  "url": "https://api.example.com/v1/posts",
  "method": "GET",
  "headers": {
    "Accept": "application/json"
  },
  "auth_type": "bearer",
  "pagination": {
    "type": "cursor",
    "cursor_param": "after"
  }
}
```

**Webhook 类型:**
```json
{
  "event_types": ["content.create", "content.update"],
  "signature_header": "X-Webhook-Signature",
  "signature_algorithm": "hmac-sha256"
}
```

---

### 2.7 接入日志表 (ingest_logs)

存储内容接入操作的详细日志。

#### 表结构

```sql
CREATE TABLE ingest_logs (
    -- 主键
    id VARCHAR(24) PRIMARY KEY,
    
    -- 任务信息
    job_id VARCHAR(24),
    source_id VARCHAR(24) NOT NULL,
    
    -- 操作类型
    operation_type VARCHAR(20) NOT NULL,
    
    -- 内容信息
    content_id VARCHAR(24),
    external_id VARCHAR(255),
    content_title VARCHAR(200),
    source_url VARCHAR(500),
    
    -- 处理结果
    status VARCHAR(20) NOT NULL,
    error_code VARCHAR(50),
    error_message TEXT,
    
    -- 处理详情
    processing_details JSONB DEFAULT '{}',
    
    -- 性能指标
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    duration_ms INTEGER,
    
    -- 创建者
    created_by VARCHAR(24),
    
    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

#### 字段说明

| 字段名 | 类型 | 可空 | 默认值 | 描述 |
|--------|------|------|--------|------|
| id | VARCHAR(24) | NO | - | 主键 |
| job_id | VARCHAR(24) | YES | NULL | 关联的任务 ID |
| source_id | VARCHAR(24) | NO | - | 接入源 ID |
| operation_type | VARCHAR(20) | NO | - | 操作类型: create/update/delete |
| content_id | VARCHAR(24) | YES | NULL | 生成的内容 ID |
| external_id | VARCHAR(255) | YES | NULL | 外部系统 ID |
| content_title | VARCHAR(200) | YES | NULL | 内容标题 |
| source_url | VARCHAR(500) | YES | NULL | 来源 URL |
| status | VARCHAR(20) | NO | - | 状态: success/partial/failed |
| error_code | VARCHAR(50) | YES | NULL | 错误码 |
| error_message | TEXT | YES | NULL | 错误信息 |
| processing_details | JSONB | NO | {} | 处理详情 |
| started_at | TIMESTAMPTZ | NO | - | 开始时间 |
| completed_at | TIMESTAMPTZ | YES | NULL | 完成时间 |
| duration_ms | INTEGER | YES | NULL | 耗时(毫秒) |
| created_by | VARCHAR(24) | YES | NULL | 创建者 ID |
| created_at | TIMESTAMPTZ | NO | NOW() | 创建时间 |

#### 索引设计

```sql
-- 主键
ALTER TABLE ingest_logs ADD CONSTRAINT pk_ingest_logs PRIMARY KEY (id);

-- 普通索引
CREATE INDEX idx_ingest_logs_job_id ON ingest_logs(job_id);
CREATE INDEX idx_ingest_logs_source_id ON ingest_logs(source_id);
CREATE INDEX idx_ingest_logs_operation_type ON ingest_logs(operation_type);
CREATE INDEX idx_ingest_logs_content_id ON ingest_logs(content_id);
CREATE INDEX idx_ingest_logs_external_id ON ingest_logs(external_id);
CREATE INDEX idx_ingest_logs_status ON ingest_logs(status);
CREATE INDEX idx_ingest_logs_error_code ON ingest_logs(error_code) WHERE error_code IS NOT NULL;
CREATE INDEX idx_ingest_logs_created_by ON ingest_logs(created_by);

-- 时间索引
CREATE INDEX idx_ingest_logs_started_at ON ingest_logs(started_at DESC);
CREATE INDEX idx_ingest_logs_completed_at ON ingest_logs(completed_at DESC);
CREATE INDEX idx_ingest_logs_created_at ON ingest_logs(created_at DESC);

-- 组合索引
CREATE INDEX idx_ingest_logs_source_status ON ingest_logs(source_id, status);
CREATE INDEX idx_ingest_logs_source_started ON ingest_logs(source_id, started_at DESC);

-- GIN 索引
CREATE INDEX idx_ingest_logs_processing_details_gin ON ingest_logs USING GIN(processing_details);
```

#### 外键关系

```sql
-- 接入源外键
ALTER TABLE ingest_logs 
    ADD CONSTRAINT fk_ingest_logs_source 
    FOREIGN KEY (source_id) 
    REFERENCES ingest_sources(id) 
    ON DELETE CASCADE 
    ON UPDATE CASCADE;

-- 内容外键
ALTER TABLE ingest_logs 
    ADD CONSTRAINT fk_ingest_logs_content 
    FOREIGN KEY (content_id) 
    REFERENCES articles(id) 
    ON DELETE SET NULL 
    ON UPDATE CASCADE;

-- 创建者外键
ALTER TABLE ingest_logs 
    ADD CONSTRAINT fk_ingest_logs_created_by 
    FOREIGN KEY (created_by) 
    REFERENCES users(id) 
    ON DELETE SET NULL 
    ON UPDATE CASCADE;
```

---

## 3. Qdrant 向量集合设计

### 3.1 概述

Qdrant 用于存储资讯内容的向量表示,支持语义搜索和相似内容推荐。

### 3.2 向量集合 (articles_embeddings)

#### 集合配置

```json
{
  "collection_name": "articles_embeddings",
  "vectors": {
    "size": 1536,
    "distance": "Cosine",
    "hnsw_config": {
      "m": 16,
      "ef_construct": 100,
      "full_scan_threshold": 10000
    }
  },
  "optimizers_config": {
    "default_segment_number": 2,
    "max_segment_size": 50000,
    "memmap_threshold": 50000,
    "indexing_threshold": 20000
  },
  "wal_config": {
    "wal_capacity_mb": 32,
    "wal_segments_ahead": 2
  }
}
```

#### 向量参数说明

| 参数 | 值 | 说明 |
|------|------|------|
| size | 1536 | 向量维度,对应 OpenAI text-embedding-3-small |
| distance | Cosine | 相似度计算方式 |

#### Payload 结构

```json
{
  "article_id": "art_abc123",
  "title": "GPT-5 即将发布",
  "slug": "gpt-5-release",
  "summary": "摘要...",
  "content_preview": "内容前500字符...",
  "category_id": "cat_ai",
  "category_name": "人工智能",
  "tags": ["GPT-5", "OpenAI", "LLM"],
  "author_id": "usr_def456",
  "author_name": "Tech Reporter",
  "status": "published",
  "language": "zh",
  "published_at": "2026-03-18T10:00:00Z",
  "created_at": "2026-03-18T09:00:00Z",
  "view_count": 1234,
  "embedding_model": "text-embedding-3-small",
  "embedding_version": "2024-03",
  "chunk_index": 0,
  "total_chunks": 1,
  "chunk_text": "..."
}
```

#### Payload 字段说明

| 字段名 | 类型 | 说明 |
|--------|------|------|
| article_id | string | 关联的文章 ID |
| title | string | 文章标题 |
| slug | string | URL slug |
| summary | string | 摘要 |
| content_preview | string | 内容预览 |
| category_id | string | 分类 ID |
| category_name | string | 分类名称 |
| tags | array | 标签列表 |
| author_id | string | 作者 ID |
| author_name | string | 作者名称 |
| status | string | 文章状态 |
| language | string | 语言代码 |
| published_at | string | 发布时间 |
| created_at | string | 创建时间 |
| view_count | integer | 浏览次数 |
| embedding_model | string | 使用的嵌入模型 |
| embedding_version | string | 模型版本 |
| chunk_index | integer | 块索引(长文本分块) |
| total_chunks | integer | 总块数 |
| chunk_text | string | 当前块的文本内容 |

#### 索引配置

```json
{
  "field_name": "article_id",
  "field_schema": "keyword"
}
```

```json
{
  "field_name": "category_id",
  "field_schema": "keyword"
}
```

```json
{
  "field_name": "tags",
  "field_schema": "keyword"
}
```

```json
{
  "field_name": "status",
  "field_schema": "keyword"
}
```

```json
{
  "field_name": "language",
  "field_schema": "keyword"
}
```

```json
{
  "field_name": "published_at",
  "field_schema": "datetime"
}
```

```json
{
  "field_name": "view_count",
  "field_schema": "integer"
}
```

#### 查询示例

**语义搜索:**
```python
from qdrant_client import QdrantClient
from qdrant_client.models import SearchParams

client = QdrantClient(host="localhost", port=6333)

# 向量(来自 embedding API)
query_vector = [0.1, 0.2, ...]  # 1536 维

results = client.search(
    collection_name="articles_embeddings",
    query_vector=query_vector,
    limit=10,
    query_filter={
        "must": [
            {"key": "status", "match": {"value": "published"}},
            {"key": "language", "match": {"value": "zh"}}
        ]
    },
    search_params=SearchParams(hnsw_ef=128, exact=False)
)
```

**相似内容推荐:**
```python
# 基于某篇文章找相似文章
article_vector = client.retrieve(
    collection_name="articles_embeddings",
    ids=["art_abc123"],
    with_vectors=True
)[0].vector

similar_articles = client.search(
    collection_name="articles_embeddings",
    query_vector=article_vector,
    limit=5,
    query_filter={
        "must_not": [
            {"key": "article_id", "match": {"value": "art_abc123"}}
        ],
        "must": [
            {"key": "status", "match": {"value": "published"}}
        ]
    }
)
```

---

## 4. 数据流向图

### 4.1 内容接入流程

```
┌─────────────────────────────────────────────────────────────────────┐
│                        内容接入数据流                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │  External    │    │  External    │    │  External    │          │
│  │  RSS Feed    │    │  API/Webhook │    │  JSON Feed   │          │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘          │
│         │                   │                   │                   │
│         └───────────────────┼───────────────────┘                   │
│                             │                                       │
│                             ▼                                       │
│                    ┌──────────────────┐                            │
│                    │   OpenClaw       │                            │
│                    │   Ingest Service │                            │
│                    └────────┬─────────┘                            │
│                             │                                       │
│         ┌───────────────────┼───────────────────┐                   │
│         │                   │                   │                   │
│         ▼                   ▼                   ▼                   │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐          │
│  │ PostgreSQL   │   │ Qdrant       │   │ Redis        │          │
│  │ articles     │   │ articles_    │   │ Cache        │          │
│  │ categories   │   │ embeddings   │   │ Rate Limit   │          │
│  │ tags         │   │              │   │              │          │
│  └──────────────┘   └──────────────┘   └──────────────┘          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 用户请求流程

```
┌─────────────────────────────────────────────────────────────────────┐
│                        用户请求数据流                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐                                                  │
│  │    User      │                                                  │
│  │   Request    │                                                  │
│  └──────┬───────┘                                                  │
│         │                                                          │
│         ▼                                                          │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐         │
│  │    CDN       │────▶│  API Gateway │────▶│   Rate       │         │
│  │   Cache      │     │   (Kong)     │     │   Limiter    │         │
│  └──────────────┘     └──────┬───────┘     └──────┬───────┘         │
│                              │                    │                  │
│                              ▼                    ▼                  │
│                    ┌──────────────────┐   ┌──────────────┐           │
│                    │   Auth Service   │   │    Redis   │           │
│                    │   (JWT Verify)   │   │   Token    │           │
│                    └────────┬─────────┘   └────────────┘           │
│                             │                                       │
│                             ▼                                       │
│                    ┌──────────────────┐                              │
│                    │  Business Logic  │                              │
│                    │    Service       │                              │
│                    └────────┬─────────┘                              │
│                             │                                       │
│         ┌───────────────────┼───────────────────┐                   │
│         │                   │                   │                   │
│         ▼                   ▼                   ▼                   │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐          │
│  │ PostgreSQL   │   │ Qdrant       │   │    Meilisearch         │
│  │  (Primary)   │   │  (Semantic   │   │   (Full-text │          │
│  │              │   │   Search)    │   │    Search)   │          │
│  └──────────────┘   └──────────────┘   └──────────────┘          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 5. 性能优化策略

### 5.1 数据库优化

#### 连接池配置

```yaml
# PostgreSQL 连接池
postgresql:
  pool_size: 20
  max_overflow: 30
  pool_timeout: 30
  pool_recycle: 3600
```

#### 查询优化

- 使用 EXPLAIN ANALYZE 分析慢查询
- 避免 SELECT *, 只查询需要的字段
- 使用 LIMIT 分页,避免 OFFSET 过大
- 对频繁查询的字段建立索引

### 5.2 缓存策略

#### Redis 缓存层

```
Key 命名规范:
- user:{user_id} -> 用户信息哈希
- user:session:{token} -> 会话信息
- article:{article_id} -> 文章详情
- articles:list:{hash} -> 文章列表(分页缓存)
- rate_limit:{endpoint}:{identifier} -> 限流计数
- ingest:job:{job_id} -> 接入任务状态
```

#### 缓存失效策略

- 写时失效(Write-Through): 更新数据时同步更新缓存
- 过期时间(TTL): 根据数据类型设置不同的过期时间
  - 用户信息: 1 小时
  - 文章详情: 24 小时
  - 列表数据: 10 分钟
  - 限流计数: 1 分钟

### 5.3 读写分离

```
┌─────────────────────────────────────────────┐
│              Application                     │
└──────────────┬──────────────────────────────┘
               │
       ┌───────▼────────┐
       │  Proxy/ORM     │
       │  (Read/Write   │
       │   Splitting)   │
       └───────┬────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
    ▼          ▼          ▼
┌──────┐  ┌──────┐  ┌──────┐
│Master│  │Replica│  │Replica│
│(Write)│  │(Read) │  │(Read) │
└──────┘  └──────┘  └──────┘
```

---

## 6. 安全策略

### 6.1 数据加密

#### 静态加密

- PostgreSQL 使用透明数据加密(TDE)
- 敏感字段(如 credentials)应用层加密
- 备份文件加密存储

#### 传输加密

- 强制使用 TLS 1.3
- 数据库连接使用 SSL
- Redis 启用 TLS

### 6.2 访问控制

#### 数据库用户权限

```sql
-- 应用只读用户
CREATE USER app_readonly WITH PASSWORD '***';
GRANT CONNECT ON DATABASE ainewshub TO app_readonly;
GRANT USAGE ON SCHEMA public TO app_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_readonly;

-- 应用读写用户
CREATE USER app_readwrite WITH PASSWORD '***';
GRANT CONNECT ON DATABASE ainewshub TO app_readwrite;
GRANT USAGE ON SCHEMA public TO app_readwrite;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_readwrite;

-- 管理用户(仅限管理员操作)
CREATE USER app_admin WITH PASSWORD '***';
GRANT ALL PRIVILEGES ON DATABASE ainewshub TO app_admin;
```

#### 行级安全(RLS)

```sql
-- 启用 RLS
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;

-- 策略: 用户只能看到自己的草稿
CREATE POLICY articles_user_drafts ON articles
    FOR SELECT
    USING (status = 'draft' AND author_id = current_setting('app.current_user_id', true));

-- 策略: 已发布内容对所有人可见
CREATE POLICY articles_published ON articles
    FOR SELECT
    USING (status = 'published');
```

---

## 7. 备份与恢复

### 7.1 备份策略

#### PostgreSQL 备份

```bash
# 每日全量备份
0 2 * * * pg_dump -h localhost -U postgres ainewshub | gzip > /backup/pg/full_$(date +\%Y\%m\%d).sql.gz

# 每小时增量备份(WAL 归档)
archive_command = 'cp %p /backup/pg/wal/%f'

# 每周一致性检查
0 3 * * 0 pg_dump -h localhost -U postgres --schema-only ainewshub > /backup/pg/schema_$(date +\%Y\%m\%d).sql
```

#### Qdrant 备份

```bash
# 创建快照
curl -X POST \
  http://localhost:6333/collections/articles_embeddings/snapshots

# 下载快照
curl -O http://localhost:6333/collections/articles_embeddings/snapshots/{snapshot_name}
```

### 7.2 恢复流程

```bash
# PostgreSQL 恢复
# 1. 停止应用
# 2. 恢复数据
gunzip -c /backup/pg/full_20260319.sql.gz | psql -h localhost -U postgres ainewshub

# 3. 恢复 WAL(时间点恢复)
pg_waldump /backup/pg/wal/...

# 4. 重启应用

# Qdrant 恢复
# 1. 上传快照
curl -X POST \
  -H "Content-Type:multipart/form-data" \
  -F "snapshot=@snapshot_file" \
  http://localhost:6333/collections/articles_embeddings/snapshots/recover
```

---

## 8. 监控与告警

### 8.1 监控指标

#### 数据库性能指标

| 指标名 | 说明 | 告警阈值 |
|--------|------|----------|
| pg_stat_activity_count | 活跃连接数 | > 80% max_connections |
| pg_stat_database_xact_commit | 事务提交率 | < 1000 TPS |
| pg_stat_database_blks_read | 磁盘读取块数 | > 10000/s |
| pg_stat_user_tables_seq_scan | 全表扫描次数 | > 100/hour |
| pg_stat_user_indexes_idx_scan | 索引扫描率 | < 95% |
| pg_stat_database_deadlocks | 死锁次数 | > 0 |
| pg_stat_replication_lag | 复制延迟 | > 5s |

#### Qdrant 指标

| 指标名 | 说明 | 告警阈值 |
|--------|------|----------|
| collections_vector_count | 向量总数 | - |
| collections_segment_count | Segment 数量 | > 50 |
| collections_optimization_avg | 平均优化时间 | > 10s |
| cluster_peer_count | 集群节点数 | < 3 |

### 8.2 告警配置

```yaml
# AlertManager 配置
groups:
  - name: database_alerts
    rules:
      - alert: PostgreSQLHighConnections
        expr: pg_stat_activity_count / pg_settings_max_connections > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "PostgreSQL 连接数过高"
          description: "当前连接数: {{ $value }}%"
          
      - alert: PostgreSQLReplicationLag
        expr: pg_stat_replication_lag > 5
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "PostgreSQL 复制延迟过高"
          description: "当前延迟: {{ $value }}s"
```

---

## 9. 附录

### 9.1 完整 ER 图

```
┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│      users       │       │    articles      │       │   categories     │
├──────────────────┤       ├──────────────────┤       ├──────────────────┤
│ PK id            │       │ PK id            │       │ PK id            │
│    username      │◄──────┤ FK author_id     │       │    name          │
│    email         │       │    title         │       │    slug          │
│    password_hash│       │    slug          │       │    description   │
│    avatar_url    │       │    content       │       │ FK parent_id     │◄─┐
│    role          │       │    status        │       │    level         │  │
│    is_active     │       │ FK category_id   │◄──────┤    path          │  │
│    preferences   │       │ FK ingest_     │       │    is_active     │  │
│    created_at    │       │    source_id     │       │    article_count │  │
│    updated_at    │       │    view_count    │       └──────────────────┘  │
└──────────────────┘       │    published_at  │                              │
                           │    created_at    │                              │
                           └──────────────────┘                              │
                                    │                                        │
                                    │                                        │
               ┌────────────────────┼────────────────────┐                  │
               │                    │                    │                  │
               ▼                    ▼                    ▼                  │
      ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐        │
      │   article_tags     │ │  ingest_sources  │ │  ingest_logs     │        │
      ├──────────────────┤ ├──────────────────┤ ├──────────────────┤        │
      │ PK,FK article_id │ │ PK id            │ │ PK id            │        │
      │ PK,FK tag_id     │ │    name          │ │ FK job_id        │        │
      │    created_at    │ │    source_type   │ │ FK source_id     │────────┘
      └──────────────────┘ │    source_config │ │    operation_type│
                           │    is_active     │ │    content_id    │
      ┌──────────────────┐ │    last_ingest_  │ │    external_id   │
      │      tags          │ │    at            │ │    status        │
      ├──────────────────┤ │    total_ingested│ │    error_code    │
      │ PK id            │ │    created_by    │ │    started_at    │
      │    name          │ └──────────────────┘ │    completed_at  │
      │    slug          │                      │    created_at    │
      │    article_count │                      └──────────────────┘
      │    created_at    │
      └──────────────────┘
```

### 9.2 数据字典

#### 状态枚举值

| 枚举类型 | 值 | 说明 |
|----------|------|------|
| user_role | user | 普通用户 |
| user_role | editor | 编辑 |
| user_role | admin | 管理员 |
| article_status | draft | 草稿 |
| article_status | published | 已发布 |
| article_status | archived | 已归档 |
| article_status | deleted | 已删除(软删除) |
| source_type | rss | RSS Feed |
| source_type | atom | Atom Feed |
| source_type | json_feed | JSON Feed |
| source_type | api | REST API |
| source_type | webhook | Webhook |
| source_type | crawler | 爬虫 |
| source_type | sitemap | XML Sitemap |
| schedule_type | manual | 手动触发 |
| schedule_type | interval | 定时间隔 |
| schedule_type | cron | Cron 表达式 |
| schedule_type | webhook | Webhook 触发 |
| ingest_status | success | 成功 |
| ingest_status | partial | 部分成功 |
| ingest_status | failed | 失败 |
| ingest_status | running | 进行中 |
| operation_type | create | 创建内容 |
| operation_type | update | 更新内容 |
| operation_type | delete | 删除内容 |

### 9.3 数据库初始化脚本

```sql
-- 创建数据库
CREATE DATABASE ainewshub 
    WITH 
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

-- 启用扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- 模糊搜索

-- 创建 updated_at 自动更新函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 创建触发器
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_articles_updated_at BEFORE UPDATE ON articles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_categories_updated_at BEFORE UPDATE ON categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tags_updated_at BEFORE UPDATE ON tags
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ingest_sources_updated_at BEFORE UPDATE ON ingest_sources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 创建软删除视图
CREATE OR REPLACE VIEW active_users AS
    SELECT * FROM users WHERE deleted_at IS NULL;

CREATE OR REPLACE VIEW active_articles AS
    SELECT * FROM articles WHERE deleted_at IS NULL;

CREATE OR REPLACE VIEW active_categories AS
    SELECT * FROM categories WHERE deleted_at IS NULL;

-- 插入测试数据(可选)
-- INSERT INTO users (id, username, email, password_hash, role) VALUES ...
-- INSERT INTO categories (id, name, slug, level) VALUES ...

-- 权限配置
-- 创建只读用户
-- CREATE USER app_readonly WITH PASSWORD '***';
-- GRANT CONNECT ON DATABASE ainewshub TO app_readonly;
-- GRANT USAGE ON SCHEMA public TO app_readonly;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_readonly;
```

---

## 10. 总结

### 10.1 设计原则回顾

1. **可扩展性**: 支持水平扩展,易于增加新功能
2. **性能**: 通过索引、缓存、读写分离优化性能
3. **可靠性**: 数据备份、监控告警、故障恢复
4. **安全性**: 数据加密、访问控制、审计日志
5. **可维护性**: 清晰的文档、规范化的命名、自动化运维

### 10.2 关键设计决策

| 决策项 | 选择 | 理由 |
|--------|------|------|
| 主数据库 | PostgreSQL | 成熟稳定,JSONB 支持,全文搜索 |
| 向量数据库 | Qdrant | 高性能,支持过滤搜索,易于部署 |
| ID 生成 | nanoid | 分布式安全,URL 友好 |
| 软删除 | deleted_at 字段 | 数据可恢复,审计追踪 |
| JSONB 使用 | 用户偏好、统计数据 | 灵活扩展,避免模式变更 |

### 10.3 后续优化方向

1. **分区表**: 大数据量时对历史数据进行分区
2. **读写分离**: 引入只读副本分担查询压力
3. **缓存预热**: 启动时预加载热点数据
4. **智能索引**: 基于查询模式自动推荐索引
5. **数据归档**: 定期归档历史数据到冷存储

---

**文档维护**: AI News Hub 技术团队  
**最后更新**: 2026-03-19  
**文档版本**: v1.0.0
