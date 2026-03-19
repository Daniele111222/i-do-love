# AI News Hub 部署文档

> 最后更新：2026-03-19
> 版本：v1.0.0

---

## 1. 部署架构

### 1.1 生产环境架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      生产环境架构                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│                         ┌──────────┐                            │
│                         │   用户    │                            │
│                         └────┬─────┘                            │
│                              │                                   │
│                              ▼                                   │
│                    ┌─────────────────┐                          │
│                    │      CDN        │                          │
│                    │  (Vercel/CDN)   │                          │
│                    └────────┬────────┘                          │
│                              │                                   │
│              ┌───────────────┼───────────────┐                  │
│              │               │               │                  │
│              ▼               ▼               ▼                  │
│     ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│     │   WAF       │  │  HTTPS      │  │  静态资源   │          │
│     │ (Cloudflare)│  │  Termination│  │  (CDN)      │          │
│     └─────────────┘  └──────┬──────┘  └─────────────┘          │
│                             │                                   │
│                             ▼                                   │
│                    ┌─────────────────┐                          │
│                    │   负载均衡器     │                          │
│                    │   (Nginx/ELB)   │                          │
│                    └────────┬────────┘                          │
│                              │                                   │
│              ┌───────────────┼───────────────┐                  │
│              │               │               │                  │
│              ▼               ▼               ▼                  │
│     ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│     │  Backend 1   │  │  Backend 2   │  │  Backend 3   │          │
│     │  (Railway)  │  │  (Railway)  │  │  (Railway)  │          │
│     └──────┬──────┘  └──────┬──────┘  └──────┬──────┘          │
│            │                 │                 │                  │
│            └─────────────────┼─────────────────┘                  │
│                              │                                   │
│              ┌───────────────┼───────────────┐                  │
│              │               │               │                  │
│              ▼               ▼               ▼                  │
│     ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│     │ PostgreSQL  │  │    Redis    │  │   Qdrant    │          │
│     │  (Supabase) │  │  (Upstash)  │  │ (Qdrant Cloud)│         │
│     └─────────────┘  └─────────────┘  └─────────────┘          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 服务说明

| 服务 | 推荐方案 | 免费额度 | 月费用估算 |
|------|----------|----------|------------|
| 前端部署 | Vercel | 100GB 带宽 | $0 |
| 后端部署 | Railway | 500小时 | $5-20 |
| PostgreSQL | Supabase | 500MB | $0 |
| Redis | Upstash | 10K 命令/天 | $0 |
| 向量数据库 | Qdrant Cloud | 1GB | $0 |
| 域名/SSL | Cloudflare | 免费 | $0 |
| 邮件服务 | Resend | 100封/天 | $0 |

---

## 2. 部署前准备

### 2.1 必需的环境变量

#### 后端环境变量

```bash
# .env.production
# 数据库
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Redis
REDIS_URL=redis://host:6379/0

# 安全
SECRET_KEY=生成的安全密钥
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
ALLOWED_ORIGINS=https://your-domain.com

# OpenAI (Phase 3+)
OPENAI_API_KEY=sk-xxx

# Webhook 密钥
WEBHOOK_SECRET=your-webhook-secret
```

#### 前端环境变量

```bash
# .env.production
VITE_API_BASE_URL=https://api.your-domain.com/api/v1
VITE_APP_NAME=AI News Hub
```

### 2.2 生成密钥

```bash
# 生成 SECRET_KEY
openssl rand -hex 32

# 生成 WEBHOOK_SECRET
openssl rand -hex 16
```

---

## 3. 前端部署

### 3.1 Vercel 部署

#### 方式一：Vercel CLI

```bash
# 安装 Vercel CLI
npm i -g vercel

# 登录
vercel login

# 进入前端目录
cd frontend

# 部署预览
vercel

# 部署生产
vercel --prod
```

#### 方式二：GitHub 集成

1. 将代码推送到 GitHub
2. 访问 [vercel.com](https://vercel.com)
3. 点击 "Import Project"
4. 选择仓库，配置构建命令：
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Environment Variables: 添加 `VITE_API_BASE_URL`

### 3.2 前端配置

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          three: ['three', '@react-three/fiber'],
        },
      },
    },
  },
  server: {
    proxy: {
      '/api': {
        target: process.env.VITE_API_BASE_URL,
        changeOrigin: true,
      },
    },
  },
});
```

---

## 4. 后端部署

### 4.1 Railway 部署

#### 1. 创建 Railway 项目

```bash
# 安装 Railway CLI
npm i -g @railway/cli

# 登录
railway login

# 初始化项目
cd backend
railway init

# 关联数据库（如果需要）
railway add
```

#### 2. 配置 railway.toml

```toml
# railway.toml
[build]
builder = "docker"
dockerfilePath = "Dockerfile"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 30
restartPolicyType = "on-failure"
restartPolicyMaxRetries = 3

[environment]
PORT = "8000"
```

#### 3. 部署

```bash
# 设置环境变量
railway variables set DATABASE_URL=xxx
railway variables set SECRET_KEY=xxx
# ... 其他变量

