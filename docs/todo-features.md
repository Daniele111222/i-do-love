# 待开发功能清单

**日期:** 2026-05-29  
**范围:** 全项目（frontend / backend / codex_check / infra / ops）

---

## P0：MVP 业务闭环（核心链路打通）

### 前端

#### 认证页面与流程
- [ ] 登录页面（`/login`）— 表单 + 调用 `/auth/login`
- [ ] 注册页面（`/register`）— 表单 + 调用 `/auth/register`
- [ ] Token 存储与管理（localStorage / memory）
- [ ] 自动刷新 access token 拦截器
- [ ] 登录状态守卫（未登录重定向到 `/login`）
- [ ] 用户信息展示与登出按钮（Header / 个人菜单）

#### 内容页面
- [ ] 文章列表页（`/articles`）— 分页浏览已接入的文章
- [ ] 文章详情页（`/articles/:id`）— 全文展示（Markdown 渲染）
- [ ] 内容来源管理页（`/sources`）— 查看/添加/删除 Feed 源
- [ ] Feed 入队操作界面（输入 URL，调用 `/ingest/feed`）
- [ ] 接入状态面板— 展示 `/ingest/status` 和 `/ingest/queue` 数据

### 后端

#### 文章与内容 API
- [ ] 文章列表 API（GET `/articles`）— 分页、排序、按来源/标签/日期过滤
- [ ] 文章详情 API（GET `/articles/:id`）
- [ ] 文章搜索 API（GET `/articles/search?q=`）
- [ ] 来源管理 CRUD（GET/POST/PUT/DELETE `/sources`）
- [ ] 标签列表 API（GET `/tags`）

#### 用户 API
- [ ] 用户资料更新（PUT `/auth/me`）— 修改昵称、密码
- [ ] 可选：头像上传

---

## P1：上线前必备

### 部署与 CI/CD
- [ ] **PostgreSQL 集成测试接入 CI** — 启动真实 PostgreSQL 执行 `test_postgres_worker_claims.py`
- [ ] **Alembic 迁移进入部署脚本** — 部署时自动执行 `alembic upgrade head`
- [ ] **Dockerfile（后端）** — 生产容器镜像构建
- [ ] **Dockerfile（前端）** — Nginx + 静态构建产物
- [ ] **docker-compose 整合** — 前后端 + 依赖一键启动
- [ ] **前端构建产物打包** — `vite build` 纳入 CI
- [ ] **OpenAPI schema 导出与校验** — CI 中保证前后端契约一致

### Worker 调度
- [ ] **Feed Worker 调度方案落地** — cron / 容器定时任务 / 独立 worker 进程
- [ ] Worker 运行频率与批大小配置化
- [ ] Worker 失败告警

### 可观测性
- [ ] **日志采集接入** — ELK / Loki / 云厂商日志服务
- [ ] 5xx 错误率告警
- [ ] 登录失败突增告警
- [ ] rate limit unavailable 告警
- [ ] worker failed 数量告警
- [ ] `/readyz` required dependency unavailable 告警

### 前端生产化
- [ ] 前端通用布局完善（侧边栏 / 面包屑 / 响应式适配）
- [ ] Loading / Empty / Error 三态组件
- [ ] 全局 Toast / 通知系统
- [ ] 前端错误监控接入（Sentry 或类似）
- [ ] 路由级代码分割（已有 `lazy`，需验证效果）
- [ ] PWA / 离线能力（可选）

---

## P2：业务增强

### RAG 与 AI 能力（Phase 3+）
- [ ] **Embedding 生成** — 文章入库后自动向量化（OpenAI / 本地模型）
- [ ] **Qdrant 向量存储与检索** — 相似文章搜索、语义查询
- [ ] **OpenAI 内容摘要** — 自动生成长文摘要
- [ ] **RAG 问答接口** — 基于已接入内容回答用户问题
- [ ] **RAG Service 边界** — 独立 service 层，不耦合路由

### 内容运营
- [ ] 文章标签自动提取（NLP / LLM）
- [ ] 文章分类 / 聚类
- [ ] 重复内容检测
- [ ] 内容质量评分
- [ ] 定时自动抓取（Feed 源定期轮询）
- [ ] 文章收藏 / 稍后读

### 后台管理
- [ ] 用户管理（管理员视角 — 列表 / 禁用 / 角色变更）
- [ ] 接入来源审核与管理
- [ ] 抓取任务手动重试 / 重新入队
- [ ] 系统运行状态仪表盘

### 认证增强
- [ ] 邮箱验证流程
- [ ] 密码重置
- [ ] 账号/IP 组合限流策略
- [ ] 设备指纹（可选）
- [ ] OAuth2 第三方登录（Google / GitHub，可选）

---

## P3：架构与质量提升

### 架构演进
- [ ] **OpenTelemetry / Prometheus 指标** — HTTP 请求耗时分位数、认证计数、限流命中数、worker 吞吐
- [ ] 更完整的后台任务平台（Celery / RQ / Arq — 如果吞吐需求超过当前 job 表方案）
- [ ] Repository 抽象层（如果业务复杂度增长到需要）
- [ ] API 版本升级策略（v1 → v2）

### 测试
- [ ] 前端组件测试覆盖业务页面
- [ ] 前端 e2e 测试（Playwright / Cypress）
- [ ] 后端集成测试覆盖真实 PostgreSQL worker claim
- [ ] API 契约测试（基于 OpenAPI schema）

### 前端体验
- [ ] 3D 动画（AuthBall 等）在恰当场景回归
- [ ] 深色模式
- [ ] 国际化（i18n）
- [ ] 自定义主题

---

## P4：codex_check 后续扩展

- [ ] 路径映射（设备 A → 设备 B 项目路径不同时的转换）
- [ ] `--overwrite`、`--keep-both` 冲突策略
- [ ] 自动检测 Codex 是否正在运行（导入前强制关闭提示）
- [ ] Windows 任务计划程序集成（定时自动 push）
- [ ] 导出包加密（AES / GPG）
- [ ] 增量同步（只同步变化的 session 文件）
- [ ] 多设备最新版本自动选择
- [ ] 简单桌面 UI（Tkinter / 系统托盘）
- [ ] Codex 插件 / 内嵌面板（CLI 模式验证稳定后再做）

---

## 优先级排序建议

| 阶段 | 核心目标 | 工作量估计 |
|------|----------|-----------|
| **P0** | 打通前后端业务闭环（可注册登录 + 查看内容） | 2-3 周 |
| **P1** | 生产部署就绪（CI + 容器化 + 告警 + Worker 调度） | 1-2 周 |
| **P2** | RAG 能力 + 内容运营 + 后台管理 | 4-6 周 |
| **P3** | 架构质量提升 + 测试加固 | 持续 |
| **P4** | codex_check 高级功能 | 按需 |

> 注：工作量估计为单人全栈开发的粗略工期，实际情况取决于并行度和需求细节。
