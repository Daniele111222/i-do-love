# AI News Hub 变更日志

> 所有重要的项目变更都将记录在此文件中。
> 遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/) 规范。

---

## [Unreleased] - 未来版本

### 计划中

#### Phase 1 (基础建设)
- [ ] 项目脚手架搭建
- [ ] 用户认证系统 MVP
- [ ] 3D 拟人化球体 MVP（眼睛跟随）
- [ ] 技术文档完善

#### Phase 2 (核心功能)
- [ ] 资讯管理完整功能
- [ ] OpenClaw 接入
- [ ] 3D 球体完整交互（捂眼、表情）
- [ ] 搜索和过滤

#### Phase 3 (AI 集成)
- [ ] RAG 知识库
- [ ] 语义搜索
- [ ] 智能问答

#### Phase 4 (智能体生态)
- [ ] 智能体注册协议
- [ ] 任务编排引擎
- [ ] 开放平台 API

---

## [v0.1.0] - 2026-03-19

### 初始版本

> 这是项目的初始版本，完成了项目文档体系的构建。

#### 新增

##### 文档体系

- `docs/README.md` - 项目总览文档
- `docs/PROJECT_CHARTER.md` - 项目章程
  - 愿景和目标定义
  - 干系人分析
  - 约束条件
  - 成功标准
- `docs/ARCHITECTURE.md` - 架构设计文档
  - 系统架构概览
  - 前后端架构设计
  - 部署架构
  - 技术选型理由
- `docs/SYSTEM_DESIGN.md` - 系统设计详述
  - 组件设计
  - 数据流设计
  - 接口设计
- `docs/API_SPEC.md` - API 规范文档
  - 认证 API（注册、登录、刷新、登出）
  - 用户 API
  - 内容 API
  - OpenClaw 接入 API
  - AI API（预留）
  - 错误响应格式
  - Rate Limiting 策略
- `docs/DATABASE_SCHEMA.md` - 数据库设计文档
  - PostgreSQL 表设计
  - Qdrant 向量集合
  - 索引设计
  - 安全策略
- `docs/SECURITY.md` - 安全设计文档
  - 认证与授权
  - API 安全
  - 数据安全
  - 输入安全
  - 基础设施安全
- `docs/AI_INTEGRATION.md` - AI 集成路线图
  - RAG 架构设计
  - LangChain 集成
  - Phase 3-4 详细计划
- `docs/DEVELOPMENT_GUIDE.md` - 开发指南
  - 环境配置
  - 代码规范
  - Git 工作流
  - 测试规范
- `docs/DEPLOYMENT.md` - 部署文档
  - 部署架构
  - Vercel/Railway 部署
  - CI/CD 配置
  - 监控和备份

##### 需求池

- `docs/requirements/BACKLOG.md` - 需求总池
  - 4 个 Epic 定义
  - 8 个 Feature 分解
  - 26 个 User Story
  - MoSCoW 优先级标注
  - T-Shirt 估算

- `docs/requirements/PRIORITY_MATRIX.md` - 优先级矩阵
  - 2x2 紧急度/重要度矩阵
  - Feature 象限分布
  - 优先级决策说明
  - 风险提示

- `docs/requirements/ROADMAP.md` - 路线图规划
  - 四阶段规划（0-6个月+）
  - 各阶段目标、交付物、里程碑
  - 资源规划
  - KPI 定义

#### 技术决策记录

| ID | 决策 | 理由 | 日期 |
|----|------|------|------|
| DEC-001 | React + TypeScript | 类型安全，生态丰富 | 2026-03-19 |
| DEC-002 | FastAPI | 高性能，异步支持，自动文档 | 2026-03-19 |
| DEC-003 | PostgreSQL + Qdrant | PostgreSQL 主数据，Qdrant 向量检索 | 2026-03-19 |
| DEC-004 | React Three Fiber | React 风格的 3D 开发 | 2026-03-19 |
| DEC-005 | JWT + Refresh Token | 标准认证方案 | 2026-03-19 |
| DEC-006 | Zustand | 轻量级状态管理 | 2026-03-19 |
| DEC-007 | LangChain | AI 编排框架预留 | 2026-03-19 |
| DEC-008 | Vercel + Railway | 前后端分离部署 | 2026-03-19 |

---

## 版本说明

### 版本号格式

采用 **语义化版本 2.0.0** 格式：
- `MAJOR.MINOR.PATCH`
- MAJOR：不兼容的 API 变更
- MINOR：向后兼容的功能新增
- PATCH：向后兼容的问题修复

### 发布状态

| 状态 | 含义 |
|------|------|
| Released | 正式发布 |
| Unreleased | 尚未发布 |
| Deprecated | 已废弃 |

---

## 更新日志格式

```markdown
## [版本号] - 发布日期

### 新增
- 功能 A
- 功能 B

### 修改
- 功能 C 的行为变更
- 性能优化

### 废弃
- 功能 D（将在 v2.0.0 移除）

### 修复
- 问题 X
- 问题 Y

### 安全
- 安全漏洞修补
```

---

## 归档

历史版本的变更日志将定期归档到 `CHANGELOG/ARCHIVE/` 目录。

---

*本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/) 规范。*
