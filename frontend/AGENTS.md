# AI News Hub Frontend - AI 开发规范

**技术栈**: React + Vite + TypeScript + Tailwind CSS + Base UI / shadcn 风格组件  
**项目类型**: frontend-web，位于前后端分离 monorepo 的 `frontend/` 子项目  

---

## 核心开发理念

### 1. 先维护工程边界，再扩展业务
- **必须**把改动归属到页面层、组件层、服务层、路由层或样式层；禁止把 API 请求、页面状态、路由注册和 UI 细节混在同一个文件里，因为后续业务会大规模重构。
- **默认**在 `frontend/` 内闭环完成前端任务；只有接口契约需要确认或变更时才触碰 `backend/`，避免扩大回归范围。
- **业务代码宁缺毋滥**：当前只保留首页与基础框架。新增登录、注册、3D 动画、复杂状态前必须有明确业务需求，不要恢复旧的演示代码。

### 2. 单一 UI 基础层
- **统一使用** `src/components/ui/` 作为基础组件层；禁止重新创建 `src/components/common/`，因为旧 common 层已经删除，恢复它会重新制造重复组件体系。
- **新增 UI primitive** 必须遵守 `components.json` 的别名：`ui` 指向 `@/components/ui`，`utils` 指向 `@/lib/utils`。
- **Tailwind class 合并**统一使用 `src/lib/utils.ts` 的 `cn`；禁止手写字符串拼接规则，因为 shadcn/Base UI 组件依赖 class 合并处理变体冲突。

### 3. 路由和页面保持薄入口
- **所有路由**集中维护在 `src/routes/index.tsx`；禁止在页面组件内动态注册路由，因为 AI 后续扩页面时需要一个确定入口。
- **页面入口**使用 `src/pages/{PageName}/index.tsx`；页面内部复杂度上来后再新增同目录的 `components/`、`hooks/`、`types.ts`。
- **`src/App.tsx` 只消费 routes** 并提供全局 `Suspense` 与 `AppErrorBoundary`；禁止把业务页面直接写入 App。

### 4. 服务层先建立契约，不抢跑业务
- **所有 HTTP 请求**必须从 `src/services/httpClient.ts` 的 `request<TResponse, TBody>()` 发出；禁止页面组件直接调用 `fetch`，否则错误处理、base URL 和 credentials 会分散。
- **业务服务文件**新增在 `src/services/{domain}Service.ts`，并使用命名导出函数；禁止把多个业务域塞进 `httpClient.ts`。
- **接口类型**优先放在同业务域 `types.ts` 或 `src/services/types.ts`；禁止用 `any` 承接后端响应，数据契约不清会放大重构成本。

---

## 项目现状与最高优先级原则

### 项目现状
- 当前前端处于架构收敛阶段：只保留首页、布局、路由、UI primitives、HTTP client 和测试入口。
- 历史认证、注册、AuthBall 3D 动画、Zustand store、Axios 服务层已删除；后续需要时按新规则重新设计，不从旧实现回填。
- 包管理器以 `package.json` 的 `packageManager` 为准；依赖版本以 `package.json` 和 `pnpm-lock.yaml` 为准。
- Node 运行时必须满足 `package.json` 的 `engines.node`；Vite / Vitest 当前依赖在 Node 18 下无法完成构建和测试。

### 最高优先级原则（红线）

#### 1. 技术栈强制对齐
- **必须**使用 `package.json` 已声明的 React、Vite、TypeScript、Tailwind CSS、Base UI / shadcn 组件体系。
- **必须**使用满足 `engines.node` 的 Node 版本运行前端脚本；Node 18 会触发 Vite / Vitest 运行时错误。
- **禁止**新增 Redux、Zustand、React Query、SWR、Axios、Material UI、Chakra、styled-components 或第二套 UI/请求/状态库，除非用户明确批准；否则会让后续架构重构分叉。
- **必须**使用 `@/*` 指向 `src/*` 的路径别名；禁止深层跨目录相对路径，因为页面和业务域迁移时会增加改动面。

