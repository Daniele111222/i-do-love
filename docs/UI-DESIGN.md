# AI News Hub - UI 设计文档

> 本文档定义了 AI News Hub 项目的视觉设计语言、交互规范和组件标准，确保整个项目保持一致的设计美学。

**版本**: 1.0.0  
**更新日期**: 2026-03-23  
**状态**: 已批准

---

## 目录

1. [设计原则与价值观](#1-设计原则与价值观)
2. [设计令牌 (Design Tokens)](#2-设计令牌-design-tokens)
3. [颜色系统](#3-颜色系统)
4. [字体系统](#4-字体系统)
5. [间距与布局系统](#5-间距与布局系统)
6. [动效规范](#6-动效规范)
7. [组件规范](#7-组件规范)
8. [暗色模式](#8-暗色模式)
9. [无障碍规范](#9-无障碍规范)
10. [图标规范](#10-图标规范)

---

## 1. 设计原则与价值观

### 1.1 品牌定位

**AI News Hub** 是一个 AI 资讯聚合平台，致力于为 AI 开发者、科技爱好者和行业从业者提供高质量的 AI 资讯服务。

### 1.2 核心价值观

| 价值观 | 描述 | 设计体现 |
|--------|------|----------|
| **科技感** | 体现 AI/科技行业的前沿性 | 天蓝色系主调、流畅动效、3D 元素 |
| **可信赖** | 提供可靠、准确的资讯 | 清晰的信息层级、克制的设计语言 |
| **易用性** | 让用户轻松获取信息 | 内容优先布局、直观的导航结构 |
| **创新性** | 独特的交互体验 | 3D 拟人化交互动画 (AuthBall) |

### 1.3 设计风格

**风格定位**: Modern Tech Minimalism（现代科技简约主义）

- 简洁的界面，减少视觉噪音
- 充足留白，让内容成为焦点
- 克制的装饰，强调功能性
- 技术细节的精致呈现（如阴影、渐变、动效）

### 1.4 设计参考

- **Apple Human Interface Guidelines** - 简洁、精致、用户为中心
- **Material Design 3** - 系统的设计语言、动效规范
- **Vercel Design** - 科技感、清晰的视觉层级

---

## 2. 设计令牌 (Design Tokens)

设计令牌是设计系统的基础，确保设计决策的一致性和可复用性。

### 2.1 颜色令牌

```css
/* globals.css 中定义 */

@theme {
  /* 主色调：天蓝色系 */
  --color-primary-50: #f0f9ff;
  --color-primary-100: #e0f2fe;
  --color-primary-200: #bae6fd;
  --color-primary-300: #7dd3fc;
  --color-primary-400: #38bdf8;
  --color-primary-500: #0ea5e9;  /* 主品牌色 */
  --color-primary-600: #0284c7;
  --color-primary-700: #0369a1;
  --color-primary-800: #075985;
  --color-primary-900: #0c4a6e;
}
```

### 2.2 语义化颜色令牌

| 令牌名称 | 用途 | Light Mode | Dark Mode |
|----------|------|------------|-----------|
| `color-bg-base` | 页面背景 | `#242424` | `#242424` |
| `color-bg-surface` | 卡片/容器背景 | `#ffffff` | `#1f2937` |
| `color-bg-elevated` | 悬浮元素背景 | `#f9fafb` | `#374151` |
| `color-text-primary` | 主要文本 | `rgba(255,255,255,0.87)` | `rgba(255,255,255,0.87)` |
| `color-text-secondary` | 次要文本 | `rgba(255,255,255,0.6)` | `rgba(255,255,255,0.6)` |
| `color-border` | 边框色 | `#e5e7eb` | `#374151` |
| `color-primary` | 主品牌色 | `#0ea5e9` | `#38bdf8` |
| `color-success` | 成功状态 | `#10b981` | `#34d399` |
| `color-warning` | 警告状态 | `#f59e0b` | `#fbbf24` |
| `color-error` | 错误状态 | `#ef4444` | `#f87171` |

### 2.3 阴影令牌

| 令牌名称 | 用途 | CSS 值 |
|----------|------|--------|
| `shadow-sm` | 轻微悬浮 | `0 1px 2px 0 rgb(0 0 0 / 0.05)` |
| `shadow-md` | 卡片悬浮 | `0 4px 6px -1px rgb(0 0 0 / 0.1)` |
| `shadow-lg` | 弹窗/模态框 | `0 10px 15px -3px rgb(0 0 0 / 0.1)` |
| `shadow-glow` | 品牌光晕效果 | `0 0 20px rgba(14, 165, 233, 0.3)` |

### 2.4 圆角令牌

| 令牌名称 | 用途 | CSS 值 |
|----------|------|--------|
| `radius-sm` | 小元素（标签） | `0.25rem (4px)` |
| `radius-md` | 按钮、输入框 | `0.5rem (8px)` |
| `radius-lg` | 卡片 | `0.75rem (12px)` |
| `radius-xl` | 大容器 | `1rem (16px)` |
| `radius-full` | 圆形元素 | `9999px` |

---

## 3. 颜色系统

### 3.1 品牌色板 (Primary)

品牌色采用天蓝色 (Sky Blue) 系列，传达科技、专业、可信赖的品牌形象。

```
Primary Color Palette
├── #0ea5e9 (Primary 500) - 主品牌色
├── #0284c7 (Primary 600) - 按钮 hover
└── #0369a1 (Primary 700) - 按钮 active
```

**使用场景**:
- 主要按钮 (Primary Button)
- 链接和强调文字
- 图标 (当需要品牌色时)
- 活跃状态指示

### 3.2 中性色板 (Neutral)

中性色用于文本、背景和边框，确保良好的可读性和层次感。

```
Neutral Palette (Gray)
├── 50  #f9fafb  - 最浅背景
├── 100 #f3f4f6  - 次浅背景
├── 200 #e5e7eb  - 边框 (light)
├── 300 #d1d5db  - 次要边框
├── 400 #9ca3af  - 占位符文字
├── 500 #6b7280  - 次要文字
├── 600 #4b5563  - 次要文字 (dark)
├── 700 #374151  - 深色模式边框
├── 800 #1f2937  - 深色模式表面
└── 900 #111827  - 最深文字/背景
```

### 3.3 功能色板 (Semantic)

```
Functional Colors
├── Success   #10b981 / #34d399 (dark)
├── Warning   #f59e0b / #fbbf24 (dark)
├── Error     #ef4444 / #f87171 (dark)
└── Info      #3b82f6 / #60a5fa (dark)
```

### 3.4 颜色对比度要求

| 文本类型 | 最小对比度 | 适用场景 |
|----------|------------|----------|
| 主要文本 | 4.5:1 (AA) | 正文、标题 |
| 次要文本 | 3:1 (AA Large) | 辅助说明文字 |
| 大文本 | 3:1 (AA) | 14px+ 粗体或 18px+ 常规 |
| 组件边界 | 3:1 (AA) | 输入框、按钮边框 |

### 3.5 颜色使用规范

**Do:**
- 使用语义化颜色令牌，而非直接使用 hex 值
- 在暗色模式下使用较浅、较不饱和的色调
- 确保文字与背景的对比度符合 WCAG AA 标准

**Don't:**
- 不要仅用颜色传达信息（同时使用图标或文字）
- 不要在同一个界面使用超过 3 种品牌色变体
- 不要使用纯黑 (#000) 或纯白 (#fff)，使用深灰和米白更优雅

---

## 4. 字体系统

### 4.1 字体族

```css
/* globals.css */
font-family: Inter, system-ui, Avenir, Helvetica, Arial, sans-serif;
```

**字体优先级**:
1. `Inter` - 优化的屏幕字体，现代、清晰
2. `system-ui` - 系统默认界面字体
3. `Avenir` - 备用衬线字体（部分 Apple 设备）
4. `Helvetica Neue` - 经典无衬线
5. `Arial` - 广泛兼容性
6. `sans-serif` - 最终回退

### 4.2 字体尺度 (Type Scale)

```
Type Scale
├── display   3rem / 48px  - Hero 标题
├── h1        2.25rem / 36px - 页面标题
├── h2        1.875rem / 30px - 区块标题
├── h3        1.5rem / 24px  - 卡片标题
├── h4        1.25rem / 20px - 小标题
├── body-lg   1.125rem / 18px - 引导文字
├── body      1rem / 16px     - 正文 (基准)
├── body-sm   0.875rem / 14px - 辅助文字
└── caption   0.75rem / 12px  - 标签、备注
```

### 4.3 行高 (Line Height)

| 用途 | 行高值 | 适用场景 |
|------|--------|----------|
| `leading-none` | 1 | 紧凑列表、标签 |
| `leading-tight` | 1.25 | 标题 |
| `leading-normal` | 1.5 | 正文 |
| `leading-relaxed` | 1.75 | 长文本阅读 |

### 4.4 字重 (Font Weight)

| 字重 | 数值 | 适用场景 |
|------|------|----------|
| `font-light` | 300 | 装饰性文字 |
| `font-normal` | 400 | 正文 |
| `font-medium` | 500 | 标签、按钮 |
| `font-semibold` | 600 | 副标题、次要标题 |
| `font-bold` | 700 | 主要标题、强调 |

### 4.5 字体使用规范

**Do:**
- 使用 16px 作为正文基准字号（避免 iOS 自动缩放）
- 限制每行字符数在 60-75 之间
- 使用 `font-display: swap` 确保字体加载时不阻塞

**Don't:**
- 不要使用 12px 以下的字号作为正文
- 不要使用纯粗体 (700) 作为大段落正文
- 不要混用多种字体族

---

## 5. 间距与布局系统

### 5.1 间距尺度 (Spacing Scale)

基于 4px 网格系统：

```
Spacing Scale (4px Base)
├── 0     0px
├── 1     0.25rem / 4px   - 微调
├── 2     0.5rem / 8px    - 元素内紧凑间距
├── 3     0.75rem / 12px  - 小间距
├── 4     1rem / 16px     - 基准间距
├── 5     1.25rem / 20px  - 中等间距
├── 6     1.5rem / 24px   - 组件内标准间距
├── 8     2rem / 32px     - 区块间距
├── 10    2.5rem / 40px   - 大区块间距
├── 12    3rem / 48px     - 页面区块间距
├── 16    4rem / 64px     - 大型区块
└── 20    5rem / 80px     - Hero 区域
```

### 5.2 布局容器

```css
/* 容器宽度 */
.container-sm   max-width: 640px;
.container-md   max-width: 768px;
.container-lg   max-width: 1024px;
.container-xl   max-width: 1280px;
.container-2xl  max-width: 1536px;
.container-full max-width: 100%;
```

**使用方式**:
```html
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
  <!-- 内容 -->
</div>
```

### 5.3 网格系统

**断点系统**:
```
Breakpoints
├── sm    640px   - 手机横屏
├── md    768px   - 平板竖屏
├── lg    1024px  - 平板横屏/小笔记本
├── xl    1280px  - 桌面
├── 2xl   1536px  - 大桌面
└── max   无最大值限制
```

**网格规范**:
- 页面使用 12 列网格
- 卡片布局使用响应式网格 (`grid-cols-1 md:grid-cols-2 lg:grid-cols-3`)
- 移动端优先，单列布局

### 5.4 Z-Index 层级

```
Z-Index Scale
├── z-0     0    - 默认
├── z-10   10    - 静态元素
├── z-20   20    - 悬浮元素 (dropdown)
├── z-30   30    - 粘性元素 (sticky header)
├── z-40   40    - 固定元素 (fixed header)
├── z-50   50    - 模态框背景
├── z-modal 100  - 模态框内容
└── z-toast 1000 - Toast 通知
```

---

## 6. 动效规范

### 6.1 动效原则

1. **功能性** - 每个动效都应有其目的，传达信息或提供反馈
2. **一致性** - 整个应用使用相同的动效模式和时长
3. **性能** - 使用 `transform` 和 `opacity` 实现，避免触发重排
4. **可访问性** - 尊重用户的 `prefers-reduced-motion` 设置

### 6.2 时长规范 (Duration)

| 动效类型 | 时长 | 示例 |
|----------|------|------|
| 微交互 | 150ms | 按钮 hover、输入框 focus |
| 状态切换 | 200ms | 展开/折叠、颜色变化 |
| 页面过渡 | 300ms | 页面切换、模态框 |
| 复杂动画 | 400ms | 大型组件进入/退出 |

**禁止**:
- 避免使用 500ms 以上的单次动效
- 避免线性 (linear) 缓动函数

### 6.3 缓动函数 (Easing)

```css
/* 常用缓动函数 */
ease-out    /* 进入动画 - 快速开始，缓慢结束 */
ease-in     /* 退出动画 - 缓慢开始，快速结束 */
ease-in-out /* 对称动画 - 缓慢开始和结束 */

/* 示例 */
transition: all 200ms ease-out;
animation: fadeIn 300ms ease-out;
```

### 6.4 项目特有动效

```css
/* globals.css - 呼吸动画 */
--animate-breathe: breathe 3s ease-in-out infinite;

@keyframes breathe {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.05); opacity: 0.9; }
}
```

**使用场景**:
- AuthBall 3D 球体的呼吸效果
- Loading 状态的柔和脉动
- Hero 区域的视觉焦点引导

### 6.5 动效规范详解

#### 6.5.1 悬浮状态 (Hover)

```css
/* 按钮悬浮 */
.button {
  transition: background-color 200ms ease-out, 
              transform 150ms ease-out;
}
.button:hover {
  transform: translateY(-1px); /* 轻微上浮 */
}
.button:active {
  transform: translateY(0); /* 按下时回位 */
}
```

#### 6.5.2 模态框/弹窗

```css
/* 进入动画 */
.modal-enter {
  opacity: 0;
  transform: scale(0.95);
}
.modal-enter-active {
  opacity: 1;
  transform: scale(1);
  transition: opacity 300ms ease-out, transform 300ms ease-out;
}

/* 退出动画 (更快) */
.modal-exit {
  opacity: 1;
  transform: scale(1);
}
.modal-exit-active {
  opacity: 0;
  transform: scale(0.95);
  transition: opacity 200ms ease-in, transform 200ms ease-in;
}
```

#### 6.5.3 列表项交错进入

```css
/* 使用 stagger 实现交错效果 */
.list-item:nth-child(1) { animation-delay: 0ms; }
.list-item:nth-child(2) { animation-delay: 50ms; }
.list-item:nth-child(3) { animation-delay: 100ms; }
/* ... */
```

#### 6.5.4 页面过渡

```css
/* 页面切换使用淡入淡出 + 轻微位移 */
.page-enter {
  opacity: 0;
  transform: translateY(10px);
}
.page-enter-active {
  opacity: 1;
  transform: translateY(0);
  transition: opacity 300ms ease-out, transform 300ms ease-out;
}
```

### 6.6 3D 动画规范 (AuthBall)

**性能要求**:
- 目标帧率: 60fps
- 使用 `useFrame` 而非 `setInterval`
- 材质和几何体复用

**动画交互**:
- 眼神跟随鼠标移动
- 密码输入时的表情变化
- 眨眼动画 (3-5秒间隔)

### 6.7 可访问性考虑

```css
/* 尊重减少动画偏好 */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 7. 组件规范

### 7.1 组件分类

| 类型 | 目录 | 说明 |
|------|------|------|
| 页面组件 | `src/pages/` | 完整页面，包含业务逻辑 |
| 公共组件 | `src/components/` | 多页面复用 |
| 公共 UI | `src/components/common/` | 通用原子组件 |
| 布局组件 | `src/layout/` | 页面布局框架 |
| 3D 组件 | `src/components/AuthBall/` | 3D 拟人化动画 |

### 7.2 组件文件结构

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

### 7.3 按钮组件 (Button)

**文件位置**: `src/components/common/Button.tsx`

**变体 (Variant)**:
| 变体 | 用途 | 样式 |
|------|------|------|
| `primary` | 主要操作 | 天蓝色实心背景 |
| `secondary` | 次要操作 | 灰色实心背景 |
| `outline` | 边框样式 | 透明背景 + 边框 |
| `ghost` | 极简样式 | 无背景，hover 时显示 |
| `danger` | 危险操作 | 红色实心背景 |

**尺寸 (Size)**:
| 尺寸 | 内边距 | 字号 |
|------|--------|------|
| `sm` | px-3 py-1.5 | text-sm |
| `md` | px-4 py-2 | text-base |
| `lg` | px-6 py-3 | text-lg |

**状态**:
- Default / Hover / Active / Disabled / Loading

**使用示例**:
```tsx
<Button variant="primary" size="md" onClick={handleClick}>
  提交
</Button>

<Button variant="outline" size="sm" loading={isSubmitting}>
  保存中...
</Button>
```

### 7.4 卡片组件 (Card)

**文件位置**: `src/components/common/Card.tsx`

**结构**:
```
Card
├── Header (可选)
│   ├── Title
│   ├── Subtitle
│   └── HeaderAction
├── Content
└── Footer (可选)
```

**变体**:
- Default: 白色背景 + 轻微阴影
- Hoverable: 添加 hover 阴影效果

**使用示例**:
```tsx
<Card title="文章标题" subtitle="2024-01-01" hoverable>
  <Card.Content>
    <p>文章摘要内容...</p>
  </Card.Content>
</Card>
```

### 7.5 输入框组件 (Input)

**文件位置**: `src/components/common/Input.tsx`

**功能特性**:
- 标签 (Label)
- 提示文字 (Hint)
- 错误信息 (Error)
- 左右图标 (LeftIcon / RightIcon)
- 密码显示切换 (Password toggle)
- 加载状态 (Loading)

**尺寸**:
| 尺寸 | 内边距 | 字号 |
|------|--------|------|
| `sm` | px-3 py-1.5 | text-sm |
| `md` | px-4 py-2 | text-base |
| `lg` | px-5 py-3 | text-lg |

**状态**:
- Default / Focus / Error / Disabled / Loading

**使用示例**:
```tsx
<Input
  label="邮箱地址"
  type="email"
  placeholder="请输入邮箱"
  error={errors.email}
  hint="我们将发送验证邮件到此地址"
/>
```

### 7.6 头部导航 (Header)

**文件位置**: `src/components/Header.tsx`

**内容**:
- Logo / 品牌名称
- 导航链接
- 用户状态 (登录/登出)

**规范**:
- 固定高度: 64px (h-16)
- 背景: 白色 / 深灰色 (暗色模式)
- 轻微阴影区分层级

### 7.7 布局组件 (Layout)

**文件位置**: `src/layout/Layout.tsx`

**结构**:
```
Layout
├── Header (固定)
├── Main (flex-1, 内容区)
└── Footer (固定)
```

**背景规范**:
```css
/* 使用渐变背景增加层次感 */
bg-gradient-to-br from-gray-50 to-gray-100
dark: from-gray-900 dark:to-gray-800
```

### 7.8 3D 认证球 (AuthBall)

**文件位置**: `src/components/AuthBall/`

**设计理念**:
- "复杂内心戏"的拟人化角色
- 默认表情: "礼貌而尴尬的微笑" + "微微下压的眉毛" + "呆滞但专注的眼神"

**交互特性**:
- 眼神跟随鼠标
- 密码输入时的表情变化
- 眨眼动画

**使用场景**:
- 登录页
- 注册页
- 认证相关流程

---

## 8. 暗色模式

### 8.1 设计原则

1. **不反转** - 暗色模式使用较浅、较不饱和的色调，而非简单的颜色反转
2. **对比度** - 确保主要文本对比度 ≥ 4.5:1，次要文本 ≥ 3:1
3. **一致性** - 与亮色模式保持相同的视觉层级和品牌表达

### 8.2 暗色模式颜色映射

| 亮色模式 | 暗色模式 | 用途 |
|----------|----------|------|
| `#ffffff` | `#1f2937` | 卡片背景 |
| `#f9fafb` | `#374151` | 悬浮背景 |
| `#e5e7eb` | `#4b5563` | 边框 |
| `#6b7280` | `#9ca3af` | 次要文本 |
| `#0ea5e9` | `#38bdf8` | 品牌色 (暗色模式较亮) |

### 8.3 Tailwind CSS 暗色模式

项目使用 `class` 策略的暗色模式，通过 `dark:` 前缀指定暗色样式。

```tsx
// Tailwind 配置 (tailwind.config.js 或 CSS)
<div className="bg-white dark:bg-gray-800 text-gray-900 dark:text-white">
  内容
</div>
```

### 8.4 组件暗色模式示例

```tsx
// Card 组件
<div className={`
  bg-white dark:bg-gray-800 
  border border-gray-200 dark:border-gray-700
  rounded-xl shadow-sm
`}>
  内容
</div>

// Button 组件
<button className={`
  bg-primary-600 text-white
  hover:bg-primary-700
  dark:bg-primary-500 dark:hover:bg-primary-600
`}>
  按钮
</button>
```

### 8.5 暗色模式测试清单

- [ ] 主要文本对比度 ≥ 4.5:1
- [ ] 次要文本对比度 ≥ 3:1
- [ ] 边框在两种模式下都可见
- [ ] 品牌色在暗色模式下足够亮
- [ ] 悬浮状态在两种模式下都有反馈
- [ ] 无纯黑/纯白背景

---

## 9. 无障碍规范

### 9.1 颜色与对比度

- 主要文本与背景: 最小 4.5:1 对比度
- 大文本 (14px+ bold 或 18px+ regular): 最小 3:1
- UI 组件边界: 最小 3:1

### 9.2 焦点状态

```css
/* 所有可交互元素必须有可见焦点指示 */
:focus-visible {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
}
```

**使用示例**:
```tsx
<button className="focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2">
  按钮
</button>
```

### 9.3 表单无障碍

- 所有输入框必须有可见标签
- 错误信息必须与输入框关联
- 支持键盘导航

```tsx
<label htmlFor="email" className="text-sm font-medium">
  邮箱地址
</label>
<input
  id="email"
  type="email"
  aria-invalid={!!errors.email}
  aria-describedby={errors.email ? `${id}-error` : undefined}
/>
{errors.email && (
  <p id={`${id}-error`} className="text-sm text-red-500">
    {errors.email}
  </p>
)}
```

### 9.4 动画无障碍

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### 9.5 ARIA 规范

| 场景 | ARIA 属性 |
|------|-----------|
| 图标按钮 | `aria-label="关闭"` |
| 模态框 | `role="dialog"`, `aria-modal="true"` |
| 活跃菜单项 | `aria-current="page"` |
| 加载状态 | `aria-busy="true"` |
| 错误提醒 | `role="alert"` |

---

## 10. 图标规范

### 10.1 图标选择

**优先使用**:
- Heroicons (outline 风格)
- Lucide React

**禁止使用**:
- Emoji 作为图标
- 混合多种图标库

### 10.2 图标尺寸

| 尺寸 | 用途 | CSS 类 |
|------|------|--------|
| `icon-xs` | 16px | `w-4 h-4` |
| `icon-sm` | 20px | `w-5 h-5` |
| `icon-md` | 24px | `w-6 h-6` |
| `icon-lg` | 32px | `w-8 h-8` |
| `icon-xl` | 40px | `w-10 h-10` |

### 10.3 图标使用示例

```tsx
import { Heroicons } from '...';

// 在按钮中
<Button leftIcon={<Heroicons.ArrowLeftIcon className="w-5 h-5" />}>
  返回
</Button>

// 独立图标
<span className="text-gray-400">
  <Heroicons.InformationCircleIcon className="w-6 h-6" />
</span>
```

### 10.4 图标颜色

| 场景 | 颜色 |
|------|------|
| 主要图标 | `text-primary-600` |
| 次要图标 | `text-gray-400` |
| 暗色模式 | `dark:text-gray-300` |
| 悬浮状态 | `group-hover:text-primary-600` |

---

## 附录 A：设计系统文件结构

```
frontend/src/
├── styles/
│   └── globals.css          # 全局样式 + Design Tokens
├── components/
│   ├── common/              # 通用组件
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   └── Input.tsx
│   ├── Header.tsx
│   └── AuthBall/            # 3D 组件
│       ├── AuthBall.tsx
│       ├── types/
│       ├── scene/
│       └── hooks/
├── layout/
│   └── Layout.tsx
├── pages/
│   └── ...
```

## 附录 B：快速参考

### 颜色令牌
```css
--color-primary-500  /* 主品牌色 */
--color-gray-50 ~ 900 /* 中性色 */
--color-success      /* 成功 */
--color-warning       /* 警告 */
--color-error         /* 错误 */
```

### 间距参考
```
4px   基准
8px   紧凑
16px  标准
24px  中等
32px  大
48px  特大
```

### 动效时间
```
150ms  微交互
200ms  状态切换
300ms  页面过渡
400ms  复杂动画
```

---

**文档维护**: 本文档应随项目迭代持续更新。重大设计变更需经过设计评审。

**最后更新**: 2026-03-23
