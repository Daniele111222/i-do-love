/**
 * AuthBall 组件导出
 */

// 主组件
export { AuthBall, default } from './AuthBall';

// 类型
export type { BallState, EmotionState, AuthBallProps } from './types/authBall.types';

// 子组件（用于高级用法）
export { SphereMesh } from './scene/SphereMesh';
export { Eyes } from './scene/Eyes';
export { Eyebrows } from './scene/Eyebrows';
export { Mouth } from './scene/Mouth';
export { Hands } from './scene/Hands';
export { BallScene } from './scene/BallScene';

// Hooks（用于自定义集成）
export { useAuthBallState } from './hooks/useAuthBallState';
export { usePasswordWatch } from './hooks/usePasswordWatch';
export { useBreathing, useEnterAnimation, useSuccessAnimation, useErrorAnimation } from './hooks/useAnimation';
export { useEyeTracking } from './hooks/useEyeTracking';
export { useBlinking } from './hooks/useBlinking';