#### 2. 历史代码处理原则
- **禁止**恢复已删除的 `src/components/AuthBall/`、`src/components/AuthPageLayout/`、`src/components/common/`、旧认证 service/store；这些代码属于旧业务方案，不再作为新架构依据。
- **删除优先于兼容**：发现旧路由、旧依赖或旧测试只服务于已删除业务时，直接删除或改写到新架构，不保留无调用方的兼容层。
- **保留可复用工程骨架**：`src/routes/`、`src/layout/`、`src/components/ui/`、`src/services/httpClient.ts`、`src/styles/globals.css` 是当前前端的基础边界。

#### 3. 类型与接口规范（强制）
- **禁止**在新代码中使用 `any`；外部数据先用 `unknown` 承接，再通过类型守卫、schema 或明确类型转换收窄。
- **服务函数必须返回业务数据**，不要把未约束的 `Response`、原始 JSON 或实现细节泄漏给页面层。
- **后端字段以接口契约为准**；前端不得自行发明隐藏映射字段。字段变更必须同步类型定义和服务层调用。

#### 4. 路由与布局规范（强制）
- **必须**通过 `src/routes/index.tsx` 注册页面，并让页面挂在 `Layout` 下；否则 Header/Footer/ErrorBoundary 等应用框架会失效。
- **只注册真实页面**。没有页面实现时禁止先加 `/login`、`/register`、测试路由等占位路径，因为 Header 或 AI 后续开发会误认为功能已存在。
- **大页面使用 `React.lazy`**；当前首页已按 lazy 加载，后续页面延续此模式，避免首屏 bundle 随业务增长失控。

#### 5. 文档同步规范（强制）
- 修改公共目录、请求入口、路由模式、样式 token 或 UI 组件层级时，必须评估是否同步更新本文件。
- 发现本文件与代码不一致时，以当前代码为准并更新本文件；过期规则比没有规则更危险。

---

## 技术栈与项目结构

<!-- 易过时内容：依赖版本以 package.json 为准，目录结构变更时需同步更新 -->

### 核心技术栈

| 类别 | 技术选型 | 使用边界 |
|------|----------|----------|
| 框架 | React | 函数组件、Hooks、React Router |
| 构建 | Vite | dev server、生产构建、`/api` 开发代理 |
| 语言 | TypeScript | `src/` 内严格类型检查 |
| 样式 | Tailwind CSS | 全局 token 和主题变量集中在 `src/styles/globals.css` |
| UI primitives | Base UI / shadcn 风格组件 | 统一放在 `src/components/ui/` |
| HTTP | Fetch wrapper | 统一入口为 `src/services/httpClient.ts` |
| 测试 | Vitest + Testing Library | 测试入口在 `src/test/` |

### 当前目录结构

```text
src/
├── components/
│   ├── AppErrorBoundary.tsx
│   ├── Header/
│   └── ui/               # Base UI / shadcn 风格基础组件
├── layout/               # 应用级布局，内部使用 Outlet
├── lib/                  # 共享工具，如 cn
├── pages/
│   └── Home/             # 当前唯一业务页面
├── routes/               # 集中路由配置和 routeMeta
├── services/             # HTTP client 与后续业务服务
├── styles/               # Tailwind / shadcn tokens
└── test/                 # Vitest setup 与组件测试
```

---

## 分层开发规范

### 页面层
- 页面文件只负责组合布局、调用页面级 hooks/service、处理页面状态；禁止直接写底层请求逻辑。
- 单页面私有逻辑放在 `src/pages/{PageName}/hooks/` 或 `src/pages/{PageName}/components/`；只有跨页面复用时才提升到 `src/components/` 或 `src/services/`。
- 页面需要新增业务类型时，优先在页面目录放 `types.ts`；跨页面共享后再提升。

### 路由层
- `RoutePath` 只保留已实现页面路径。
- `routeMeta` 的 key 必须与 `RoutePath` 保持一致；新增菜单、权限或标题时从这里读取，不要在 Header 或页面里散落硬编码。
- 需要权限路由时先设计 `requiresAuth` 的消费位置，再注册受保护页面；禁止只写 meta 不实现守卫。

