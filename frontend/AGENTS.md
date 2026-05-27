# AI News Hub Frontend - AGENTS.md

**技术栈**: React + Vite + TypeScript + Tailwind CSS + React Three Fiber  
**项目类型**: frontend-web，位于前后端分离 monorepo 的 `frontend/` 子项目  

---

## 核心开发理念

### 1. 前端边界先于功能扩张
- **必须**先判断改动属于页面、组件、服务层、状态层还是 3D 场景层；不要把 API 请求、路由注册、全局状态和 UI 细节混在同一个文件里。
- **默认**在 `frontend/` 内闭环完成前端任务；只有接口契约必须变更时才同步触碰 `backend/`，否则会扩大回归面。
- **新增能力**优先复用已存在目录和依赖；禁止为了单个需求引入新的 UI 库、状态库或 HTTP 客户端，因为当前依赖已覆盖这些职责。

### 2. 服务层与认证链路保持单一入口
- **所有 HTTP 请求**必须经过 `src/services/api.ts` 创建的 Axios 实例；绕开该实例会丢失 `baseURL`、`withCredentials`、超时和 token 刷新逻辑。
- **认证 API**使用 `src/services/authService.ts` 中的命名异步函数风格；不要改成对象式 `authService.login()` 混用，避免调用风格分裂。
- **认证状态**由 `src/stores/authStore.ts` 对外提供；页面组件只调用 store actions，不直接拼登录、刷新、登出流程。

### 3. UI 体系要收敛而不是并行生长
- 当前同时存在 `src/components/common/` 和 `src/components/ui/`：前者是历史业务通用组件，后者是 Base UI / shadcn 风格基础组件。新增组件前必须先选定层级，不要在两个目录各造一份同名能力。
- 新增 Base UI / shadcn 风格组件时必须遵守 `components.json` 的别名：`ui` 指向 `@/components/ui`，`utils` 指向 `@/lib/utils`。
- Tailwind 类名合并统一使用 `src/lib/utils.ts` 的 `cn`，或在历史组件里沿用已存在的 `clsx` + `twMerge`；不要手写字符串拼接规则。

### 4. AuthBall 是独立 3D 子系统
- `src/components/AuthBall/` 内部按 `hooks/`、`scene/`、`types/` 分层；新增表情、动作、材质时必须把状态类型放回 `types/authBall.types.ts`，不要把配置散落在场景组件里。
- 3D 动画必须使用 React Three Fiber 的渲染循环能力；禁止用 `setInterval` 驱动场景更新，因为它会和帧循环不同步。
- `AuthBall` 已处理 WebGL 不可用和 context lost 状态；修改 Canvas 或 renderer 配置时必须保留降级展示，避免认证页白屏。

---

## 项目背景与最高优先级规则

### 项目现状
- `frontend/` 是 AI News Hub 的浏览器端项目，对接后端 `/api/v1`，开发代理配置在 `vite.config.ts`。
- 入口链路为 `src/main.tsx` -> `src/App.tsx` -> `src/routes/index.tsx`；路由集中声明，页面通过 lazy import 加载。
- 认证链路包含内存 access token、refresh token cookie、Axios 401 刷新、Zustand auth store。
- 组件体系正在从历史 `common` 组件向 `ui` primitives 过渡；维护重点是收敛边界，而不是继续复制组件。

### 最高优先级规则（红线）

#### 1. 技术栈强制对齐
- **必须**使用 `frontend/package.json` 已声明的前端技术栈和脚本；版本号以 `package.json` 与 lockfile 为准。
- **禁止**新增 Redux、React Query、SWR、Material UI、Chakra、styled-components 或第二套请求库，除非用户明确要求；否则会让状态、请求和 UI 规范分叉。
- **必须**使用 `@/*` 指向 `src/*` 的路径别名；跨层相对路径过深会降低可维护性并增加移动文件成本。

#### 2. 服务层与类型契约（强制）
- **必须**把接口请求放在 `src/services/`，把接口相关类型放在 `src/types/` 或同一业务域的 `types.ts`；页面组件不得直接调用 `axios`。
- **必须**让新服务函数返回已经解包后的业务数据或明确的响应类型；不要把未约束的 `AxiosResponse` 直接泄漏给页面层。
- **禁止**在新代码中使用 `any` 处理接口错误或响应数据；使用 `unknown`、`AxiosError` 类型守卫或明确接口类型。现有 `src/services/api.ts`、`src/services/authService.ts`、`src/stores/authStore.ts` 里的 `any` 是技术债，触碰时应顺手收窄。

