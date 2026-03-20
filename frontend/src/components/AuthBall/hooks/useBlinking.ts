/**
 * useBlinking - 眨眼动画 Hook
 * 自动触发眨眼，支持不同情绪的眨眼频率
 */
import { useRef, useCallback } from 'react';
import { useFrame } from '@react-three/fiber';
import type { EmotionState } from '../types/authBall.types';

interface BlinkingResult {
  /** 眨眼进度 0=睁眼, 1=完全闭合 */
  blinkProgress: number;
  /** 当前是否正在眨眼 */
  isBlinking: boolean;
}

/**
 * useBlinking Hook
 * 
 * @param emotion - 当前情绪状态，影响眨眼频率和次数
 * @example
 * ```tsx
 * const { blinkProgress, isBlinking } = useBlinking(emotion);
 * ```
 */
export function useBlinking(emotion: EmotionState): BlinkingResult {
  const blinkProgressRef = useRef(0);
  const isBlinkingRef = useRef(false);
  const nextBlinkTimeRef = useRef(getRandomBlinkInterval(emotion));
  const blinkPhaseRef = useRef(0); // 0=闭合中, 1=睁开中
  const consecutiveBlinksRef = useRef(0);

  // 根据情绪状态决定眨眼参数
  const getBlinkParams = useCallback((state: EmotionState) => {
    switch (state) {
      case 'hover':
        return { duration: 0.15, doubleBlink: true }; // hover 时双击眨眼
      case 'success':
        return { duration: 0.12, doubleBlink: false };
      case 'error':
        return { duration: 0.18, doubleBlink: false };
      default:
        return { duration: 0.15, doubleBlink: false };
    }
  }, []);

  useFrame((state, delta) => {
    const params = getBlinkParams(emotion);

    if (!isBlinkingRef.current) {
      // 检查是否该眨眼
      const elapsed = state.clock.getElapsedTime();
      if (elapsed >= nextBlinkTimeRef.current) {
        // 开始眨眼
        isBlinkingRef.current = true;
        blinkPhaseRef.current = 0;
        blinkProgressRef.current = 0;
      }
    } else {
      // 正在眨眼，更新进度
      const blinkSpeed = 1 / params.duration; // 完整眨眼周期需要的时间
      
      if (blinkPhaseRef.current === 0) {
        // 闭合中
        blinkProgressRef.current += delta * blinkSpeed;
        
        if (blinkProgressRef.current >= 1) {
          // 开始睁开
          blinkProgressRef.current = 1;
          blinkPhaseRef.current = 1;
          
          // 检查是否双击眨眼
          if (params.doubleBlink && consecutiveBlinksRef.current < 1) {
            consecutiveBlinksRef.current++;
          } else {
            consecutiveBlinksRef.current = 0;
            isBlinkingRef.current = false;
            blinkProgressRef.current = 0;
            nextBlinkTimeRef.current = state.clock.getElapsedTime() + getRandomBlinkInterval(emotion);
          }
        }
      } else {
        // 睁开中
        blinkProgressRef.current -= delta * blinkSpeed * 1.5; // 睁开稍快
        
        if (blinkProgressRef.current <= 0) {
          blinkProgressRef.current = 0;
          
          // 检查是否双击眨眼
          if (params.doubleBlink && consecutiveBlinksRef.current < 1) {
            // 短暂停顿后再次眨眼
            setTimeout(() => {
              if (isBlinkingRef.current) {
                blinkPhaseRef.current = 0;
              }
            }, 80);
          } else {
            isBlinkingRef.current = false;
            nextBlinkTimeRef.current = state.clock.getElapsedTime() + getRandomBlinkInterval(emotion);
          }
        }
      }
    }
  });

  return {
    blinkProgress: blinkProgressRef.current,
    isBlinking: isBlinkingRef.current,
  };
}

/**
 * 获取随机眨眼间隔
 * 根据情绪状态变化眨眼频率
 */
function getRandomBlinkInterval(emotion: EmotionState): number {
  const baseInterval = 2500; // 2.5秒基础
  
  switch (emotion) {
    case 'hover':
      return 1500 + Math.random() * 1000; // hover 时更频繁
    case 'focus-password':
      return 3000 + Math.random() * 1500;
    case 'success':
      return 2000 + Math.random() * 1000;
    case 'error':
      return 4000 + Math.random() * 2000; // error 时较慢
    default:
      return baseInterval + Math.random() * 1500;
  }
}

export default useBlinking;
