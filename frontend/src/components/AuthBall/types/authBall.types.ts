/**
 * Shared types for the AuthBall character component.
 */

export type BallState = 'default' | 'looking' | 'shy' | 'happy';

export type EmotionState =
  | 'idle'
  | 'hover'
  | 'focus-password'
  | 'success'
  | 'error';

export type AnimPhase = 'entering' | 'idle';

export interface BallContext {
  emotion: EmotionState;
  animPhase: AnimPhase;
  mouseNorm: { x: number; y: number };
  isPasswordFocused: boolean;
  blinkProgress: number;
  breathOffset: number;
  enterProgress: number;
}

export interface AuthBallProps {
  state?: BallState;
  size?: number;
  className?: string;
  trackCursor?: boolean;
  passwordMode?: 'auto-watch' | 'controlled';
  isPasswordActive?: boolean;
  // eslint-disable-next-line no-unused-vars
  onPasswordFocus?(nextFocused: boolean): void;
}

export const SPHERE_COLORS: Record<EmotionState, string> = {
  idle: '#8B7CF8',
  hover: '#7B6CE8',
  'focus-password': '#F87CA8',
  success: '#6EE7A0',
  error: '#5A5A7A',
};

export interface BrowConfig {
  rotZ: number;
  posY: number;
  innerAngle: number;
}

export const BROW_CONFIGS: Record<EmotionState, BrowConfig> = {
  idle: { rotZ: 0, posY: 0, innerAngle: 0 },
  hover: { rotZ: -0.15, posY: 0.05, innerAngle: -0.15 },
  'focus-password': { rotZ: 0.1, posY: 0.06, innerAngle: 0.15 },
  success: { rotZ: -0.25, posY: 0.08, innerAngle: -0.25 },
  error: { rotZ: 0.25, posY: -0.02, innerAngle: 0.35 },
};

export type MouthCurve = 'slight-smile' | 'neutral' | 'D-shape' | 'frown';

export interface MouthConfig {
  curve: MouthCurve;
  openness: number;
}

export const MOUTH_CONFIGS: Record<EmotionState, MouthConfig> = {
  idle: { curve: 'slight-smile', openness: 0 },
  hover: { curve: 'slight-smile', openness: 0 },
  'focus-password': { curve: 'neutral', openness: 0 },
  success: { curve: 'D-shape', openness: 0.8 },
  error: { curve: 'frown', openness: 0 },
};
