/**
 * Eyebrows - 眉毛组件
 * 根据情绪状态变化形态
 */
import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import type { EmotionState } from '../types/authBall.types';
import { BROW_CONFIGS } from '../types/authBall.types';

interface EyebrowsProps {
  /** 当前情绪状态 */
  emotion: EmotionState;
}

const BROW_POSITIONS = {
  left: { x: -0.35, y: 0.38, z: 0.88 },
  right: { x: 0.35, y: 0.38, z: 0.88 },
};

const BROW_GEOMETRY = {
  width: 0.28,
  height: 0.045,
  depth: 0.04,
};

/**
 * Eyebrows 组件
 * 左右眉毛，根据情绪状态变化
 */
export function Eyebrows({ emotion }: EyebrowsProps) {
  const leftBrowRef = useRef<THREE.Mesh>(null);
  const rightBrowRef = useRef<THREE.Mesh>(null);

  useFrame(() => {
    // 左右眉毛分别计算
    [leftBrowRef, rightBrowRef].forEach((ref, index) => {
      if (!ref.current) return;
      
      const side = index === 0 ? 'left' : 'right';
      const config = BROW_CONFIGS[emotion];
      
      // 旋转 - 左右眉毛旋转方向相反（形成八字或挑眉效果）
      const rotZMultiplier = side === 'left' ? 1 : -1;
      const targetRotZ = config.rotZ * rotZMultiplier;
      
      ref.current.rotation.z = THREE.MathUtils.lerp(
        ref.current.rotation.z,
        targetRotZ,
        0.15
      );
      
      // Y 位置
      ref.current.position.y = THREE.MathUtils.lerp(
        ref.current.position.y,
        BROW_POSITIONS[side].y + config.posY,
        0.15
      );
    });
  });

  return (
    <group>
      {/* 左眉 */}
      <mesh
        ref={leftBrowRef}
        position={[
          BROW_POSITIONS.left.x,
          BROW_POSITIONS.left.y,
          BROW_POSITIONS.left.z,
        ]}
        rotation={[0.1, 0, 0]}
      >
        <boxGeometry args={[BROW_GEOMETRY.width, BROW_GEOMETRY.height, BROW_GEOMETRY.depth]} />
        <meshStandardMaterial color="#2d2d3a" roughness={0.6} />
      </mesh>
      
      {/* 右眉 */}
      <mesh
        ref={rightBrowRef}
        position={[
          BROW_POSITIONS.right.x,
          BROW_POSITIONS.right.y,
          BROW_POSITIONS.right.z,
        ]}
        rotation={[-0.1, 0, 0]}
      >
        <boxGeometry args={[BROW_GEOMETRY.width, BROW_GEOMETRY.height, BROW_GEOMETRY.depth]} />
        <meshStandardMaterial color="#2d2d3a" roughness={0.6} />
      </mesh>
    </group>
  );
}

export default Eyebrows;
