/**
 * AuthBall - 3D 拟人化球体主组件
 * 
 * 一个拥有"复杂内心戏"的角色
 * 默认表情是"礼貌而尴尬的微笑" + "微微下压的眉毛" + "呆滞但专注的眼神"
 */
import { useState, useEffect, useCallback, forwardRef } from 'react';
import { Canvas } from '@react-three/fiber';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import type { BallState, EmotionState } from './types/authBall.types';
import { useAuthBallState } from './hooks/useAuthBallState';
import { usePasswordWatch } from './hooks/usePasswordWatch';
import { BallScene } from './scene/BallScene';

interface AuthBallProps {
  /** 外部状态（测试页面使用）*/
  state?: BallState;
  /** 球体大小 */
  size?: number;
  /** CSS类名 */
  className?: string;
  /** 密码框聚焦回调 */
  onPasswordFocus?: (focused: boolean) => void;
}

/**
 * AuthBall 组件
 * 
 * @example
 * ```tsx
 * <AuthBall state="default" size={1.5} className="w-full h-[450px]" />
 * ```
 */
export const AuthBall = forwardRef<HTMLDivElement, AuthBallProps>(
  ({ state = 'default', size = 1.5, className, onPasswordFocus }, ref) => {
    // 密码框监听
    const { isPasswordFocused } = usePasswordWatch();
    
    // 鼠标位置状态
    const [mouseNorm, setMouseNorm] = useState({ x: 0, y: 0 });
    
    // 内部情绪状态
    const { emotion, isEyeTrackingActive } = useAuthBallState({
      externalState: state,
      isPasswordFocused,
      isError: false, // 可扩展：外部传入 error 状态
      isSuccess: false, // 可扩展：外部传入 success 状态
    });

    // 鼠标移动监听
    const handleMouseMove = useCallback((event: MouseEvent) => {
      const x = (event.clientX / window.innerWidth) * 2 - 1;
      const y = -((event.clientY / window.innerHeight) * 2 - 1);
      setMouseNorm({ x, y });
    }, []);

    // 鼠标离开监听
    const handleMouseLeave = useCallback(() => {
      // 鼠标离开时不立即回正，让眼神缓慢回归
    }, []);

    useEffect(() => {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseleave', handleMouseLeave);
      
      return () => {
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseleave', handleMouseLeave);
      };
    }, [handleMouseMove, handleMouseLeave]);

    // 回调通知
    useEffect(() => {
      onPasswordFocus?.(isPasswordFocused);
    }, [isPasswordFocused, onPasswordFocus]);

    return (
      <div
        ref={ref}
        className={twMerge(clsx('relative', className))}
        style={{ width: '100%', height: '100%' }}
      >
        <Canvas
          camera={{ position: [0, 0, 4], fov: 50 }}
          gl={{
            antialias: true,
            alpha: true,
          }}
          dpr={[1, 2]} // 限制像素比，性能优化
          style={{ background: 'transparent' }}
        >
          <BallSceneWrapper
            emotion={emotion}
            isEyeTrackingActive={isEyeTrackingActive}
            size={size}
            mouseNorm={mouseNorm}
          />
        </Canvas>
      </div>
    );
  }
);

AuthBall.displayName = 'AuthBall';

// 内部封装组件，用于访问 R3F context
interface BallSceneWrapperProps {
  emotion: EmotionState;
  isEyeTrackingActive: boolean;
  size: number;
  mouseNorm: { x: number; y: number };
}

function BallSceneWrapper({
  emotion,
  isEyeTrackingActive,
  size,
  mouseNorm,
}: BallSceneWrapperProps) {
  return (
    <BallScene
      emotion={emotion}
      isEyeTrackingActive={isEyeTrackingActive}
      size={size}
      externalMouseNorm={mouseNorm}
    />
  );
}

export default AuthBall;
