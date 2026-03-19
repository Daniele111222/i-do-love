/**
 * 鼠标位置 Hook
 * 用于 3D 球体眼睛跟随
 */
import { useState, useEffect, useCallback, RefObject } from 'react';
import { useThree } from '@react-three/fiber';

interface MousePosition {
  x: number; // 归一化 -1 到 1
  y: number; // 归一化 -1 到 1
  rawX: number; // 原始屏幕坐标
  rawY: number;
}

/**
 * 在 React 组件中使用：跟踪鼠标在视口中的位置
 */
export function useMousePosition(): MousePosition {
  const [position, setPosition] = useState<MousePosition>({
    x: 0,
    y: 0,
    rawX: 0,
    rawY: 0,
  });

  useEffect(() => {
    const handleMouseMove = (event: MouseEvent) => {
      // 归一化到 -1 到 1
      const x = (event.clientX / window.innerWidth) * 2 - 1;
      const y = -(event.clientY / window.innerHeight) * 2 + 1;

      setPosition({
        x,
        y,
        rawX: event.clientX,
        rawY: event.clientY,
      });
    };

    window.addEventListener('mousemove', handleMouseMove);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, []);

  return position;
}

/**
 * 在 R3F Canvas 中使用：跟踪鼠标在 3D 空间中的位置
 * 返回归一化的鼠标位置，可直接用于 3D 对象
 */
export function useMousePosition3D(): { x: number; y: number } {
  // 使用 useThree 确保此 hook 在 R3F Canvas 上下文中使用
  useThree();
  const [position, setPosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (event: MouseEvent) => {
      // 计算相对于视口中心的位置
      const x = (event.clientX / window.innerWidth) * 2 - 1;
      const y = -(event.clientY / window.innerHeight) * 2 + 1;

      setPosition({ x, y });
    };

    window.addEventListener('mousemove', handleMouseMove);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, []);

  return position;
}

/**
 * 跟踪鼠标相对于特定元素的相对位置
 */
export function useRelativeMousePosition(
  ref: RefObject<HTMLElement>
): MousePosition {
  const [position, setPosition] = useState<MousePosition>({
    x: 0,
    y: 0,
    rawX: 0,
    rawY: 0,
  });

  const handleMouseMove = useCallback((event: MouseEvent) => {
    if (!ref.current) return;

    const rect = ref.current.getBoundingClientRect();
    const relativeX = event.clientX - rect.left;
    const relativeY = event.clientY - rect.top;

    // 归一化到 -1 到 1
    const x = (relativeX / rect.width) * 2 - 1;
    const y = -((relativeY / rect.height) * 2 - 1);

    setPosition({
      x,
      y,
      rawX: relativeX,
      rawY: relativeY,
    });
  }, [ref]);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    element.addEventListener('mousemove', handleMouseMove);

    return () => {
      element.removeEventListener('mousemove', handleMouseMove);
    };
  }, [ref, handleMouseMove]);

  return position;
}
