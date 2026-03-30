/**
 * State reducer for AuthBall.
 */
import { useMemo } from 'react';
import type { BallState, EmotionState } from '../types/authBall.types';

const STATE_MAP: Record<BallState, EmotionState> = {
  default: 'idle',
  looking: 'hover',
  shy: 'focus-password',
  happy: 'success',
};

interface UseAuthBallStateOptions {
  externalState: BallState;
  isPasswordFocused: boolean;
  isError: boolean;
  isSuccess: boolean;
  trackCursor: boolean;
}

interface UseAuthBallStateResult {
  emotion: EmotionState;
  isEyeTrackingActive: boolean;
  priorityLevel: number;
}

const PRIORITY_LEVELS: Record<EmotionState, number> = {
  idle: 0,
  hover: 1,
  'focus-password': 2,
  success: 3,
  error: 4,
};

export function useAuthBallState({
  externalState,
  isPasswordFocused,
  isError,
  isSuccess,
  trackCursor,
}: UseAuthBallStateOptions): UseAuthBallStateResult {
  const emotion = useMemo<EmotionState>(() => {
    if (isError) return 'error';
    if (isSuccess) return 'success';
    if (isPasswordFocused) return 'focus-password';
    return STATE_MAP[externalState] ?? 'idle';
  }, [externalState, isError, isPasswordFocused, isSuccess]);

  const isEyeTrackingActive = useMemo(() => {
    if (!trackCursor) return false;
    if (emotion === 'focus-password' || emotion === 'success' || emotion === 'error') {
      return false;
    }
    return true;
  }, [emotion, trackCursor]);

  return {
    emotion,
    isEyeTrackingActive,
    priorityLevel: PRIORITY_LEVELS[emotion],
  };
}

export default useAuthBallState;
