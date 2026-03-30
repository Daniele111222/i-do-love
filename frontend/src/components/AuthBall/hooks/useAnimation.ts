/* eslint-disable react-hooks/refs */
/**
 * useBreathing - 呼吸动画 Hook
 * 计算呼吸偏移量，用于球体轻微起伏和左右晃动
 */
import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';

interface BreathingResult {
  /** 呼吸偏移量（用于球体缩放/位置） */
  breathOffset: number;
  /** 呼吸相位 0-2PI */
  breathPhase: number;
}

/**
 * useBreathing Hook
 * 
 * @example
 * ```tsx
 * const { breathOffset } = useBreathing();
 * ```
 */
export function useBreathing(): BreathingResult {
  const breathPhaseRef = useRef(0);
  const breathOffsetRef = useRef(0);

  // 呼吸参数
  const BREATH_SPEED = 0.8;      // 呼吸频率
  const BREATH_AMPLITUDE = 0.025; // 呼吸幅度（缩放）

  useFrame((_, delta) => {
    // 更新呼吸相位
    breathPhaseRef.current += delta * BREATH_SPEED;
    
    // 计算呼吸偏移（正弦波）
    const breathe = Math.sin(breathPhaseRef.current);
    breathOffsetRef.current = breathe * BREATH_AMPLITUDE;
  });

  return {
    breathOffset: breathOffsetRef.current,
    breathPhase: breathPhaseRef.current,
  };
}

/**
 * useEnterAnimation - 入场动画 Hook
 * 弹性缓冲效果
 */
interface EnterAnimationResult {
  /** 入场进度 0-1 */
  enterProgress: number;
  /** 入场是否完成 */
  isEntered: boolean;
}

export function useEnterAnimation(duration: number = 1.5): EnterAnimationResult {
  const progressRef = useRef(0);
  const startTimeRef = useRef<number | null>(null);
  const isEnteredRef = useRef(false);

  useFrame((state) => {
    if (isEnteredRef.current) {
      progressRef.current = 1;
      return;
    }

    if (startTimeRef.current === null) {
      startTimeRef.current = state.clock.getElapsedTime();
    }

    const elapsed = state.clock.getElapsedTime() - startTimeRef.current;
    const rawProgress = Math.min(elapsed / duration, 1);
    
    // 使用 easeOutBack 弹性缓动
    progressRef.current = easeOutBack(rawProgress);
    
    if (rawProgress >= 1) {
      isEnteredRef.current = true;
    }
  });

  return {
    enterProgress: progressRef.current,
    isEntered: isEnteredRef.current,
  };
}

/**
 * useSuccessAnimation - 成功动画 Hook
 */
interface SuccessAnimationResult {
  jumpOffset: number;
  isAnimating: boolean;
}

export function useSuccessAnimation(trigger: boolean): SuccessAnimationResult {
  const jumpPhaseRef = useRef(0);
  const isAnimatingRef = useRef(false);
  const jumpOffsetRef = useRef(0);
  const wasTriggeredRef = useRef(false);

  useFrame((_, delta) => {
    if (trigger && !wasTriggeredRef.current) {
      // 触发时重置
      jumpPhaseRef.current = 0;
      isAnimatingRef.current = true;
      wasTriggeredRef.current = true;
    } else if (!trigger) {
      wasTriggeredRef.current = false;
    }

    if (isAnimatingRef.current) {
      jumpPhaseRef.current += delta * 4; // 跳跃速度
      
      // 跳跃高度随时间衰减
      const jumpHeight = Math.sin(jumpPhaseRef.current) * 0.3 * Math.exp(-jumpPhaseRef.current * 0.3);
      jumpOffsetRef.current = Math.max(0, jumpHeight);
      
      if (jumpPhaseRef.current > Math.PI * 2) {
        isAnimatingRef.current = false;
        jumpOffsetRef.current = 0;
      }
    }
  });

  return {
    jumpOffset: jumpOffsetRef.current,
    isAnimating: isAnimatingRef.current,
  };
}

/**
 * useErrorAnimation - 错误动画 Hook
 */
interface ErrorAnimationResult {
  shakeOffset: number;
  isAnimating: boolean;
}

export function useErrorAnimation(trigger: boolean): ErrorAnimationResult {
  const shakePhaseRef = useRef(0);
  const isAnimatingRef = useRef(false);
  const shakeOffsetRef = useRef(0);
  const wasTriggeredRef = useRef(false);

  useFrame((_, delta) => {
    if (trigger && !wasTriggeredRef.current) {
      shakePhaseRef.current = 0;
      isAnimatingRef.current = true;
      wasTriggeredRef.current = true;
    } else if (!trigger) {
      wasTriggeredRef.current = false;
    }

    if (isAnimatingRef.current) {
      shakePhaseRef.current += delta * 8; // 摇头速度
      
      // 摇头幅度随时间衰减
      const shakeAmount = Math.sin(shakePhaseRef.current) * 0.15 * Math.exp(-shakePhaseRef.current * 0.4);
      shakeOffsetRef.current = shakeAmount;
      
      if (shakePhaseRef.current > Math.PI * 3) {
        isAnimatingRef.current = false;
        shakeOffsetRef.current = 0;
      }
    }
  });

  return {
    shakeOffset: shakeOffsetRef.current,
    isAnimating: isAnimatingRef.current,
  };
}

/**
 * 弹性缓出函数
 */
function easeOutBack(x: number): number {
  const c1 = 1.70158;
  const c3 = c1 + 1;
  return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2);
}