#### 3. 认证 token 规则（强制）
- **必须**保留 `src/services/api.ts` 的认证入口：access token 写入内存，refresh token 走 cookie，Axios 实例开启 `withCredentials`。
- **禁止**把 access token 持久化到 `localStorage`；泄露面比内存更大，且会和当前刷新策略冲突。
- **禁止**把 `src/stores/authStore.ts` 改成 Zustand `persist` 保存 token；当前架构由服务层管理 token，store 只持有用户态和 UI 状态。

#### 4. 路由与页面注册（强制）
- **新增页面**必须在 `src/routes/index.tsx` 注册路径常量、lazy 页面组件和 `routeMeta`；不要在页面组件内动态注册路由。
- **页面入口**默认使用 `src/pages/{PageName}/index.tsx`；复杂页面再拆 `components/`、`hooks/`、`types.ts`，不要把跨页面组件塞进页面目录。
- **App 根组件**只消费 routes 并提供全局 Suspense fallback；不要在 `src/App.tsx` 里硬编码业务页面。

#### 5. 公共组件边界（强制）
- **修改 `src/components/common/` 或 `src/components/ui/` 前**必须用搜索确认现有引用；公共组件变更会影响多页面和测试。
- **新增基础 UI primitive**放入 `src/components/ui/`，使用 `@/lib/utils` 的 `cn` 与 `components.json` 约定。
- **维护历史业务组件**继续放在 `src/components/common/`，但不要在新业务里复制已有 `ui` primitive 的能力。

#### 6. 文档同步规则（强制）
- 新增公共目录、请求约定、状态管理约定、路由模式或 AuthBall 子系统规则时，必须评估是否同步更新本文件。
- 发现本文件和代码不一致时，以代码为准并更新本文件；过期规则比没有规则更危险。

---

## 项目记忆网络

| 记忆节点 | 事实 | 维护含义 |
|---|---|---|
| `frontend/package.json` | 前端依赖、脚本、包管理器入口 | 版本与命令以这里为准，AGENTS 不重复版本号 |
| `src/main.tsx` | React 根挂载、`BrowserRouter`、全局样式导入 | 不在此处放业务逻辑 |
| `src/App.tsx` | 全局 `Suspense` + routes 渲染 | 路由扩展去 `src/routes/index.tsx` |
| `src/routes/index.tsx` | `RoutePath`、lazy 页面、`routeMeta` | 所有路由集中维护 |
| `src/services/api.ts` | Axios 实例、baseURL、cookie、token 刷新 | 请求、认证和 401 处理的单一入口 |
| `src/services/authService.ts` | 登录、注册、刷新、登出服务函数 | 认证流程不要散落到页面 |
| `src/stores/authStore.ts` | Zustand 认证状态与 actions | 页面层只消费 store，不直接管 token |
| `src/types/user.ts` | 用户与认证 API 类型 | 接口契约变更时同步此处 |
| `src/components/AuthBall/` | 认证页 3D 角色子系统 | 3D 状态、场景、hooks 分层维护 |
| `src/components/ui/` | Base UI / shadcn 风格 primitives | 新 primitives 的默认落点 |
| `src/components/common/` | 历史通用业务组件 | 改动前搜索引用和测试 |
| `src/lib/utils.ts` | `cn` 类名合并工具 | Tailwind 冲突合并优先复用它 |
| `src/styles/globals.css` | Tailwind 4、shadcn token、字体与主题变量 | 设计 token 和全局样式集中维护 |

---

## 技术栈与目录结构

### 核心技术栈

| 类别 | 选型 | 使用边界 |
|---|---|---|
| 框架 | React | 函数组件、Hooks、React Router |
| 构建 | Vite | dev server、代理、生产构建 |
| 语言 | TypeScript | `src/` 内严格类型检查 |
| 样式 | Tailwind CSS | `src/styles/globals.css` 管理主题与 token |
| UI primitives | Base UI / shadcn 风格组件 | `src/components/ui/` |
| 3D | React Three Fiber / Drei / Three.js | `src/components/AuthBall/` |
| 状态 | Zustand | 当前仅认证 store |
| HTTP | Axios | `src/services/api.ts` 单例 |
| 表单与校验 | React Hook Form / Zod | 需要表单契约时优先使用 |
| 测试 | Vitest + Testing Library | `src/**/*.{test,spec}.tsx` |

### 目录结构

```text
src/
├── components/
│   ├── AuthBall/      # 3D 认证角色：hooks、scene、types 分层
│   ├── common/        # 历史通用业务组件
│   └── ui/            # Base UI / shadcn 风格基础组件
├── hooks/             # 跨页面复用 hooks
├── layout/            # 布局组件
├── lib/               # 共享工具，如 cn
├── pages/             # 页面入口
├── routes/            # 集中路由配置
├── services/          # API 请求层
├── stores/            # Zustand stores
├── styles/            # 全局样式与主题 token
├── test/              # 测试 setup 与现有用例
└── types/             # 跨模块共享类型
```

