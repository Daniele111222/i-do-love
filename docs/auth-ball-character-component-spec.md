# AuthBall Character Component 开发文档

## 1. 目标

为认证页提供一个独立的角色组件 `AuthBall`，用于登录页和注册页的品牌化交互展示，并支持以下两项核心行为：

1. 角色眼睛始终跟随用户鼠标光标。
2. 当用户在登录或注册流程中输入密码时，角色闭眼。

这个组件不是一次性的页面特效，而是认证体验中的可复用 UI 角色组件。

## 2. 当前项目现状

项目中已经存在 `AuthBall` 的基础实现和大部分交互骨架：

- 组件入口：`frontend/src/components/AuthBall/AuthBall.tsx`
- 状态机：`frontend/src/components/AuthBall/hooks/useAuthBallState.ts`
- 密码框监听：`frontend/src/components/AuthBall/hooks/usePasswordWatch.ts`
- 眼睛渲染：`frontend/src/components/AuthBall/scene/Eyes.tsx`
- 认证页：
  - `frontend/src/pages/login/index.tsx`
  - `frontend/src/pages/Register/index.tsx`

### 已有能力

1. `AuthBall.tsx`
   - 已监听全局 `mousemove`
   - 已计算归一化鼠标坐标 `mouseNorm`
   - 已调用 `usePasswordWatch()`
   - 已将 `emotion`、`isEyeTrackingActive`、`mouseNorm` 传给 3D 场景

2. `usePasswordWatch.ts`
   - 已支持监听 `input[type="password"]` 的 `focus/blur`
   - 已支持 DOM 动态新增密码框
   - 已返回 `isPasswordFocused`

3. `useAuthBallState.ts`
   - 已支持 `focus-password` 状态
   - 已约定 `focus-password` 优先级高于 `hover/idle`

4. `Eyes.tsx`
   - 已支持瞳孔跟随
   - 已支持根据 `focus-password` 向下看
   - 已支持眨眼动画结构

### 当前缺口

1. 登录页和注册页还没有真正渲染 `AuthBall`。
2. 目前“闭眼”的触发更接近“焦点状态 + 眨眼/遮眼风格”，需要明确升级为“密码输入期间稳定闭眼”。
3. 鼠标跟随是全局窗口级别，文档上需要明确是否保留这种设计，还是改为仅在认证布局区域内跟随。
4. 现有 `usePasswordWatch` 基于原生 DOM 查询，能工作，但在 React 表单上下文里不是最强约束方案，需要明确后续接入规范。

## 3. 角色组件定义

### 组件职责

`AuthBall` 负责：

- 渲染认证角色的 3D 外观
- 接收或推导当前交互状态
- 根据鼠标位置更新眼球朝向
- 根据密码输入状态切换闭眼表现

`AuthBall` 不负责：

- 管理表单校验
- 管理登录/注册提交逻辑
- 决定页面文案和布局

## 4. 交互规则

### 4.1 鼠标跟随

目标行为：

- 页面加载后，角色进入默认待机状态
- 用户移动鼠标时，角色双眼持续朝向光标
- 眼球移动应该有轻微缓动，而不是瞬间跳转
- 鼠标离开窗口后，眼球缓慢回中

建议规则：

- 只移动瞳孔，不移动整个眼白
- 水平方向幅度大于垂直方向幅度
- 设置最大偏移，避免眼神过度夸张
- 鼠标跟随在 `focus-password` 期间禁用

### 4.2 密码输入闭眼

目标行为：

- 用户聚焦到任意密码框时，角色闭眼
- 用户在密码框中持续输入时，角色保持闭眼
- 用户离开密码框后，角色恢复默认睁眼状态

这里的“typing my password”在产品实现上建议解释为：

- `password input focused` 即进入闭眼态
- `blur password input` 即退出闭眼态

原因：

1. 这是最稳定的产品体验。
2. 用户在密码输入时通常会间歇停顿，仅监听 `keydown` 会导致眼睛频繁开合。
3. 当前项目的 `usePasswordWatch` 已经是基于 focus/blur 设计，改造成本最低。

