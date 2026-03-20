/**
 * AuthBall 类型定义
 * 定义组件内部使用的所有类型
 */

/** 外部 API 状态（测试页面使用）*/
export type BallState = 'default' | 'looking' | 'shy' | 'happy';

/** 内部情绪状态（细粒度，驱动实际动画） */
export type EmotionState =
  | 'idle'           // 无奈微笑 + 平眉 + 呆滞眼
  | 'hover'          // 眨眼 + 眉毛挑动
  | 'focus-password'  // 脸红 + 眼神向下 + 手遮眼
  | 'success'        // 眉扬 + 眯眼 + D型笑 + 跳跃
  | 'error';         // 八字眉 + 嘴角下垂 + 摇头 + 变暗

/** 动画入场阶段 */
export type AnimPhase = 'entering' | 'idle';

/** 传递给各子组件的上下文 */
export interface BallContext {
  /** 当前情绪状态 */
  emotion: EmotionState;
  /** 入场/静止阶段 */
  animPhase: AnimPhase;
  /** 鼠标归一化位置 -1 to 1 */
  mouseNorm: { x: number; y: number };
  /** 是否密码框聚焦 */
  isPasswordFocused: boolean;
  /** 眨眼进度 0=睁眼, 1=闭眼 */
  blinkProgress: number;
  /** 呼吸偏移量 */
  breathOffset: number;
  /** 入场进度 0=起点, 1=完成 */
  enterProgress: number;
}

/** 组件 Props */
export interface AuthBallProps {
  /** 外部状态 */
  state?: BallState;
  /** 球体大小 Three.js 单位 */
  size?: number;
  /** CSS类名 */
  className?: string;
  /** 密码框聚焦回调 */
  onPasswordFocus?: (focused: boolean) => void;
}

/** 球体颜色配置 */
export const SPHERE_COLORS: Record<EmotionState, string> = {
  idle: '#8B7CF8',           // 淡紫蓝
  hover: '#7B6CE8',          // 稍深蓝
  'focus-password': '#F87CA8', // 粉红（脸红）
  success: '#6EE7A0',        // 薄荷绿
  error: '#5A5A7A',          // 暗灰紫
};

/** 眉毛配置 */
export interface BrowConfig {
  rotZ: number;      // 旋转角度
  posY: number;      // Y位置偏移
  innerAngle: number; // 内侧角度（八字眉用）
}

export const BROW_CONFIGS: Record<EmotionState, BrowConfig> = {
  idle: { rotZ: 0, posY: 0, innerAngle: 0 },
  hover: { rotZ: -0.15, posY: 0.05, innerAngle: -0.15 },
  'focus-password': { rotZ: 0.1, posY: 0.06, innerAngle: 0.15 },
  success: { rotZ: -0.25, posY: 0.08, innerAngle: -0.25 },
  error: { rotZ: 0.25, posY: -0.02, innerAngle: 0.35 },
};

/** 嘴巴曲线类型 */
export type MouthCurve = 'slight-smile' | 'neutral' | 'D-shape' | 'frown';

export interface MouthConfig {
  curve: MouthCurve;
  openness: number; // 0-1 张嘴程度
}

export const MOUTH_CONFIGS: Record<EmotionState, MouthConfig> = {
  idle: { curve: 'slight-smile', openness: 0 },
  hover: { curve: 'slight-smile', openness: 0 },
  'focus-password': { curve: 'neutral', openness: 0 },
  success: { curve: 'D-shape', openness: 0.8 },
  error: { curve: 'frown', openness: 0 },
};
