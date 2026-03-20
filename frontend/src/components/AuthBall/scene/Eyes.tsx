/**
 * Eyes - 眼睛系统组件
 * 包含眼白、瞳孔、高光、眼皮（眨眼）
 */
import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import type { EmotionState } from '../types/authBall.types';

interface EyesProps {
  /** 当前情绪状态 */
  emotion: EmotionState;
  /** 鼠标归一化位置 */
  mouseNorm: { x: number; y: number };
  /** 瞳孔跟随目标位置 */
  pupilTarget: { x: number; y: number };
  /** 眨眼进度 0-1 */
  blinkProgress: number;
  /** 是否激活眼神跟随 */
  isTracking: boolean;
}

const EYE_POSITIONS = {
  left: { x: -0.35, y: 0.15, z: 0.85 },
  right: { x: 0.35, y: 0.15, z: 0.85 },
};

const EYE_WHITE_SIZE = 0.22;
const PUPIL_SIZE = 0.12;
const HIGHLIGHT_SIZE = 0.04;

/**
 * Eyes 组件
 * 左右眼 + 瞳孔跟随 + 眨眼
 */
export function Eyes({
  emotion,
  pupilTarget,
  blinkProgress,
  isTracking,
}: EyesProps) {
  return (
    <group>
      <SingleEye
        side="left"
        position={EYE_POSITIONS.left}
        emotion={emotion}
        pupilTarget={pupilTarget}
        blinkProgress={blinkProgress}
        isTracking={isTracking}
      />
      <SingleEye
        side="right"
        position={EYE_POSITIONS.right}
        emotion={emotion}
        pupilTarget={pupilTarget}
        blinkProgress={blinkProgress}
        isTracking={isTracking}
      />
    </group>
  );
}

interface SingleEyeProps {
  side: 'left' | 'right';
  position: { x: number; y: number; z: number };
  emotion: EmotionState;
  pupilTarget: { x: number; y: number };
  blinkProgress: number;
  isTracking: boolean;
}

function SingleEye({
  side,
  position,
  emotion,
  pupilTarget,
  blinkProgress,
  isTracking,
}: SingleEyeProps) {
  const groupRef = useRef<THREE.Group>(null);
  const pupilRef = useRef<THREE.Mesh>(null);
  const eyelidRef = useRef<THREE.Mesh>(null);

  useFrame(() => {
    if (!pupilRef.current || !eyelidRef.current) return;

    // 瞳孔跟随 - Lerp 插值实现滞后效果
    const maxOffset = 0.08; // 最大偏移量
    const targetX = isTracking ? pupilTarget.x * maxOffset : 0;
    const targetY = isTracking ? pupilTarget.y * maxOffset : 0;
    
    // focus-password 时眼神向下看
    const lookDownOffset = emotion === 'focus-password' ? -0.04 : 0;
    
    // 当前瞳孔位置
    const currentX = pupilRef.current.position.x;
    const currentY = pupilRef.current.position.y;
    
    // Lerp 插值系数：跟随时0.15，离开时0.04（更慢回正）
    const lerpFactor = isTracking ? 0.15 : 0.04;
    
    pupilRef.current.position.x = THREE.MathUtils.lerp(currentX, targetX, lerpFactor);
    pupilRef.current.position.y = THREE.MathUtils.lerp(currentY, targetY + lookDownOffset, lerpFactor);

    // 眼皮眨眼动画 - scale.y 控制眼皮闭合程度
    const eyelidScale = 1 - blinkProgress;
    eyelidRef.current.scale.y = eyelidScale;
    // 眼皮位置也要调整，保持在眼睛上方
    eyelidRef.current.position.y = position.y + (EYE_WHITE_SIZE * (1 - blinkProgress * 0.5));
  });

  // 高光位置 - 瞳孔右上
  const highlightOffset = useMemo(() => {
    return {
      x: position.x + (side === 'left' ? -1 : 1) * PUPIL_SIZE * 0.3,
      y: position.y + PUPIL_SIZE * 0.4,
      z: position.z + PUPIL_SIZE,
    };
  }, [position, side]);

  return (
    <group ref={groupRef} position={[position.x, position.y, position.z]}>
      {/* 眼白 */}
      <mesh>
        <sphereGeometry args={[EYE_WHITE_SIZE, 32, 32]} />
        <meshStandardMaterial color="#FFFFFF" roughness={0.3} />
      </mesh>
      
      {/* 瞳孔 */}
      <mesh ref={pupilRef} position={[0, 0, EYE_WHITE_SIZE * 0.8]}>
        <sphereGeometry args={[PUPIL_SIZE, 32, 32]} />
        <meshStandardMaterial color="#1a1a2e" roughness={0.2} />
      </mesh>
      
      {/* 高光 */}
      <mesh position={[
        highlightOffset.x - position.x,
        highlightOffset.y - position.y,
        highlightOffset.z - position.z
      ]}>
        <sphereGeometry args={[HIGHLIGHT_SIZE, 16, 16]} />
        <meshBasicMaterial color="#FFFFFF" />
      </mesh>
      
      {/* 眼皮 - 用于眨眼 */}
      <mesh 
        ref={eyelidRef}
        position={[0, position.y + EYE_WHITE_SIZE * 0.5, position.z + 0.01]}
        rotation={[0, 0, 0]}
      >
        {/* 椭圆形眼皮 */}
        <planeGeometry args={[EYE_WHITE_SIZE * 2.2, EYE_WHITE_SIZE * 1.5]} />
        <meshBasicMaterial 
          color={getEyelidColor(emotion)} 
          transparent
          opacity={1}
          side={THREE.DoubleSide}
        />
      </mesh>
    </group>
  );
}

/**
 * 获取眼皮颜色（与球体颜色匹配）
 */
function getEyelidColor(emotion: EmotionState): string {
  const colorMap: Record<EmotionState, string> = {
    idle: '#8B7CF8',
    hover: '#7B6CE8',
    'focus-password': '#F87CA8',
    success: '#6EE7A0',
    error: '#5A5A7A',
  };
  return colorMap[emotion];
}

export default Eyes;