### 服务层
- `src/services/httpClient.ts` 只维护请求基础设施：base URL、headers、credentials、响应解析和统一错误。
- 新增业务域服务时使用 `export async function getXxx()` 这种命名函数风格，便于 tree-shaking 和测试替换。
- 认证、刷新 token、全局登录态等能力当前不存在；需要时重新设计 service + state + route guard，不要恢复旧实现。

### 状态层
- 当前项目没有全局状态库。页面局部状态默认使用 React state / reducer。
- 只有跨页面共享、生命周期明确、无法通过 URL 或服务缓存表达的状态，才允许引入全局状态方案；引入前必须得到用户确认并更新本文件。
- 禁止为单页面表单、弹窗、筛选条件创建全局 store，因为会让业务重构时状态来源不清。

### UI 与样式
- 新基础组件放在 `src/components/ui/`，并使用 `cn` 合并 `className`。
- 业务组件不要放进 `src/components/ui/`；它们应放在页面目录或业务域目录，避免污染 primitive 层。
- 主题变量、字体、shadcn token 只在 `src/styles/globals.css` 集中维护；禁止新增并行全局 CSS 文件。
- 图标优先使用 `lucide-react`；不要为常见操作手写 SVG，除非图标库不存在该语义。

---

## 检查与验证机制

### 代码提交前检查清单
- [ ] **类型检查**：运行 `pnpm run typecheck`。
- [ ] **代码风格**：运行 `pnpm run lint`。
- [ ] **单元测试**：运行 `pnpm test` 或相关 Vitest 子集。
- [ ] **生产构建**：运行 `pnpm run build`。
- [ ] **架构一致性**：确认没有恢复旧 auth/AuthBall/common 目录，没有新增未实现路由，没有绕过 `httpClient` 发请求。

### 代码审查关注点

**架构层面**
- 新文件是否位于正确层级：page、ui、layout、routes、services 是否边界清楚？
- 是否引入了新库来解决现有栈已经覆盖的问题？
- 是否把未来业务功能写成了当前框架的一部分，占用了错误位置？

**数据与服务层面**
- 请求是否统一经过 `src/services/httpClient.ts`？
- 服务返回类型是否明确，页面是否避免消费原始响应细节？
- 错误处理是否能被页面展示或边界捕获，而不是只 `console.error`？

**体验与维护层面**
- 页面是否提供 loading、error 或 empty 的合理位置？
- 组件文字是否在移动端和桌面端都不会溢出？
- 测试是否覆盖当前组件/服务的真实契约，而不是绑定旧业务文案？

---

## 公共工具与约定

- **className 合并**：统一使用 `src/lib/utils.ts` 的 `cn`。
- **HTTP 请求**：统一使用 `src/services/httpClient.ts` 的 `request`。
- **路由常量**：统一使用 `src/routes/index.tsx` 的 `RoutePath`。
- **UI primitives**：统一从 `src/components/ui/*` 引入。

---

## 已知后续事项

- `pnpm-lock.yaml` 顶层 importer 已与 `package.json` 对齐；由于当前环境无法运行 pnpm，历史解析条目将在下次 `pnpm install --lockfile-only` 后自动清理。
- 业务重构开始后，需要按真实业务域新增 `pages/{Domain}`、`services/{domain}Service.ts`、`types.ts` 和测试，不要一次性预铺空目录。
- 若重新引入认证，必须先确认后端契约，再设计 route guard、service、state 与错误处理。

---

## 本文档的维护规则

- AGENTS.md 中的每条规则必须能回答“违反它会导致什么具体后果”；无法回答的规则应删除。
- 能被 lint、类型检查或构建自动强制的规则不重复写入，除非需要解释架构原因。
- 发现文档与代码不一致时，以代码为准并更新文档。
- 新增公共组件、工具、目录或架构约定时，评估是否需要同步更新本文档。

<!-- last-verified: 2026-05-27 -->
