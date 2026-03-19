# AI News Hub 安全设计文档

> 最后更新：2026-03-19
> 版本：v1.0.0

---

## 1. 安全策略概述

### 1.1 安全目标

| 目标 | 描述 |
|------|------|
| **机密性** | 确保用户数据和系统信息不被未授权访问 |
| **完整性** | 确保数据在传输和存储过程中不被篡改 |
| **可用性** | 确保系统服务持续稳定运行 |
| **可追溯性** | 确保所有操作可审计、可追溯 |

### 1.2 安全原则

1. **最小权限原则**：每个组件和用户只拥有完成任务所需的最小权限
2. **纵深防御**：多层安全防护，单一防线失效不影响整体安全
3. **默认安全**：安全配置是默认选项，不需要额外配置
4. **零信任**：不信任内部网络，所有请求都需要验证

---

## 2. 认证与授权

### 2.1 认证机制

#### JWT Token 设计

```
┌─────────────────────────────────────────────────────────────┐
│                     Access Token 结构                        │
├─────────────────────────────────────────────────────────────┤
│  Header:                                                     │
│  {                                                           │
│    "alg": "RS256",                                          │
│    "typ": "JWT"                                             │
│  }                                                           │
│                                                              │
│  Payload:                                                    │
│  {                                                           │
│    "sub": "user_id",              // 用户 ID                │
│    "role": "user",                // 用户角色                │
│    "iat": 1710000000,             // 签发时间                │
│    "exp": 1710001500              // 过期时间 (15min)       │
│  }                                                           │
│                                                              │
│  Signature: RS256(Header.Payload, PrivateKey)               │
└─────────────────────────────────────────────────────────────┘
```

#### Token 安全策略

| 策略 | 配置值 | 说明 |
|------|--------|------|
| Access Token 有效期 | 15 分钟 | 短期有效，减少泄露风险 |
| Refresh Token 有效期 | 7 天 | 长期有效，方便用户 |
| Token 存储 | HttpOnly Cookie | 防止 XSS 攻击 |
| Token 传输 | HTTPS Only | 加密传输 |
| Token 撤销 | Redis 黑名单 | 支持强制登出 |

### 2.2 密码安全

#### 密码策略

| 规则 | 要求 |
|------|------|
| 最小长度 | 8 字符 |
| 最大长度 | 128 字符 |
| 大小写 | 必须包含 |
| 数字 | 必须包含 |
| 特殊字符 | 推荐包含 |
| 历史密码 | 最近 5 个密码不能重复 |

#### 密码存储

```
原始密码 → bcrypt(Password, salt_rounds=12) → 哈希存储
```

### 2.3 授权模型

#### 角色定义

| 角色 | 描述 | 权限范围 |
|------|------|----------|
| `anonymous` | 匿名用户 | 浏览公开内容 |
| `user` | 注册用户 | 个人设置、收藏、评论 |
| `editor` | 内容编辑 | 内容审核、标签管理 |
| `admin` | 管理员 | 全系统管理、用户管理 |

#### API 权限矩阵

| API 端点 | anonymous | user | editor | admin |
|----------|-----------|------|--------|-------|
| GET /articles | ✓ | ✓ | ✓ | ✓ |
| POST /articles | ✗ | ✗ | ✓ | ✓ |
| PUT /articles/{id} | ✗ | ✗ | ✓ | ✓ |
| DELETE /articles/{id} | ✗ | ✗ | ✗ | ✓ |
| GET /admin/users | ✗ | ✗ | ✗ | ✓ |

---

## 3. API 安全

### 3.1 Webhook 安全

#### OpenClaw Webhook 签名验证

```
┌─────────────────────────────────────────────────────────────┐
│                   Webhook 安全流程                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  OpenClaw                      AI News Hub                   │
│     │                              │                         │
│     │  POST /api/v1/ingest/webhook │                         │
│     │ ───────────────────────────▶ │                         │
│     │                              │                         │
│     │  Header:                     │                         │
│     │  X-Signature: sha256=xxx     │                         │
│     │                              │                         │
│     │                              │  1. 提取 body           │
│     │                              │  2. 使用 HMAC-SHA256    │
│     │                              │     + Webhook Secret    │
│     │                              │     计算签名             │
│     │                              │  3. 比较签名             │
│     │                              │                         │
│     │      200 OK                  │                         │
│     │ ◀─────────────────────────── │                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### 签名验证算法

```python
# Python 示例
import hmac
import hashlib

