/**
 * AnimatedSphere - 带动画的球体
 * 整合入场动画、呼吸动画、成功跳跃、错误摇头
 */
import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import type { EmotionState } from '../types/authBall.types';

// 动画参数
const ENTER_DURATION = 1.5;
const ENTER_START_Y = -6;
const BREATH_SPEED = 0.8;
const BREATH_AMPLITUDE = 0.025;

/** 球体颜色映射 */
const SPHERE_COLORS: Record<EmotionState, string> = {
  idle: '#8B7CF8',
  hover: '#7B6CE8',
  'focus-password': '#F87CA8',
  success: '#6EE7A0',
  error: '#5A5A7A',
};

interface AnimatedSphereProps {
  emotion: EmotionState;
  size: number;
}

/**
 * AnimatedSphere 组件
 */
export function AnimatedSphere({ emotion, size }: AnimatedSphereProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  
  // 动画状态
  const animRef = useRef({
    // 入场
    enterProgress: 0,
    enterStartTime: null as number | null,
    // 呼吸
    breathPhase: 0,
    // 跳跃
    jumpPhase: 0,
    wasJumping: false,
    // 摇头
    shakePhase: 0,
    wasShaking: false,
    // 当前材质颜色
    currentColor: new THREE.Color(SPHERE_COLORS.idle),
  });

  // 创建材质
  const material = useMemo(() => {
    return new THREE.MeshStandardMaterial({
      color: new THREE.Color(SPHERE_COLORS.idle),
      roughness: 0.4,
      metalness: 0.1,
    });
  }, []);

  useFrame((state, delta) => {
    if (!meshRef.current) return;
    
    const anim = animRef.current;
    const elapsed = state.clock.getElapsedTime();

    // 1. 入场动画
    if (anim.enterStartTime === null) {
      anim.enterStartTime = elapsed;
    }
    const enterElapsed = elapsed - anim.enterStartTime;
    const rawProgress = Math.min(enterElapsed / ENTER_DURATION, 1);
    anim.enterProgress = easeOutBack(rawProgress);

    // 2. 呼吸动画
    anim.breathPhase += delta * BREATH_SPEED;
    const breathOffset = Math.sin(anim.breathPhase) * BREATH_AMPLITUDE;

    // 3. 成功跳跃
    let jumpOffset = 0;
    if (emotion === 'success' && !anim.wasJumping) {
      anim.jumpPhase = 0;
      anim.wasJumping = true;
    } else if (emotion !== 'success') {
      anim.wasJumping = false;
    }

    if (anim.wasJumping) {
      anim.jumpPhase += delta * 4;
      jumpOffset = Math.sin(anim.jumpPhase) * 0.3 * Math.exp(-anim.jumpPhase * 0.3);
      if (anim.jumpPhase > Math.PI * 2) {
        anim.wasJumping = false;
        jumpOffset = 0;
      }
    }

    // 4. 错误摇头
    let shakeOffset = 0;
    if (emotion === 'error' && !anim.wasShaking) {
      anim.shakePhase = 0;
      anim.wasShaking = true;
    } else if (emotion !== 'error') {
      anim.wasShaking = false;
    }

    if (anim.wasShaking) {
      anim.shakePhase += delta * 8;
      shakeOffset = Math.sin(anim.shakePhase) * 0.15 * Math.exp(-anim.shakePhase * 0.4);
      if (anim.shakePhase > Math.PI * 3) {
        anim.wasShaking = false;
        shakeOffset = 0;
      }
    }

    // 应用变换
    const enterY = THREE.MathUtils.lerp(ENTER_START_Y, 0, anim.enterProgress);
    meshRef.current.position.y = enterY + breathOffset + jumpOffset;
    meshRef.current.position.x = shakeOffset * 0.1;
    meshRef.current.scale.set(
      1 + breathOffset * 0.01,
      1 - breathOffset * 0.01,
      1
    );

    // 更新颜色
    const targetColor = new THREE.Color(SPHERE_COLORS[emotion]);
    anim.currentColor.lerp(targetColor, 0.1);
    material.color.copy(anim.currentColor);
  });

  return (
    <mesh ref={meshRef} position={[0, ENTER_START_Y, 0]}>
      <sphereGeometry args={[size, 64, 64]} />
      <primitive object={material} attach="material" />
    </mesh>
  );
}

/** 弹性缓出函数 */
function easeOutBack(x: number): number {
  const c1 = 1.70158;
  const c3 = c1 + 1;
  return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2);
}
