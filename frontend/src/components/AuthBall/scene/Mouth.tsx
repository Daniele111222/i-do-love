/**
 * Mouth - 嘴巴组件
 * 根据情绪状态变化形态（微笑/大笑/下垂等）
 */
import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import type { EmotionState } from '../types/authBall.types';
import { MOUTH_CONFIGS as configs } from '../types/authBall.types';

interface MouthProps {
  /** 当前情绪状态 */
  emotion: EmotionState;
}

const MOUTH_POSITION = { x: 0, y: -0.2, z: 0.9 };

/**
 * Mouth 组件
 * 通过 THREE.Shape 创建曲线嘴巴
 */
export function Mouth({ emotion }: MouthProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const config = configs[emotion];

  useFrame(() => {
    if (!meshRef.current) return;
    
    // 动画过渡 - 可扩展
    const scale = 1 + (config.openness * 0.2);
    meshRef.current.scale.y = THREE.MathUtils.lerp(
      meshRef.current.scale.y,
      scale,
      0.15
    );
  });

  // 创建嘴巴形状
  const geometry = useMemo(() => {
    return createMouthGeometry(config.curve, config.openness);
  }, [config.curve, config.openness]);

  return (
    <mesh
      ref={meshRef}
      position={[MOUTH_POSITION.x, MOUTH_POSITION.y, MOUTH_POSITION.z]}
    >
      <primitive object={geometry} attach="geometry" />
      <meshBasicMaterial color="#4a4a5a" side={THREE.DoubleSide} />
    </mesh>
  );
}

/**
 * 根据曲线类型创建嘴巴几何体
 */
function createMouthGeometry(curve: string, openness: number): THREE.ShapeGeometry {
  const shape = new THREE.Shape();
  
  const width = 0.25;
  const height = 0.06 + (openness * 0.1); // 张嘴程度影响高度
  
  switch (curve) {
    case 'slight-smile': {
      // 轻微上扬的弧线 - 无奈的微笑
      shape.moveTo(-width / 2, 0);
      shape.quadraticCurveTo(0, height * 0.3, width / 2, 0);
      shape.quadraticCurveTo(0, -height * 0.1, -width / 2, 0);
      break;
    }
    
    case 'neutral': {
      // 直线 - neutral
      shape.moveTo(-width / 2, 0);
      shape.lineTo(width / 2, 0);
      shape.lineTo(width / 2, height * 0.2);
      shape.lineTo(-width / 2, height * 0.2);
      shape.closePath();
      break;
    }
    
    case 'D-shape': {
      // D型 - 大笑
      // 上边是直线，下边是半圆弧
      const radius = width / 2;
      shape.moveTo(-width / 2, 0);
      shape.lineTo(width / 2, 0);  // 上边
      shape.absarc(0, 0, radius, 0, Math.PI, false);  // 下半圆
      shape.lineTo(-width / 2, 0);
      break;
    }
    
    case 'frown': {
      // 下垂 - 不开心
      shape.moveTo(-width / 2, height * 0.3);
      shape.quadraticCurveTo(0, -height * 0.2, width / 2, height * 0.3);
      shape.quadraticCurveTo(0, height * 0.1, -width / 2, height * 0.3);
      break;
    }
    
    default: {
      shape.moveTo(-width / 2, 0);
      shape.quadraticCurveTo(0, height * 0.3, width / 2, 0);
      shape.quadraticCurveTo(0, -height * 0.1, -width / 2, 0);
    }
  }
  
  return new THREE.ShapeGeometry(shape, 32);
}

export default Mouth;
