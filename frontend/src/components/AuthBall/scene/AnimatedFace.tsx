/**
 * AnimatedFace - 带动画的面部特征
 * 包含眼睛（含瞳孔跟随、眨眼）、眉毛、嘴巴
 */
import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import type { EmotionState } from '../types/authBall.types';

// 眨眼参数
const BLINK_DURATION = 0.15;
const BLINK_INTERVAL_BASE = 2500;

/** 球体颜色映射（用于眼皮和脸红） */
const SPHERE_COLORS: Record<EmotionState, string> = {
  idle: '#8B7CF8',
  hover: '#7B6CE8',
  'focus-password': '#F87CA8',
  success: '#6EE7A0',
  error: '#5A5A7A',
};

/** 眉毛配置 */
const BROW_CONFIGS: Record<EmotionState, { rotZ: number; posY: number }> = {
  idle: { rotZ: 0, posY: 0 },
  hover: { rotZ: 0.15, posY: 0.05 },
  'focus-password': { rotZ: 0.1, posY: 0.06 },
  success: { rotZ: 0.25, posY: 0.08 },
  error: { rotZ: 0.25, posY: -0.02 },
};

interface AnimatedFaceProps {
  emotion: EmotionState;
  mouseNorm: { x: number; y: number };
  isEyeTrackingActive: boolean;
}

/**
 * AnimatedFace 组件
 */
export function AnimatedFace({ emotion, mouseNorm, isEyeTrackingActive }: AnimatedFaceProps) {
  return (
    <group>
      {/* 左眼 */}
      <AnimatedEye
        emotion={emotion}
        side="left"
        mouseNorm={mouseNorm}
        isEyeTrackingActive={isEyeTrackingActive}
      />
      
      {/* 右眼 */}
      <AnimatedEye
        emotion={emotion}
        side="right"
        mouseNorm={mouseNorm}
        isEyeTrackingActive={isEyeTrackingActive}
      />
      
      {/* 左眉 */}
      <AnimatedBrow emotion={emotion} side="left" />
      
      {/* 右眉 */}
      <AnimatedBrow emotion={emotion} side="right" />
      
      {/* 嘴巴 */}
      <AnimatedMouth emotion={emotion} />
    </group>
  );
}

interface AnimatedEyeProps {
  emotion: EmotionState;
  side: 'left' | 'right';
  mouseNorm: { x: number; y: number };
  isEyeTrackingActive: boolean;
}

function AnimatedEye({ emotion, side, mouseNorm, isEyeTrackingActive }: AnimatedEyeProps) {
  const groupRef = useRef<THREE.Group>(null);
  const pupilRef = useRef<THREE.Mesh>(null);
  const upperEyelidRef = useRef<THREE.Mesh>(null);
  
  // 动画状态
  const animRef = useRef({
    pupilX: 0,
    pupilY: 0,
    blinkProgress: 0,
    isBlinking: false,
    blinkPhase: 0,
    nextBlinkTime: 0,
    consecutiveBlinks: 0,
  });

  // 眼睛位置
  const eyeX = side === 'left' ? -0.35 : 0.35;

  useFrame((state, delta) => {
    const anim = animRef.current;
    const elapsed = state.clock.getElapsedTime();

    // 瞳孔跟随
    if (isEyeTrackingActive) {
      const targetX = mouseNorm.x * 0.08;
      const targetY = mouseNorm.y * 0.08 - (emotion === 'focus-password' ? 0.04 : 0);
      
      anim.pupilX = THREE.MathUtils.lerp(anim.pupilX, targetX, 0.15);
      anim.pupilY = THREE.MathUtils.lerp(anim.pupilY, targetY, 0.15);
    } else {
      anim.pupilX = THREE.MathUtils.lerp(anim.pupilX, 0, 0.04);
      anim.pupilY = THREE.MathUtils.lerp(anim.pupilY, 0, 0.04);
    }

    if (pupilRef.current) {
      pupilRef.current.position.x = anim.pupilX;
      pupilRef.current.position.y = anim.pupilY;
    }

    // 眨眼
    if (!anim.isBlinking && elapsed >= anim.nextBlinkTime) {
      anim.isBlinking = true;
      anim.blinkPhase = 0;
      anim.blinkProgress = 0;
    }

    if (anim.isBlinking) {
      const blinkSpeed = 1 / BLINK_DURATION;
      
      if (anim.blinkPhase === 0) {
        // 闭合中
        anim.blinkProgress += delta * blinkSpeed;
        if (anim.blinkProgress >= 1) {
          anim.blinkProgress = 1;
          anim.blinkPhase = 1;
          
          // hover 时双击眨眼
          if (emotion === 'hover' && anim.consecutiveBlinks < 1) {
            anim.consecutiveBlinks++;
          } else {
            anim.consecutiveBlinks = 0;
            anim.isBlinking = false;
            anim.blinkProgress = 0;
            anim.nextBlinkTime = elapsed + getBlinkInterval(emotion);
          }
        }
      } else {
        // 睁开中
        anim.blinkProgress -= delta * blinkSpeed * 1.5;
        if (anim.blinkProgress <= 0) {
          anim.blinkProgress = 0;
          
          if (emotion === 'hover' && anim.consecutiveBlinks < 1) {
            anim.blinkPhase = 0;
          } else {
            anim.isBlinking = false;
            anim.nextBlinkTime = elapsed + getBlinkInterval(emotion);
          }
        }
      }
    }

    // 更新眼皮
    if (upperEyelidRef.current) {
      upperEyelidRef.current.scale.y = 1 - anim.blinkProgress;
      // 眼皮位置随眨眼移动
      upperEyelidRef.current.position.y = 0.37 - anim.blinkProgress * 0.2;
    }
  });

  return (
    <group ref={groupRef} position={[eyeX, 0.15, 0.85]}>
      {/* 眼白 */}
      <mesh>
        <sphereGeometry args={[0.22, 32, 32]} />
        <meshStandardMaterial color="#FFFFFF" roughness={0.3} />
      </mesh>
      
      {/* 瞳孔 */}
      <mesh ref={pupilRef} position={[0, 0, 0.18]}>
        <sphereGeometry args={[0.12, 32, 32]} />
        <meshStandardMaterial color="#1a1a2e" roughness={0.2} />
      </mesh>
      
      {/* 高光 */}
      <mesh position={[-0.05, 0.08, 0.22]}>
        <sphereGeometry args={[0.04, 16, 16]} />
        <meshBasicMaterial color="#FFFFFF" />
      </mesh>
      
      {/* 上眼皮 */}
      <mesh ref={upperEyelidRef} position={[0, 0.37, 0.01]}>
        <planeGeometry args={[0.5, 0.35]} />
        <meshBasicMaterial
          color={SPHERE_COLORS[emotion]}
          transparent
          opacity={1}
          side={THREE.DoubleSide}
        />
      </mesh>
    </group>
  );
}

