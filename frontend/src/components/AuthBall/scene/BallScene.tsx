/**
 * BallScene - R3F Canvas 内的场景根节点
 * 组合所有子组件，轻量级协调器
 */
import type { EmotionState } from '../types/authBall.types';
import { AnimatedSphere } from './AnimatedSphere';
import { AnimatedFace } from './AnimatedFace';
import { AnimatedHands } from './AnimatedHands';

interface BallSceneProps {
  /** 当前情绪状态 */
  emotion: EmotionState;
  /** 是否激活眼神跟随 */
  isEyeTrackingActive: boolean;
  /** 球体大小 */
  size: number;
  /** 外部传入的鼠标位置（归一化 -1 to 1） */
  externalMouseNorm: { x: number; y: number };
}

/**
 * BallScene 组件
 * 轻量级协调器，组合子组件
 */
export function BallScene({
  emotion,
  isEyeTrackingActive,
  size,
  externalMouseNorm,
}: BallSceneProps) {
  return (
    <>
      {/* 三点布光系统 */}
      <ThreePointLighting />
      
      {/* 球体主体 - 包含入场动画、呼吸、成功/错误动画 */}
      <AnimatedSphere
        emotion={emotion}
        size={size}
      />
      
      {/* 面部特征 - 眼睛、眉毛、嘴巴独立动画 */}
      <AnimatedFace
        emotion={emotion}
        mouseNorm={externalMouseNorm}
        isEyeTrackingActive={isEyeTrackingActive}
      />
      
      {/* 遮眼手掌 */}
      <AnimatedHands
        emotion={emotion}
        size={size}
      />
    </>
  );
}

/**
 * 三点布光系统
 */
function ThreePointLighting() {
  return (
    <>
      <ambientLight intensity={0.4} />
      {/* 主光源 - 右上方 */}
      <directionalLight
        position={[5, 5, 5]}
        intensity={0.8}
      />
      {/* 补光 - 左上方，冷色调 */}
      <directionalLight
        position={[-3, 2, 4]}
        intensity={0.4}
        color="#b4c6e7"
      />
      {/* 底光 - 暖色调增加层次 */}
      <pointLight
        position={[0, -3, 2]}
        intensity={0.2}
        color="#ffd700"
      />
    </>
  );
}

export default BallScene;
