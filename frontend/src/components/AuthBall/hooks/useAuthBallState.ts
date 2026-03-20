/**
 * useAuthBallState - 状态机 Hook
 * 整合外部 BallState + 内部自动检测，输出 EmotionState
 */
import { useMemo } from 'react';
import type { BallState, EmotionState } from '../types/authBall.types';

/** 外部 BallState 到内部 EmotionState 的映射 */
const STATE_MAP: Record<BallState, EmotionState> = {
  default: 'idle',
  looking: 'hover',  // looking 状态激活眼神跟随+眉挑
  shy: 'focus-password',  // shy 触发遮眼+脸红
  happy: 'success',  // happy 触发成功表情
};

interface UseAuthBallStateOptions {
  /** 外部传入状态 */
  externalState: BallState;
  /** 密码框是否聚焦 */
  isPasswordFocused: boolean;
  /** 是否正在执行错误动画 */
  isError: boolean;
  /** 是否正在执行成功动画 */
  isSuccess: boolean;
}

interface UseAuthBallStateResult {
  /** 当前情绪状态 */
  emotion: EmotionState;
  /** 是否激活眼神跟随 */
  isEyeTrackingActive: boolean;
  /** 优先级描述 */
  priorityLevel: number;
}

/**
 * 状态优先级（高优先覆盖低优先）
 * 用于调试和日志
 */
const PRIORITY_LEVELS: Record<EmotionState, number> = {
  idle: 0,
  hover: 1,
  'focus-password': 2,
  success: 3,
  error: 4,
};

/**
 * AuthBall 状态管理 Hook
 * 
 * @example
 * ```tsx
 * const { emotion, isEyeTrackingActive } = useAuthBallState({
 *   externalState: 'default',
 *   isPasswordFocused: false,
 *   isError: false,
 *   isSuccess: false,
 * });
 * ```
 */
export function useAuthBallState({
  externalState,
  isPasswordFocused,
  isError,
  isSuccess,
}: UseAuthBallStateOptions): UseAuthBallStateResult {
  const emotion = useMemo<EmotionState>(() => {
    // 优先级：error > success > focus-password > hover/idle
    
    if (isError) return 'error';
    if (isSuccess) return 'success';
    if (isPasswordFocused) return 'focus-password';
    
    // 外部状态映射
    return STATE_MAP[externalState] || 'idle';
  }, [externalState, isPasswordFocused, isError, isSuccess]);

  const isEyeTrackingActive = useMemo(() => {
    // looking 状态始终激活眼神跟随
    // idle 在鼠标移动时也激活
    return externalState === 'looking' || (emotion === 'idle' && !isPasswordFocused);
  }, [externalState, emotion, isPasswordFocused]);

  const priorityLevel = useMemo(() => {
    return PRIORITY_LEVELS[emotion];
  }, [emotion]);

  return {
    emotion,
    isEyeTrackingActive,
    priorityLevel,
  };
}

export default useAuthBallState;
