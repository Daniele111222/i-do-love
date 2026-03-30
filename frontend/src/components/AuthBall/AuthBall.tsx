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

/** WebGL 状态 */
interface WebGLState {
  isSupported: boolean;
  contextLost: boolean;
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
    
    // WebGL 状态
    const [webglState, setWebglState] = useState<WebGLState>({
      isSupported: true,
      contextLost: false,
    });

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

    // Canvas 创建时的回调
    const handleCreated = useCallback(({ gl }: { gl: WebGLRenderer }) => {
      // 检查 WebGL 支持
      const canvas = gl.domElement;
      const context = canvas.getContext('webgl2') || canvas.getContext('webgl');
      
      if (!context) {
        setWebglState({ isSupported: false, contextLost: false });
        return;
      }

      // 监听 WebGL 上下文丢失
      const handleContextLost = (event: Event) => {
        event.preventDefault();
        console.warn('[AuthBall] WebGL Context Lost');
        setWebglState({ isSupported: true, contextLost: true });
      };

      // 监听 WebGL 上下文恢复
      const handleContextRestored = () => {
        console.log('[AuthBall] WebGL Context Restored');
        setWebglState({ isSupported: true, contextLost: false });
      };

      canvas.addEventListener('webglcontextlost', handleContextLost);
      canvas.addEventListener('webglcontextrestored', handleContextRestored);

      // 设置抗锯齿
      gl.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    }, []);

    // WebGL 不支持或上下文丢失时的 Fallback
    if (!webglState.isSupported) {
      return (
        <div
          ref={ref}
          className={twMerge(clsx('relative flex items-center justify-center', className))}
          style={{ width: '100%', height: '100%' }}
        >
          <div className="text-center text-gray-400">
            <div className="text-4xl mb-2">🎭</div>
            <p className="text-sm">3D 表情球暂不可用</p>
            <p className="text-xs mt-1">请启用 WebGL 以体验完整功能</p>
          </div>
        </div>
      );
    }

    if (webglState.contextLost) {
      return (
        <div
          ref={ref}
          className={twMerge(clsx('relative flex items-center justify-center', className))}
          style={{ width: '100%', height: '100%' }}
        >
          <div className="text-center text-gray-400">
            <div className="text-4xl mb-2">🔄</div>
            <p className="text-sm">正在重新连接 3D 场景...</p>
            <p className="text-xs mt-1">刷新页面可解决此问题</p>
          </div>
        </div>
      );
    }

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
            powerPreference: 'high-performance',
          }}
          dpr={[1, 1.5]} // 降低像素比，减少 GPU 压力
          style={{ background: 'transparent' }}
          onCreated={handleCreated}
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