如果后续确实需要更严格的“仅输入瞬间闭眼”，可以在此基础上增加键盘输入节流，但不建议作为首版。

## 5. 推荐状态模型

基于当前项目，建议将状态收敛为以下优先级：

1. `error`
2. `success`
3. `focus-password`
4. `looking`
5. `idle`

### 状态语义

- `idle`
  - 默认待机
  - 允许轻微眨眼
  - 鼠标移动时进入眼神跟随

- `looking`
  - 明确启用鼠标跟随
  - 可用于测试页或强制交互展示

- `focus-password`
  - 密码框聚焦时触发
  - 停止鼠标跟随
  - 眼睛闭合
  - 可叠加轻微害羞/低头，但首版优先保证“闭眼”动作清楚

- `success`
  - 登录/注册成功后的瞬时表情

- `error`
  - 登录/注册失败后的瞬时表情

## 6. 推荐 API 设计

现有 `AuthBallProps`：

- `state?: BallState`
- `size?: number`
- `className?: string`
- `onPasswordFocus?: (focused: boolean) => void`

建议升级为：

```ts
interface AuthBallProps {
  state?: BallState;
  size?: number;
  className?: string;
  trackCursor?: boolean;
  passwordMode?: 'auto-watch' | 'controlled';
  isPasswordActive?: boolean;
  onPasswordFocus?: (focused: boolean) => void;
}
```

### 含义

- `trackCursor`
  - 是否开启眼睛跟随光标
  - 默认 `true`

- `passwordMode`
  - `auto-watch`: 继续使用内部 `usePasswordWatch`
  - `controlled`: 由父组件显式传入 `isPasswordActive`

- `isPasswordActive`
  - 在 `controlled` 模式下使用
  - 用于从登录/注册表单直接控制闭眼

### 为什么建议支持 `controlled`

虽然 `auto-watch` 能快速接入，但认证页是 React 表单，长期看更推荐父组件显式传值：

- 依赖更清晰
- 更容易测试
- 更容易支持多表单场景
- 避免未来页面上有多个密码框组件时产生误判

## 7. 实施方案

## 7.1 第一阶段：最小可用接入

目标：不大改现有架构，快速让认证页出现可工作的角色。

步骤：

1. 在登录页和注册页布局中加入 `AuthBall`
2. 保持 `AuthBall` 内部继续使用 `usePasswordWatch`
3. 保持鼠标跟随逻辑使用 `window.mousemove`
4. 将 `focus-password` 的视觉表现改成“眼睛闭合优先”

适合当前项目的原因：

- 改动小
- 复用现有代码最多
- 能最快验证视觉和交互效果

## 7.2 第二阶段：推荐落地方案

目标：让角色状态由认证页显式驱动，提升可靠性。

步骤：

1. 登录页、注册页在密码字段上维护 `isPasswordActive`
2. `AuthBall` 增加 `passwordMode="controlled"` 和 `isPasswordActive`
3. `usePasswordWatch` 仅保留给测试页或兼容模式
4. 后续如需错误态/成功态，也由页面显式传给 `AuthBall`

### 父组件示例

```tsx
const [isPasswordActive, setIsPasswordActive] = useState(false);

<Input
  type="password"
  onFocus={() => setIsPasswordActive(true)}
  onBlur={() => setIsPasswordActive(false)}
/>

<AuthBall
  trackCursor
  passwordMode="controlled"
  isPasswordActive={isPasswordActive}
/>
```

## 8. 认证页接入建议

### 登录页

当前文件：`frontend/src/pages/login/index.tsx`

建议改成双栏布局：

- 左侧：`AuthBall`
- 右侧：登录卡片

最低要求：

- 页面中真实渲染 `AuthBall`
- 密码字段可驱动闭眼

### 注册页

当前文件：`frontend/src/pages/Register/index.tsx`

建议与登录页保持一致的认证布局：