# 部署
railway up
```

### 4.2 Docker 部署

#### Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 运行
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### docker-compose.yml

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db
      - redis

  db:
    image: postgres:16
    environment:
      POSTGRES_USER: ai_news
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: ai_news
    volumes:
      - pg_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  pg_data:
```

### 4.3 健康检查

```python
# app/main.py
from fastapi import FastAPI
from app.api.v1 import router as api_v1

app = FastAPI(title="AI News Hub API")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

app.include_router(api_v1, prefix="/api/v1")
```

---

## 5. 数据库配置

### 5.1 PostgreSQL (Supabase)

1. 创建 Supabase 项目
2. 获取连接 URL：
   ```
   postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
   ```
3. 设置环境变量

#### 初始迁移

```bash
# 安装 Alembic CLI
pip install alembic

# 初始化（如果需要）
alembic init alembic

# 创建迁移
alembic revision --autogenerate -m "initial"

# 应用迁移
alembic upgrade head
```

### 5.2 Redis (Upstash)

1. 创建 Upstash Redis 数据库
2. 获取连接 URL：
   ```
   redis://default:[PASSWORD]@[HOST]:6379
   ```
3. 设置环境变量

### 5.3 Qdrant Cloud

1. 创建 Qdrant Cloud 集群
2. 获取 API Key 和 URL
3. 设置环境变量

---

## 6. 域名配置

### 6.1 DNS 设置

```
# A Record
A @ 203.0.113.1  # 指向服务器 IP

# CNAME Record
CNAME www @

# API 子域名
CNAME api @  # 或 A record 指向后端 IP
```

### 6.2 SSL 证书

#### 使用 Cloudflare（推荐）

1. 注册 Cloudflare
2. 添加域名，更新 Nameservers
3. SSL 模式设置为 "Full" 或 "Strict"

#### 使用 Let's Encrypt

```bash
# 安装 certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com -d api.your-domain.com
```

---

## 7. CI/CD 流程

### 7.1 GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: vercel/actions/deploy@v1
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}

  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: railway/actions/deploy@main
        with:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

### 7.2 环境变量管理

```bash
# Vercel 环境变量
vercel env add VITE_API_BASE_URL production

# Railway 环境变量
railway variables set SECRET_KEY=xxx production
```

---

## 8. 监控与日志

### 8.1 日志配置

```python
# app/core/config.py
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("/var/log/ai-news.log"),
    ],
)
```

### 8.2 健康检查

```bash
# 检查 API 健康
curl https://api.your-domain.com/health

# 检查数据库连接
curl https://api.your-domain.com/health/db

# 检查 Redis 连接
curl https://api.your-domain.com/health/redis
```

---

## 9. 备份策略

### 9.1 PostgreSQL 备份

```bash
# 手动备份
pg_dump -U postgres -d ai_news > backup_$(date +%Y%m%d).sql

# Supabase 自动备份
# Supabase 提供每日自动备份，保留 7 天
```

### 9.2 Redis 备份

```bash
# RDB 持久化
redis-cli SAVE

# AOF 持久化（推荐）
# Redis 默认开启 AOF
```

---

## 10. 灾难恢复

### 10.1 恢复流程

```
1. 检测故障
   └── 监控告警 / 用户反馈

2. 评估影响
   └── 确定受影响服务

3. 切换流量
   └── 启用备份 / 启动新实例

4. 数据恢复（如需要）
   └── 从备份恢复数据库

5. 验证服务
   └── 确认功能正常

6. 事后复盘
   └── 分析原因，防止复发
```

### 10.2 故障响应时间目标

| 故障级别 | 响应时间 | 恢复时间 |
|----------|----------|----------|
| P0 (服务中断) | 15 分钟 | 1 小时 |
| P1 (部分不可用) | 1 小时 | 4 小时 |
| P2 (性能下降) | 4 小时 | 24 小时 |
| P3 (非紧急) | 24 小时 | 72 小时 |

---

## 11. 部署检查清单

### 部署前

- [ ] 所有环境变量已配置
- [ ] 数据库迁移已测试
- [ ] SSL 证书已生效
- [ ] DNS 已正确配置
- [ ] 监控告警已设置

### 部署后

- [ ] 健康检查通过
- [ ] 前端可访问
- [ ] API 可正常调用
- [ ] 用户认证流程正常
- [ ] 数据库读写正常
- [ ] 日志正常输出

### 上线后

- [ ] 监控仪表板正常
- [ ] 错误率在预期范围
- [ ] 性能指标达标
- [ ] 用户反馈正常

---

## 12. 回滚流程

### 12.1 前端回滚

```bash
# Vercel CLI
vercel rollback [deployment-url]
```

### 12.2 后端回滚

```bash
# Railway
railway rollback [deployment-id]

# Docker
docker-compose down
docker-compose -f docker-compose.backup.yml up -d
```

### 12.3 数据库回滚

```bash
# Alembic
alembic downgrade -1

# 手动恢复
psql -U postgres -d ai_news < backup_20240101.sql
```

---

## 13. 联系和支持

| 问题类型 | 联系方式 |
|----------|----------|
| 紧急故障 | @oncall |
| 部署问题 | #devops-support |
| 功能咨询 | #product |

---

*本部署文档适用于生产环境，将随着部署实践持续更新*
