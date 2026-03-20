/**
 * useEyeTracking - 眼神跟随 Hook
 * 
 * 注意：这个 hook 在当前架构中未被使用
 * 瞳孔跟随逻辑直接在 AnimatedFace 组件中通过 useFrame 实现
 * 此文件保留用于参考或未来自定义需求
 */
import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface EyeTrackingResult {
  /** 瞳孔目标位置（归一化） */
  pupilTarget: { x: number; y: number };
  /** 是否正在跟踪 */
  isTracking: boolean;
}

/**
 * useEyeTracking Hook
 * 
 * @example
 * ```tsx
 * const { pupilTarget, isTracking } = useEyeTracking(isActive);
 * ```
 */
export function useEyeTracking(isActive: boolean): EyeTrackingResult {
  const pupilTargetRef = useRef({ x: 0, y: 0 });
  const isTrackingRef = useRef(false);

  useFrame(() => {
    if (!isActive) {
      // 不活跃时缓慢回正
      pupilTargetRef.current.x = THREE.MathUtils.lerp(pupilTargetRef.current.x, 0, 0.04);
      pupilTargetRef.current.y = THREE.MathUtils.lerp(pupilTargetRef.current.y, 0, 0.04);
      
      if (Math.abs(pupilTargetRef.current.x) < 0.01 && Math.abs(pupilTargetRef.current.y) < 0.01) {
        isTrackingRef.current = false;
      }
    }
  });

  return {
    pupilTarget: pupilTargetRef.current,
    isTracking: isActive && isTrackingRef.current,
  };
}

export default useEyeTracking;