def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(
        key=secret.encode(),
        msg=payload,
        digestmod=hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(f"sha256={expected}", signature)
```

### 3.2 Rate Limiting

#### 限流策略

| 端点类型 | 限制 | 窗口 |
|----------|------|------|
| 公开 API | 100 次/分钟 | 滑动窗口 |
| 认证 API | 5 次/分钟 | 固定窗口 |
| 写入 API | 30 次/分钟 | 滑动窗口 |
| OpenClaw 接入 | 1000 次/小时 | 固定窗口 |
| AI 问答 | 10 次/分钟 | 固定窗口 |

#### 限流响应

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "请求过于频繁，请稍后再试",
    "retry_after": 60
  }
}
```

### 3.3 CORS 配置

```python
# FastAPI CORS 配置
CORSMiddleware(
    app,
    allow_origins=["https://ai-newshub.com"],  # 生产环境
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

---

## 4. 数据安全

### 4.1 数据加密

#### 传输加密

- **TLS 1.3**：所有 HTTP 通信必须使用 HTTPS
- **证书**：使用 Let's Encrypt 或商业证书
- **HSTS**：强制 HTTPS 访问

#### 存储加密

| 数据类型 | 加密方式 | 说明 |
|----------|----------|------|
| 用户密码 | bcrypt | 单向哈希，不可逆 |
| JWT Secret | AES-256 | 对称加密存储 |
| 数据库 | LUKS | 磁盘级加密 |
| 敏感配置 | Vault | 密钥管理服务 |
| 备份数据 | AES-256 | 备份加密 |

### 4.2 数据库安全

#### PostgreSQL 安全配置

```sql
-- 启用 SSL 连接
ALTER SYSTEM SET ssl = on;
ALTER SYSTEM SET ssl_cert_file = '/path/to/server.crt';
ALTER SYSTEM SET ssl_key_file = '/path/to/server.key';

-- 密码复杂度要求
ALTER SYSTEM SET password_encryption = 'scram-sha-256';

-- Row-Level Security (RLS)
CREATE POLICY user_isolation ON users
    FOR ALL
    USING (auth.uid() = id);

-- 审计日志
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_duration = on;
```

#### 访问控制

```python
# 数据库连接池配置
async def get_db():
    # 只允许应用服务器连接
    # 限制 IP 白名单
    pass
```

### 4.3 数据脱敏

| 场景 | 脱敏规则 |
|------|----------|
| 用户邮箱 | `u***@domain.com` |
| 手机号 | `138****5678` |
| 身份证 | `310***********1234` |
| 真实姓名 | `李*` |
| API Key | `sk-***xxxx` |

---

## 5. 输入安全

### 5.1 SQL 注入防护

```python
# 使用 SQLAlchemy ORM，自动防注入
# ✅ 正确写法
result = db.query(Article).filter(Article.title == user_input).all()

# ❌ 危险写法 - 禁止使用
# result = db.execute(f"SELECT * FROM articles WHERE title = '{user_input}'")
```

### 5.2 XSS 防护

```typescript
// React 自动转义，不需要额外处理
// 但在 dangerouslySetInnerHTML 使用时必须谨慎

// ✅ 安全：使用 DOMPurify 净化
import DOMPurify from 'dompurify';
const sanitizedHTML = DOMPurify.sanitize(dirtyHTML);

// ❌ 危险：直接使用
// <div dangerouslySetInnerHTML={{ __html: dirtyHTML }} />
```

### 5.3 CSRF 防护

```typescript
// 使用 csurf 中间件
import csurf from 'csurf';

app.use(csurf({
  cookie: {
    httpOnly: true,
    secure: true,
  }
}));
```

### 5.4 请求验证

```python
# Pydantic 模型验证所有输入
from pydantic import BaseModel, EmailStr, validator

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('密码长度至少8位')
        if not re.search(r'[A-Z]', v):
            raise ValueError('密码必须包含大写字母')
        return v
```

---

## 6. 基础设施安全

### 6.1 网络安全

#### 防火墙规则

```
┌─────────────────────────────────────────────────────────────┐
│                     网络访问控制                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   互联网                                                     │
│      │                                                      │
│      ▼                                                      │
│   ┌─────────┐   80/443   ┌──────────┐                       │
│   │  WAF    │ ─────────▶ │ 负载均衡 │                       │
│   └─────────┘            └────┬─────┘                       │
│                             │                              │
│                    ┌────────┴────────┐                     │
│                    ▼                 ▼                     │
│               ┌─────────┐       ┌─────────┐                │
│               │ Frontend│       │ Backend │                │
│               │  Server │       │  Server │                │
│               └────┬────┘       └────┬────┘                │
│                    │                 │                     │
│                    └────────┬────────┘                     │
│                             │                              │
│                    ┌────────┴────────┐                     │
│                    ▼                 ▼                     │
│               ┌─────────┐       ┌─────────┐ ┌────────┐     │
│               │ PostgreSQL│      │  Redis  │ │ Qdrant │     │
│               └─────────┘       └─────────┘ └────────┘     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### 安全组配置

| 组件 | 入站规则 | 出站规则 |
|------|----------|----------|
| WAF | 0.0.0.0/0 (80,443) | 应用服务器 |
| Frontend | WAF (80,443) | 0.0.0.0/0 |
| Backend | Frontend (8080) | DB, Redis |
| PostgreSQL | Backend (5432) | 仅内网 |
| Redis | Backend (6379) | 仅内网 |

### 6.2 容器安全

```dockerfile
# 使用非 root 用户运行
FROM node:20-alpine

# 创建应用用户
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# 设置工作目录权限
WORKDIR /app
RUN chown -R appuser:appgroup /app

# 切换到非 root 用户
USER appuser

# 只读文件系统
READONLY=true
```

### 6.3 密钥管理

```
# 密钥存储优先级
1. 环境变量（开发）
2. Docker Secrets（Swarm）
3. HashiCorp Vault（生产）
4. AWS Secrets Manager（AWS 部署）
```

---

## 7. 安全运营

### 7.1 日志与监控

#### 安全日志

| 事件 | 级别 | 记录内容 |
|------|------|----------|
| 登录成功 | INFO | 用户ID, IP, 时间 |
| 登录失败 | WARNING | 尝试用户, IP, 次数 |
| 权限不足 | WARNING | 用户ID, 请求资源 |
| Token 刷新 | DEBUG | 用户ID |
| 管理操作 | INFO | 管理员ID, 操作内容 |
| 异常访问 | ERROR | IP, 请求路径, 错误 |

#### 监控告警

| 告警规则 | 阈值 | 动作 |
|----------|------|------|
| 登录失败率 | > 10% | 触发账户锁定 |
| API 错误率 | > 5% | 发送告警 |
| 异常 IP 访问 | > 100次/分钟 | 封禁 IP |
| Token 刷新异常 | 短时间内 > 10次 | 审计调查 |

### 7.2 备份与恢复

| 备份类型 | 频率 | 保留时间 | 加密 |
|----------|------|----------|------|
| 全量备份 | 每日 | 30 天 | AES-256 |
| 增量备份 | 每小时 | 7 天 | AES-256 |
| 事务日志 | 实时 | 7 天 | AES-256 |
| 异地备份 | 每日 | 90 天 | AES-256 |

### 7.3 应急响应

```
安全事件响应流程：

1. 发现 (Detection)
   └── 监控告警 / 用户报告 / 内部发现
   
2. 评估 (Assessment) 
   └── 确定影响范围、严重程度
   
3. 遏制 (Containment)
   └── 隔离受影响系统、阻断攻击路径
   
4. 根除 (Eradication)
   └── 清除恶意代码、修复漏洞
   
5. 恢复 (Recovery)
   └── 恢复系统、更新备份
   
6. 复盘 (Post-Incident)
   └── 分析原因、更新安全策略
```

---

## 8. 合规要求

### 8.1 隐私保护

- **数据最小化**：只收集必需的数据
- **用户同意**：收集前获取明确同意
- **删除权**：用户可请求删除账户和数据
- **数据可携**：支持导出用户数据

### 8.2 Cookie 政策

| Cookie 类型 | 用途 | 过期时间 |
|-------------|------|----------|
| session_id | 会话管理 | 浏览器关闭 |
| refresh_token | 登录状态 | 7 天 |
| preferences | 用户偏好 | 1 年 |

---

## 9. 安全检查清单

### 开发阶段

- [ ] 所有输入经过验证
- [ ] 使用参数化查询
- [ ] 敏感数据加密存储
- [ ] API 实现认证和授权
- [ ] 错误信息不泄露敏感细节
- [ ] 安全库更新到最新版本

### 部署阶段

- [ ] HTTPS 启用
- [ ] 生产环境调试关闭
- [ ] 环境变量正确配置
- [ ] 防火墙规则设置
- [ ] 监控告警配置
- [ ] 备份机制验证

### 运维阶段

- [ ] 定期安全更新
- [ ] 日志审计
- [ ] 渗透测试
- [ ] 应急响应演练
- [ ] 安全培训

---

## 10. 附录

### 10.1 安全相关依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| bcrypt | 4.1+ | 密码哈希 |
| PyJWT | 2.8+ | JWT 处理 |
| python-jose | 3.3+ | JWT 验证 |
| SQLAlchemy | 2.0+ | ORM 防注入 |
| httpx | 0.25+ | 安全 HTTP |

### 10.2 安全工具

| 工具 | 用途 |
|------|------|
| OWASP ZAP | 自动化渗透测试 |
| Snyk | 依赖漏洞扫描 |
| SonarQube | 代码安全分析 |
| Vault | 密钥管理 |

---

*本文档将随着安全威胁形势和合规要求变化持续更新*
