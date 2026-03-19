/**
 * AuthBall - 3D 拟人化球体组件
 *
 * 功能：
 * - 3D 球体渲染
 * - 呼吸动画（持续）
 * - 眼睛跟随鼠标移动
 * - 根据状态变化表情
 */
import { useRef, useMemo, useEffect } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { Environment } from '@react-three/drei';
import * as THREE from 'three';

// ============ 类型定义 ============

type BallState = 'default' | 'looking' | 'shy' | 'happy';

interface AuthBallProps {
  /** 球体状态 */
  state?: BallState;
  /** 球体大小 */
  size?: number;
  /** 是否启用鼠标跟随 */
  mouseFollow?: boolean;
  /** 类名 */
  className?: string;
}

// ============ 眼睛组件 ============

interface EyesProps {
  state: BallState;
}

function Eyes({ state }: EyesProps) {
  const leftEyeRef = useRef<THREE.Group>(null);
  const rightEyeRef = useRef<THREE.Group>(null);
  const { size } = useThree();

  // 目标旋转角度（平滑插值用）
  const targetRotation = useRef({ x: 0, y: 0 });
  // 当前旋转（插值结果）
  const currentRotation = useRef({ x: 0, y: 0 });
  // 鼠标归一化坐标
  const mouse = useMemo(() => ({ x: 0, y: 0 }), []);

  // 眨眼状态
  const blinkScale = useRef(1);
  const blinkTime = useRef(0);

  // 监听鼠标移动（挂载时注册，卸载时清理）
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
      mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, [mouse, size]);

  useFrame((_, delta) => {
    // 计算目标旋转
    targetRotation.current.x = mouse.y * 0.3;
    targetRotation.current.y = mouse.x * 0.5;

    // 平滑插值
    currentRotation.current.x = THREE.MathUtils.lerp(
      currentRotation.current.x,
      targetRotation.current.x,
      0.1
    );
    currentRotation.current.y = THREE.MathUtils.lerp(
      currentRotation.current.y,
      targetRotation.current.y,
      0.1
    );

    // 更新眼睛旋转
    if (leftEyeRef.current) {
      leftEyeRef.current.rotation.x = currentRotation.current.x;
      leftEyeRef.current.rotation.y = currentRotation.current.y;
    }
    if (rightEyeRef.current) {
      rightEyeRef.current.rotation.x = currentRotation.current.x;
      rightEyeRef.current.rotation.y = currentRotation.current.y;
    }

    // 眨眼动画（每 ~3 秒眨一次）
    blinkTime.current += delta;
    if (blinkTime.current > 3 && blinkTime.current < 3.12) {
      blinkScale.current = 0.08;
    } else {
      blinkScale.current = THREE.MathUtils.lerp(blinkScale.current, 1, 0.25);
    }
    if (blinkTime.current > 3.5) blinkTime.current = 0;

    // 将眨眼缩放应用到瞳孔 mesh（通过 userData 引用）
    if (leftEyeRef.current) {
      const pupil = leftEyeRef.current.getObjectByName('pupil') as THREE.Mesh | undefined;
      if (pupil) pupil.scale.y = blinkScale.current;
    }
    if (rightEyeRef.current) {
      const pupil = rightEyeRef.current.getObjectByName('pupil') as THREE.Mesh | undefined;
      if (pupil) pupil.scale.y = blinkScale.current;
    }
  });

  // 瞳孔颜色根据状态变化
  const pupilColor =
    state === 'happy' ? '#22c55e' : state === 'shy' ? '#f472b6' : '#1e293b';

  return (
    <>
      {/* 左眼 */}
      <group ref={leftEyeRef} position={[-0.2, 0.15, 0.8]}>
        <mesh>
          <sphereGeometry args={[0.12, 32, 32]} />
          <meshStandardMaterial color="#ffffff" />
        </mesh>
        <mesh name="pupil" position={[0, 0, 0.1]}>
          <circleGeometry args={[0.06, 32]} />
          <meshStandardMaterial color={pupilColor} />
        </mesh>
        <mesh position={[0.02, 0.02, 0.12]}>
          <circleGeometry args={[0.02, 32]} />
          <meshBasicMaterial color="#ffffff" />
        </mesh>
      </group>

      {/* 右眼 */}
      <group ref={rightEyeRef} position={[0.2, 0.15, 0.8]}>
        <mesh>
          <sphereGeometry args={[0.12, 32, 32]} />
          <meshStandardMaterial color="#ffffff" />
        </mesh>
        <mesh name="pupil" position={[0, 0, 0.1]}>
          <circleGeometry args={[0.06, 32]} />
          <meshStandardMaterial color={pupilColor} />
        </mesh>
        <mesh position={[0.02, 0.02, 0.12]}>
          <circleGeometry args={[0.02, 32]} />
          <meshBasicMaterial color="#ffffff" />
        </mesh>
      </group>
    </>
  );
}