interface AnimatedBrowProps {
  emotion: EmotionState;
  side: 'left' | 'right';
}

function AnimatedBrow({ emotion, side }: AnimatedBrowProps) {
  const browRef = useRef<THREE.Mesh>(null);

  useFrame(() => {
    const config = BROW_CONFIGS[emotion];
    const targetRotZ = side === 'left' ? config.rotZ : -config.rotZ;
    const targetPosY = 0.38 + config.posY;

    if (browRef.current) {
      browRef.current.rotation.z = THREE.MathUtils.lerp(browRef.current.rotation.z, targetRotZ, 0.15);
      browRef.current.position.y = THREE.MathUtils.lerp(browRef.current.position.y, targetPosY, 0.15);
    }
  });

  const browX = side === 'left' ? -0.35 : 0.35;

  return (
    <mesh ref={browRef} position={[browX, 0.38, 0.88]}>
      <boxGeometry args={[0.28, 0.045, 0.04]} />
      <meshStandardMaterial color="#2d2d3a" roughness={0.6} />
    </mesh>
  );
}

interface AnimatedMouthProps {
  emotion: EmotionState;
}

function AnimatedMouth({ emotion }: AnimatedMouthProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const animRef = useRef({ openness: 0 });

  // 根据情绪状态计算目标张嘴程度
  const targetOpenness = useMemo(() => {
    switch (emotion) {
      case 'success': return 0.8;
      case 'error': return 0.1;
      default: return 0;
    }
  }, [emotion]);

  useFrame(() => {
    animRef.current.openness = THREE.MathUtils.lerp(
      animRef.current.openness,
      targetOpenness,
      0.15
    );

    if (meshRef.current) {
      meshRef.current.scale.y = 1 + animRef.current.openness * 0.3;
    }
  });

  // 创建嘴巴几何体
  const geometry = useMemo(() => {
    return createMouthGeometry(emotion);
  }, [emotion]);

  return (
    <mesh ref={meshRef} position={[0, -0.2, 0.9]}>
      <primitive object={geometry} attach="geometry" />
      <meshBasicMaterial color="#4a4a5a" side={THREE.DoubleSide} />
    </mesh>
  );
}

/** 创建嘴巴几何体 */
function createMouthGeometry(emotion: EmotionState): THREE.ShapeGeometry {
  const shape = new THREE.Shape();
  const width = 0.25;
  const baseHeight = 0.06;
  const openness = emotion === 'success' ? 0.15 : emotion === 'error' ? 0.03 : 0.03;
  const height = baseHeight + openness;

  switch (emotion) {
    case 'success':
      // D型嘴 - 大笑
      shape.moveTo(-width / 2, 0);
      shape.lineTo(width / 2, 0);
      shape.absarc(0, 0, width / 2, 0, Math.PI, false);
      shape.lineTo(-width / 2, 0);
      break;

    case 'error':
      // 下垂嘴角 - 难过
      shape.moveTo(-width / 2, height * 0.3);
      shape.quadraticCurveTo(0, -height * 0.2, width / 2, height * 0.3);
      shape.quadraticCurveTo(0, height * 0.1, -width / 2, height * 0.3);
      break;

    default:
      // 轻微微笑 - 无奈营业
      shape.moveTo(-width / 2, 0);
      shape.quadraticCurveTo(0, height * 0.3, width / 2, 0);
      shape.quadraticCurveTo(0, -height * 0.1, -width / 2, 0);
  }

  return new THREE.ShapeGeometry(shape, 32);
}

/** 获取眨眼间隔 */
function getBlinkInterval(emotion: EmotionState): number {
  switch (emotion) {
    case 'hover': return 1500 + Math.random() * 1000;
    case 'focus-password': return 3000 + Math.random() * 1500;
    case 'success': return 2000 + Math.random() * 1000;
    case 'error': return 4000 + Math.random() * 2000;
    default: return BLINK_INTERVAL_BASE + Math.random() * 1500;
  }
}


