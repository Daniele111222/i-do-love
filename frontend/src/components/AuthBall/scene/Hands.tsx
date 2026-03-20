/**
 * Hands - 遮眼手掌组件
 * 当密码框聚焦时从两侧伸出遮住眼睛
 */
import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface HandsProps {
  /** 是否显示手掌 */
  isVisible: boolean;
  /** 球体大小 */
  size: number;
}

const HAND_START_X = 2.5;    // 起始位置（球体两侧远处）
const HAND_END_X_LEFT = -0.55;   // 左掌最终位置
const HAND_END_X_RIGHT = 0.55;  // 右掌最终位置
const HAND_Y = 0.15;         // 与眼睛齐平
const HAND_Z = 0.95;         // 在眼睛前方

/**
 * Hands 组件
 * 两只手掌，从两侧滑入遮眼
 */
export function Hands({ isVisible, size }: HandsProps) {
  const leftHandRef = useRef<THREE.Group>(null);
  const rightHandRef = useRef<THREE.Group>(null);

  useFrame(() => {
    [leftHandRef, rightHandRef].forEach((ref, index) => {
      if (!ref.current) return;
      
      const isLeft = index === 0;
      const targetX = isLeft ? HAND_END_X_LEFT : HAND_END_X_RIGHT;
      const startX = isLeft ? -HAND_START_X : HAND_START_X;
      
      // 目标位置
      const visible = isVisible ? 1 : 0;
      const targetPosX = THREE.MathUtils.lerp(startX, targetX, visible);
      
      // Lerp 插值实现弹性效果
      const lerpFactor = isVisible ? 0.18 : 0.12; // 出现更快，消失稍慢
      ref.current.position.x = THREE.MathUtils.lerp(ref.current.position.x, targetPosX, lerpFactor);
      
      // 透明度控制
      ref.current.visible = ref.current.position.x !== startX;
    });
  });

  return (
    <group>
      {/* 左手掌 */}
      <group ref={leftHandRef} position={[-HAND_START_X, HAND_Y, HAND_Z]} scale={[size, size, size]}>
        <HandPalm isLeft />
      </group>
      
      {/* 右手掌 */}
      <group ref={rightHandRef} position={[HAND_START_X, HAND_Y, HAND_Z]} scale={[size, size, size]}>
        <HandPalm isLeft={false} />
      </group>
    </group>
  );
}

interface HandPalmProps {
  isLeft: boolean;
}

function HandPalm({ isLeft }: HandPalmProps) {
  // 简化手掌：用几个圆柱体组合
  const palmColor = '#FFD700'; // 亮黄色，与球体呼应
  
  return (
    <group rotation={[0, 0, isLeft ? 0.3 : -0.3]}>
      {/* 手掌主体 */}
      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[0.25, 0.35, 0.08]} />
        <meshStandardMaterial color={palmColor} roughness={0.5} />
      </mesh>
      
      {/* 拇指 */}
      <mesh 
        position={[isLeft ? 0.15 : -0.15, 0.12, 0]} 
        rotation={[0, 0, isLeft ? -0.5 : 0.5]}
      >
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
      <mesh 
        position={[isLeft ? -0.12 : 0.12, 0.18, 0]} 
        rotation={[0, 0, isLeft ? 0.2 : -0.2]}
      >
        <capsuleGeometry args={[0.03, 0.12, 8, 16]} />
        <meshStandardMaterial color={palmColor} roughness={0.5} />
      </mesh>
    </group>
  );
}

export default Hands;
