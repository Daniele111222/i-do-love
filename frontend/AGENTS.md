# AI News Hub - Frontend

**技术栈**: React 19 + Vite 8 + TypeScript 5 + Tailwind CSS 4 + React Three Fiber
**项目类型**: Web 应用（支持响应式）
**分支**: main

---

## 🎯 核心开发理念

### 1. 声明式编程与组件化思维

- **组件化设计**：高内聚低耦合、Props 接口清晰、开闭原则
- **声明式 UI**：基于状态渲染 UI，使用 React Hooks 管理状态与副作用
- **条件渲染**：使用早期返回或三元表达式，避免深层嵌套

### 2. 3D 可视化开发能力

- 使用 `@react-three/fiber` 和 `@react-three/drei` 实现 3D 渲染
- 理解 Three.js 场景图（Scene、Camera、Renderer）
- **3D 动画原则**：60fps 目标，材质/几何体复用，使用 `useFrame` 而非 `setInterval`

### 3. 代码质量与可维护性

- **防御性编程**：外部数据判空、边界条件处理、错误边界
- **可测试性**：业务逻辑抽离为纯函数，副作用集中管理

---

## ⚠️ 最高优先级原则（红线）

### 1. 技术栈强制对齐
- **必须**：React 19 + TypeScript + Vite + Tailwind CSS 4
- **禁止**：引入新 UI 库（如 Material-UI、Chakra）

### 2. 类型与参数规范（强制）
- **禁止 `any`**：使用 `unknown` + 类型守卫或明确类型
- **接口定义**：API 请求/响应、复杂对象必须使用接口定义
- **严格模式**：已开启 `noUnusedLocals`、`noUnusedParameters`

### 3. 服务层规范（强制）
- **位置**：`src/services/` 目录下
- **请求方法**：使用 `src/services/api.ts` 中封装的 Axios 实例
- **类型定义**：接口响应类型定义在 `src/types/` 目录下

### 4. 状态管理规范
- **状态管理**：使用 Zustand
- **持久化**：认证状态使用 Zustand persist，存储在 localStorage
- **禁止直接操作 localStorage**：通过 store 的 actions 操作

### 5. 代码审查同步
- 修改公共组件/hooks 后需询问是否同步到 `AGENTS.md`

### 6. 完成所有任务的时候请回复”sir，任务已经完成“

---

## 🛠 技术栈

| 类别 | 技术选型 | 说明 |
|------|---------|------|
| **框架** | React 19.x | 函数组件 + Hooks 模式 |
| **语言** | TypeScript 5.x | 严格模式 |
| **构建** | Vite 8.x | 快速开发体验 |
| **样式** | Tailwind CSS 4.x | 原子化 CSS |
| **3D** | React Three Fiber 9.x | Three.js React 封装 |
| **路由** | React Router DOM 7.x | 声明式路由 |
| **状态** | Zustand 5.x | 轻量状态管理 |
| **HTTP** | Axios 1.x | HTTP 请求库 |
| **表单** | React Hook Form 7.x | 表单状态管理 |
| **验证** | Zod 4.x | Schema 验证 |
| **动画** | Framer Motion 12.x | 交互动画 |
| **测试** | Vitest 4.x | 单元测试框架 |

---

## 📋 组件与样式规范

### 组件分类与存放位置

| 组件类型 | 存放位置 | 说明 |
|---------|---------|------|
| **页面组件** | `src/pages/` | 完整页面，包含业务逻辑 |
| **公共组件** | `src/components/` | 多页面复用 |
| **公共 UI** | `src/components/common/` | 通用原子组件 |
| **布局组件** | `src/layout/` | 页面布局框架 |

### Hooks 分类与存放位置

| Hooks 类型 | 存放位置 | 说明 |
|-----------|---------|------|
| **页面级 Hooks** | `src/pages/{PageName}/` | 与页面强绑定 |
| **公共 Hooks** | `src/hooks/` | 多页面复用 |

**命名规范**：所有 Hook 文件和函数均以 `use` 开头，使用 camelCase。

### 组件文件结构

```typescript
// 1. React 和框架导入
// 2. 第三方库
// 3. 项目内部组件
// 4. 工具函数和 Hooks
// 5. 服务层
// 6. 类型定义
// 7. 样式

export interface ComponentProps {
  /** 用户ID */
  userId: string;
  /** 是否显示标题 */
  showTitle?: boolean;
  /** 点击回调 */
  onClick?: (userId: string) => void;
}

export const Component: React.FC<ComponentProps> = ({ ... }) => {
  // 状态定义
  const [state, setState] = useState(false);

  // 事件处理
  const handleClick = () => { ... };

  // 渲染（早期返回）
  if (loading) return <Loading />;
  
  return ( ... );
};
```