---

## 分层开发规范

### 页面层
- 页面文件负责组合组件、调用 hooks/store、处理页面态；不要直接写 Axios 请求。
- 页面有私有复杂逻辑时，放到页面目录下的 `hooks/` 或 `components/`；只有跨页面复用时才提升到 `src/hooks/` 或 `src/components/`。
- 页面需要认证信息时从 `useAuthStore` 获取；不要读取 cookie 或 `window.__ACCESS_TOKEN__`。

### 服务层
- `src/services/api.ts` 只维护请求基础设施：baseURL、headers、credentials、token 注入、刷新、错误转发。
- 业务服务文件使用命名导出函数，例如 `login`、`register`、`getCurrentUser`；保持与 `src/services/authService.ts` 一致。
- 环境变量以 `.env.example` 记录；当前 API 地址变量为 `VITE_API_BASE_URL`。

### 状态层
- 全局 store 只放跨页面共享且需要同步驱动 UI 的状态；不要把单页面表单状态提升进 Zustand。
- store action 可以调用 service，但 service 不得反向 import store；否则认证链路会形成循环依赖。
- `isLoading`、`error` 这类临时 UI 状态不要持久化。

### UI 与样式
- 新增 `src/components/ui/` 组件时使用 `cn` 合并 className，并暴露清晰的 variant / size 类型。
- 修改 `src/components/common/` 时保持既有 props 兼容；该目录已有测试直接引用 `@/components/common/Button`。
- 主题 token、字体、shadcn CSS 变量和 Tailwind `@theme` 只在 `src/styles/globals.css` 集中维护。
- 禁止新增全局 CSS 文件绕开 `globals.css`；跨页面样式分散会让主题和暗色模式失控。

### AuthBall 3D 子系统
- 新增状态先扩展 `BallState` / `EmotionState`，再补齐 `SPHERE_COLORS`、`BROW_CONFIGS`、`MOUTH_CONFIGS` 等映射。
- 场景组件放在 `src/components/AuthBall/scene/`，行为 hook 放在 `src/components/AuthBall/hooks/`。
- DOM 监听必须有 cleanup；`usePasswordWatch` 已使用 `MutationObserver` 和事件解绑，新监听逻辑必须保持同等清理。
- Canvas renderer 配置改动后必须检查桌面和窄屏页面，确认 AuthBall 非空白、未遮挡表单。

---

## 检查与验证机制

### 变更前检查
- [ ] **影响范围**: 是否触碰 `src/components/common/`、`src/components/ui/`、`src/services/api.ts`、`src/stores/authStore.ts` 或 `src/components/AuthBall/` 这类高影响文件。
- [ ] **调用方搜索**: 公共组件、store action、service 函数改名前必须搜索所有 import。
- [ ] **接口契约**: API 字段变更时同步 `src/types/`，并确认后端路径仍匹配 `/api/v1`。
- [ ] **认证安全**: 未把 token 写入 `localStorage`，未绕过 Axios 实例。

### 推荐验证命令

```bash
pnpm run lint
pnpm run build
pnpm test
```

### 代码审查关注点
- **架构**: 新代码是否放在正确层级；页面是否保持薄；公共组件是否出现重复实现。
- **契约**: service 返回类型、store state、route meta 是否一致；错误处理是否使用明确类型而不是 `any`。
- **体验**: 登录/注册流程是否有 loading、error、disabled 状态；AuthBall 降级状态是否仍可读。
- **性能**: 路由是否继续 lazy import；3D 动画是否沿用帧循环；DOM 监听是否清理。

---

## 已知技术债

- `src/services/api.ts` 和 `src/services/authService.ts` 使用 `(window as any).__ACCESS_TOKEN__`；后续触碰时应补充全局类型声明，避免继续扩散 `any`。
- `src/stores/authStore.ts` 的 `catch (error: any)` 应收窄为 `unknown` + Axios 错误判断；新增 action 不得复制该写法。
- `src/components/common/` 与 `src/components/ui/` 存在功能重叠；新增 UI 能力时必须优先收敛到一个层级。

---

## 本文档的维护规则

- AGENTS.md 中的每条规则必须能回答“违反它会导致什么具体后果”；无法回答的规则应删除。
- 能被 lint、类型检查或构建自动强制的规则不重复写入，除非需要解释架构原因。
- 发现文档与代码不一致时，以代码为准，更新文档。
- 新增公共组件、工具、目录或架构约定时，评估是否同步更新本文档。

<!-- last-verified: 2026-05-26 -->
