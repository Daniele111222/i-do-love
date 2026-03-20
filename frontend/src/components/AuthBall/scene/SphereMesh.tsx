/**
 * SphereMesh - 球体几何体组件
 * 负责渲染主体球体 + 入场/呼吸动画
 */
import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import type { EmotionState } from '../types/authBall.types';
import { SPHERE_COLORS } from '../types/authBall.types';

interface SphereMeshProps {
  /** 当前情绪状态 */
  emotion: EmotionState;
  /** 球体大小 */
  size: number;
  /** 入场进度 0-1 */
  enterProgress: number;
  /** 呼吸偏移量 */
  breathOffset: number;
  /** 成功跳跃偏移 */
  jumpOffset: number;
  /** 摇头偏移 */
  shakeOffset: number;
}

const ENTER_TARGET_Y = 0;    // 入场后目标Y位置
const ENTER_START_Y = -6;    // 入场起点Y位置

/**
 * SphereMesh 组件
 * 入场动画 + 呼吸动画 + 颜色变化
 */
export function SphereMesh({
  emotion,
  size,
  enterProgress,
  breathOffset,
  jumpOffset,
  shakeOffset,
}: SphereMeshProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  
  // 材质 - 根据情绪状态变化
  const material = useMemo(() => {
    const color = SPHERE_COLORS[emotion];
    return new THREE.MeshStandardMaterial({
      color: new THREE.Color(color),
      roughness: 0.4,        // 适中粗糙度，充气质感
      metalness: 0.1,        // 轻微金属感增加光泽
      envMapIntensity: 0.5,
    });
  }, [emotion]);

  // 更新材质颜色（避免重新创建材质）
  useFrame(() => {
    if (meshRef.current) {
      const mat = meshRef.current.material as THREE.MeshStandardMaterial;
      const targetColor = new THREE.Color(SPHERE_COLORS[emotion]);
      mat.color.lerp(targetColor, 0.1);
    }
  });

  // 入场Y位置计算
  const enterY = useMemo(() => {
    return THREE.MathUtils.lerp(ENTER_START_Y, ENTER_TARGET_Y, easeOutBack(enterProgress));
  }, [enterProgress]);

  return (
    <mesh 
      ref={meshRef}
      position={[shakeOffset * 0.1, enterY + breathOffset + jumpOffset, 0]}
      scale={[1 + breathOffset * 0.01, 1 - breathOffset * 0.01, 1]}
    >
      {/* 高多边形球体，避免锯齿 */}
      <sphereGeometry args={[size, 64, 64]} />
      <primitive object={material} attach="material" />
    </mesh>
  );
}

/**
 * 弹性缓出函数 - 模拟弹簧效果
 */
function easeOutBack(x: number): number {
  const c1 = 1.70158;
  const c3 = c1 + 1;
  return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2);
}

export default SphereMesh;