**要点**：
- Props 使用 JSDoc 注释说明用途
- 使用早期返回处理加载/空状态
- 条件渲染使用三元表达式，避免深层嵌套

### 3D 组件开发规范

```typescript
// 1. Three.js 相关导入
import { useFrame } from '@react-three/fiber';
import { useRef } from 'react';
import * as THREE from 'three';

// 2. 类型定义
interface SceneProps {
  position?: [number, number, number];
}

// 3. 组件实现
export const Scene: React.FC<SceneProps> = ({ position = [0, 0, 0] }) => {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame(() => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.01;
    }
  });

  return (
    <mesh ref={meshRef} position={position}>
      <sphereGeometry args={[1, 32, 32]} />
      <meshStandardMaterial color="#4a90d9" />
    </mesh>
  );
};
```

**要点**：
- 使用 `useRef` 管理 Three.js 对象引用
- 使用 `useFrame` 进行动画（而非 `setInterval`）
- 材质和几何体复用，减少内存占用

### 样式规范

#### Tailwind CSS

- **原子化类名**：优先使用 Tailwind 内置类名
- **类名合并**：使用 `clsx` 或 `cn` 工具函数
- **响应式设计**：使用 `sm:`、`md:`、`lg:`、`xl:` 前缀

```typescript
import { clsx } from 'clsx';

const classes = clsx(
  'px-4 py-2 rounded-lg font-medium transition-colors',
  variant === 'primary' && 'bg-blue-500 text-white hover:bg-blue-600',
  className
);
```

#### CSS Module

当 Tailwind 无法满足需求时，使用 CSS Module：

```typescript
import styles from './Example.module.css';
<div className={styles.container} />
```

---

## 🔌 API 服务层

### 服务文件结构

```
src/services/
├── api.ts            # Axios 实例配置和拦截器
└── authService.ts    # 认证相关 API
```

### Axios 实例配置要点

```typescript
// src/services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
});

// 请求拦截器：注入 Token
// 响应拦截器：处理 401 重定向
```

**要点**：
- `baseURL` 从环境变量 `VITE_API_BASE_URL` 读取
- 请求拦截器注入 `Authorization: Bearer {token}`
- 响应拦截器处理 401 重定向到登录页

### 认证服务模板

```typescript
import api from './api';
import type { User, LoginRequest, LoginResponse } from '@/types/user';

export const authService = {
  login: (data: LoginRequest) =>
    api.post<LoginResponse>('/auth/login', data),
  register: (data: LoginRequest) =>
    api.post<User>('/auth/register', data),
  getCurrentUser: () =>
    api.get<User>('/auth/me'),
  logout: () =>
    api.post('/auth/logout'),
};
```

---

## 🗃 状态管理（Zustand）

### Store 编写要点

```typescript
// src/stores/authStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (user: User, token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      login: (user, token) => set({ user, token, isAuthenticated: true }),
      logout: () => set({ user: null, token: null, isAuthenticated: false }),
    }),
    {
      name: 'auth-storage',       // localStorage key
      partialize: (state) => ({   // 只持久化必要字段
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
```

**要点**：
- 使用 `persist` middleware 持久化状态
- `partialize` 控制只持久化必要字段（不持久化 loading 等临时状态）
- 禁止直接操作 localStorage，通过 actions 操作

---

## 🛣 路由配置

路由配置文件：`src/routes/index.tsx`，使用 React Router v7。

---

## ✅ 检查与验证机制

### 提交前检查清单

- [ ] 类型检查：无 TypeScript 错误，无 `any` 类型
- [ ] 代码风格：通过 ESLint 检查
- [ ] 文件命名：组件 PascalCase，hooks camelCase
- [ ] 样式规范：优先 Tailwind 类名，复杂样式用 CSS Module
- [ ] 性能优化：无冗余渲染，合理使用 useMemo/useCallback
- [ ] 错误处理：API 调用有错误处理逻辑
- [ ] 3D 性能：使用 `useFrame` 而非 `setInterval`

### 代码审查关注点

**架构**：组件职责单一？状态管理合理？业务逻辑抽离？

**性能**：无冗余渲染？3D 资源正确清理？图片懒加载？路由按需加载？

**体验**：加载状态友好？错误提示清晰？空状态有引导？

---

## 📚 参考资源

- [React 文档](https://react.dev/)
- [Vite 文档](https://vitejs.dev/)
- [TypeScript 文档](https://www.typescriptlang.org/)
- [Tailwind CSS 文档](https://tailwindcss.com/)
- [React Three Fiber 文档](https://docs.pmnd.rs/react-three-fiber)
- [React Router 文档](https://reactrouter.com/)
- [Zustand 文档](https://zustand.docs.pmnd.se/)
- [React Hook Form 文档](https://react-hook-form.com/)
- [Zod 文档](https://zod.dev/)

---