- 左侧：`AuthBall`
- 右侧：注册卡片

特殊点：

- 注册页存在两个密码字段
- 任一密码字段聚焦时，都应触发闭眼

## 9. Eyes 组件开发要求

当前文件：`frontend/src/components/AuthBall/scene/Eyes.tsx`

需要明确这几个行为：

### 睁眼态

- 眼白保持稳定
- 瞳孔根据 `pupilTarget` 跟随
- 使用 `lerp` 实现平滑追踪

### 闭眼态

- `focus-password` 时不只是“向下看”，而是眼睑真正覆盖眼睛
- 闭眼优先级高于鼠标跟随
- 闭眼时瞳孔可以停止更新或归中

### 推荐实现规则

```ts
const shouldCloseEyes = emotion === 'focus-password';
const shouldTrack = isTracking && !shouldCloseEyes;
```

并将眼睑闭合程度和 `blinkProgress` 解耦：

- 普通眨眼：短时闭合
- 密码模式：稳定闭合

建议引入：

```ts
const eyelidClose = shouldCloseEyes ? 1 : blinkProgress;
```

这样 `focus-password` 能稳定覆盖普通 blink 逻辑。

## 10. 鼠标跟随实现要求

当前实现位于：`frontend/src/components/AuthBall/AuthBall.tsx`

现状：

- 使用 `window.addEventListener('mousemove')`
- 通过窗口尺寸计算归一化坐标

建议保留首版实现，但明确边界：

- 优点：简单、全局一致、开发快
- 缺点：鼠标即使移到页面其他位置，角色也会继续盯着看

后续优化方案：

- 改为只在认证布局容器内采集鼠标位置
- 或以 `AuthBall` 容器为坐标系进行归一化

推荐后续接口：

```ts
trackingScope?: 'window' | 'container'
```

首版建议默认 `window`。

## 11. 可测试性要求

需要覆盖的测试场景：

1. 页面加载时 `AuthBall` 正常渲染
2. 鼠标移动时瞳孔目标值发生变化
3. 密码框 focus 时进入 `focus-password`
4. 密码框 blur 时退出 `focus-password`
5. 登录页密码框可驱动闭眼
6. 注册页任一密码框都可驱动闭眼

### 推荐测试分层

- 单元测试
  - `useAuthBallState`
  - `usePasswordWatch`

- 组件测试
  - `AuthBall` 接收 `isPasswordActive` 时是否正确切换状态

- 页面集成测试
  - 登录页、注册页与 `AuthBall` 的联动

## 12. 性能和体验要求

- 鼠标跟随必须使用平滑插值，不能直接跳帧
- 角色动画应可中断，密码聚焦时立即闭眼
- `focus-password` 不应和普通 blink 冲突
- WebGL 不可用时必须保留降级 UI
- 不要让角色动画阻塞表单输入

## 13. 推荐开发顺序

1. 在登录页与注册页接入 `AuthBall`
2. 保持现有 `usePasswordWatch` 跑通基础联动
3. 修改 `Eyes.tsx`，让 `focus-password` 变成真正闭眼
4. 将密码联动改成受控模式
5. 补充测试

## 14. 验收标准

完成后应满足：

1. 登录页和注册页都能看到角色组件。
2. 鼠标在页面移动时，角色眼睛始终朝向光标。
3. 聚焦任意密码输入框时，角色立即闭眼。
4. 离开密码框时，角色恢复睁眼并继续跟随光标。
5. 体验稳定，不出现频繁抖动、错位或状态闪烁。

## 15. 本次建议结论

基于当前代码，最合适的落地策略是：

1. 先保留现有 `AuthBall` 结构和 `usePasswordWatch`，快速让功能可见。
2. 但从文档和 API 设计上，明确下一步要迁移到 `controlled password state`。
3. `Eyes.tsx` 需要从“密码时向下看”升级为“密码时闭眼优先”。

这样能最大程度复用当前项目成果，同时把组件真正做成可维护的认证角色组件。
