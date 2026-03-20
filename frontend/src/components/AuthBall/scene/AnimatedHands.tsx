/**
 * AnimatedHands - 带动画的遮眼手掌
 * 当密码框聚焦时从两侧伸出遮住眼睛
 */
import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import type { EmotionState } from '../types/authBall.types';

// 手掌位置参数
const HAND_START_X = 2.5;    // 起始位置（球体两侧远处）
const HAND_END_X = 0.55;     // 最终位置

interface AnimatedHandsProps {
  emotion: EmotionState;
  size: number;
}

/**
 * AnimatedHands 组件
 */
export function AnimatedHands({ emotion, size }: AnimatedHandsProps) {
  const isVisible = emotion === 'focus-password';

  return (
    <group>
      {/* 左手 */}
      <AnimatedHand isLeft isVisible={isVisible} size={size} />
      
      {/* 右手 */}
      <AnimatedHand isLeft={false} isVisible={isVisible} size={size} />
    </group>
  );
}

interface AnimatedHandProps {
  isLeft: boolean;
  isVisible: boolean;
  size: number;
}

function AnimatedHand({ isLeft, isVisible, size }: AnimatedHandProps) {
  const groupRef = useRef<THREE.Group>(null);
  const animRef = useRef({ currentX: isLeft ? -HAND_START_X : HAND_START_X });

  useFrame(() => {
    if (!groupRef.current) return;

    const targetX = isLeft ? -HAND_END_X : HAND_END_X;
    const startX = isLeft ? -HAND_START_X : HAND_START_X;
    const lerpFactor = isVisible ? 0.18 : 0.12;
    
    animRef.current.currentX = THREE.MathUtils.lerp(
      animRef.current.currentX,
      isVisible ? targetX : startX,
      lerpFactor
    );

    groupRef.current.position.x = animRef.current.currentX;
  });

  // 黄色手掌
  const palmColor = '#FFD700';

  return (
    <group ref={groupRef} position={[isLeft ? -HAND_START_X : HAND_START_X, 0.15, 0.95]} scale={[size, size, size]}>
      {/* 手掌 */}
      <mesh>
        <boxGeometry args={[0.25, 0.35, 0.08]} />
        <meshStandardMaterial color={palmColor} roughness={0.5} />
      </mesh>
      
      {/* 拇指 */}
      <mesh position={[isLeft ? 0.15 : -0.15, 0.12, 0]} rotation={[0, 0, isLeft ? -0.5 : 0.5]}>
        <capsuleGeometry args={[0.04, 0.12, 8, 16]} />
        <meshStandardMaterial color={palmColor} roughness={0.5} />
      </mesh>
      
      {/* 食指 */}
      <mesh position={[isLeft ? 0.08 : -0.08, 0.22, 0]} rotation={[0, 0, isLeft ? -0.1 : 0.1]}>
        <capsuleGeometry args={[0.035, 0.18, 8, 16]} />
        <meshStandardMaterial color={palmColor} roughness={0.5} />
      </mesh>
      
      {/* 中指 */}
      <mesh position={[0, 0.24, 0]}>
        <capsuleGeometry args={[0.035, 0.2, 8, 16]} />
        <meshStandardMaterial color={palmColor} roughness={0.5} />
      </mesh>
      
      {/* 无名指 */}
      <mesh position={[isLeft ? -0.08 : 0.08, 0.22, 0]} rotation={[0, 0, isLeft ? 0.1 : -0.1]}>
        <capsuleGeometry args={[0.035, 0.18, 8, 16]} />
        <meshStandardMaterial color={palmColor} roughness={0.5} />
      </mesh>
      
      {/* 小指 */}
      <mesh position={[isLeft ? -0.12 : 0.12, 0.18, 0]} rotation={[0, 0, isLeft ? 0.2 : -0.2]}>
        <capsuleGeometry args={[0.03, 0.12, 8, 16]} />
        <meshStandardMaterial color={palmColor} roughness={0.5} />
      </mesh>
    </group>
  );
}