// ============ 嘴巴组件 ============

interface MouthProps {
  state: BallState;
}

function Mouth({ state }: MouthProps) {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame(() => {
    if (!meshRef.current) return;

    if (state === 'happy') {
      meshRef.current.rotation.z = THREE.MathUtils.lerp(
        meshRef.current.rotation.z, 0.1, 0.1
      );
      meshRef.current.scale.y = THREE.MathUtils.lerp(
        meshRef.current.scale.y, 1.5, 0.1
      );
    } else if (state === 'shy') {
      meshRef.current.rotation.z = THREE.MathUtils.lerp(
        meshRef.current.rotation.z, 0, 0.1
      );
      meshRef.current.scale.y = THREE.MathUtils.lerp(
        meshRef.current.scale.y, 0.5, 0.1
      );
    } else {
      meshRef.current.rotation.z = THREE.MathUtils.lerp(
        meshRef.current.rotation.z, -0.05, 0.1
      );
      meshRef.current.scale.y = THREE.MathUtils.lerp(
        meshRef.current.scale.y, 1, 0.1
      );
    }
  });

  return (
    <mesh ref={meshRef} position={[0, -0.15, 0.85]}>
      <torusGeometry args={[0.08, 0.02, 16, 32, Math.PI]} />
      <meshStandardMaterial color="#1e293b" />
    </mesh>
  );
}

// ============ 呼吸动画球体 ============

interface BreathingBallProps {
  size: number;
  state: BallState;
}

function BreathingBall({ size, state }: BreathingBallProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const breatheTime = useRef(0);

  const baseColor = state === 'shy' ? '#fda4af' : '#e0e7ff';

  useFrame((_, delta) => {
    if (!meshRef.current) return;

    breatheTime.current += delta;

    // 呼吸缩放
    const breatheScale = 1 + Math.sin(breatheTime.current * 1.5) * 0.03;
    meshRef.current.scale.setScalar(breatheScale);

    // 漂浮上下
    meshRef.current.position.y = Math.sin(breatheTime.current * 0.8) * 0.05;
  });

  return (
    <mesh ref={meshRef}>
      <sphereGeometry args={[size, 64, 64]} />
      <meshStandardMaterial
        color={baseColor}
        roughness={0.3}
        metalness={0.1}
        envMapIntensity={0.5}
      />
    </mesh>
  );
}

// ============ 3D 场景 ============

interface SceneProps {
  size: number;
  state: BallState;
}

function Scene({ size, state }: SceneProps) {
  return (
    <>
      <ambientLight intensity={0.4} />
      <directionalLight position={[5, 5, 5]} intensity={1} castShadow />
      <directionalLight position={[-5, 3, -5]} intensity={0.3} color="#b4c6ff" />

      <BreathingBall size={size} state={state} />
      <Eyes state={state} />
      <Mouth state={state} />

      <Environment preset="city" />
    </>
  );
}

// ============ 主组件 ============

export function AuthBall({
  state = 'default',
  size = 1.5,
  mouseFollow: _mouseFollow = true,
  className = '',
}: AuthBallProps) {
  return (
    <div className={className} style={{ width: '100%', height: '400px' }}>
      <Canvas
        camera={{ position: [0, 0, 5], fov: 50 }}
        gl={{ antialias: true, alpha: true }}
      >
        <Scene size={size} state={state} />
      </Canvas>
    </div>
  );
}

export default AuthBall;
