/**
 * AuthBall - 3D character used on auth pages.
 */
import { useState, useEffect, useCallback, forwardRef } from 'react';
import { Canvas } from '@react-three/fiber';
import type { WebGLRenderer } from 'three';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import type { AuthBallProps } from './types/authBall.types';
import { useAuthBallState } from './hooks/useAuthBallState';
import { usePasswordWatch } from './hooks/usePasswordWatch';
import { BallScene } from './scene/BallScene';

interface WebGLState {
  isSupported: boolean;
  contextLost: boolean;
}

const NEUTRAL_MOUSE = { x: 0, y: 0 };

export const AuthBall = forwardRef<HTMLDivElement, AuthBallProps>(
  (
    {
      state = 'default',
      size = 1.5,
      className,
      trackCursor = true,
      passwordMode = 'auto-watch',
      isPasswordActive = false,
      onPasswordFocus,
    },
    ref
  ) => {
    const { isPasswordFocused: watchedPasswordFocused } = usePasswordWatch();
    const effectivePasswordFocused =
      passwordMode === 'controlled' ? isPasswordActive : watchedPasswordFocused;

    const [mouseNorm, setMouseNorm] = useState(NEUTRAL_MOUSE);
    const [webglState, setWebglState] = useState<WebGLState>({
      isSupported: true,
      contextLost: false,
    });

    const { emotion, isEyeTrackingActive } = useAuthBallState({
      externalState: state,
      isPasswordFocused: effectivePasswordFocused,
      isError: false,
      isSuccess: false,
      trackCursor,
    });

    const handleMouseMove = useCallback((event: MouseEvent) => {
      const x = (event.clientX / window.innerWidth) * 2 - 1;
      const y = -((event.clientY / window.innerHeight) * 2 - 1);
      setMouseNorm({ x, y });
    }, []);

    const handleMouseLeave = useCallback(() => {
      setMouseNorm(NEUTRAL_MOUSE);
    }, []);

    useEffect(() => {
      if (!trackCursor) {
        return;
      }

      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseleave', handleMouseLeave);

      return () => {
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseleave', handleMouseLeave);
      };
    }, [handleMouseLeave, handleMouseMove, trackCursor]);

    useEffect(() => {
      onPasswordFocus?.(effectivePasswordFocused);
    }, [effectivePasswordFocused, onPasswordFocus]);

    const handleCreated = useCallback(({ gl }: { gl: WebGLRenderer }) => {
      const canvas = gl.domElement;
      const context = canvas.getContext('webgl2') || canvas.getContext('webgl');

      if (!context) {
        setWebglState({ isSupported: false, contextLost: false });
        return;
      }

      const handleContextLost = (event: Event) => {
        event.preventDefault();
        console.warn('[AuthBall] WebGL Context Lost');
        setWebglState({ isSupported: true, contextLost: true });
      };

      const handleContextRestored = () => {
        console.log('[AuthBall] WebGL Context Restored');
        setWebglState({ isSupported: true, contextLost: false });
      };

      canvas.addEventListener('webglcontextlost', handleContextLost);
      canvas.addEventListener('webglcontextrestored', handleContextRestored);
      gl.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    }, []);

    if (!webglState.isSupported) {
      return (
        <div
          ref={ref}
          className={twMerge(clsx('relative flex items-center justify-center', className))}
          style={{ width: '100%', height: '100%' }}
        >
          <div className="text-center text-stone-500">
            <div className="mb-2 text-4xl">◌</div>
            <p className="text-sm">3D 角色暂时不可用</p>
            <p className="mt-1 text-xs">请启用 WebGL 以体验完整交互</p>
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
          <div className="text-center text-stone-500">
            <div className="mb-2 text-4xl">◌</div>
            <p className="text-sm">正在重新连接 3D 场景...</p>
            <p className="mt-1 text-xs">刷新页面可恢复显示</p>
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
          dpr={[1, 1.5]}
          style={{ background: 'transparent' }}
          onCreated={handleCreated}
        >
          <BallScene
            emotion={emotion}
            isEyeTrackingActive={isEyeTrackingActive}
            size={size}
            externalMouseNorm={trackCursor ? mouseNorm : NEUTRAL_MOUSE}
          />
        </Canvas>
      </div>
    );
  }
);

AuthBall.displayName = 'AuthBall';

export default AuthBall;
