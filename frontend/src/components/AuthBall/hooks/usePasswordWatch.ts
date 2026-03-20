/**
 * usePasswordWatch - 密码框监听 Hook
 * 监听页面中所有 input[type="password"] 的 focus/blur 事件
 */
import { useState, useEffect, useCallback, useRef } from 'react';

interface PasswordWatchResult {
  /** 是否密码框聚焦 */
  isPasswordFocused: boolean;
  /** 手动设置聚焦状态（用于外部触发） */
  setPasswordFocused: (focused: boolean) => void;
}

/**
 * usePasswordWatch Hook
 * 
 * @example
 * ```tsx
 * const { isPasswordFocused } = usePasswordWatch();
 * ```
 */
export function usePasswordWatch(): PasswordWatchResult {
  const [isPasswordFocused, setIsPasswordFocused] = useState(false);
  const passwordInputRefs = useRef<Set<HTMLInputElement>>(new Set());

  // 处理焦点事件
  const handleFocus = useCallback(() => {
    setIsPasswordFocused(true);
  }, []);

  const handleBlur = useCallback(() => {
    setIsPasswordFocused(false);
  }, []);

  // 绑定密码框事件
  const bindPasswordInputs = useCallback(() => {
    // 清除旧的监听
    passwordInputRefs.current.forEach((input) => {
      input.removeEventListener('focus', handleFocus);
      input.removeEventListener('blur', handleBlur);
    });
    passwordInputRefs.current.clear();

    // 查找所有密码框
    const passwordInputs = document.querySelectorAll<HTMLInputElement>('input[type="password"]');
    passwordInputs.forEach((input) => {
      input.addEventListener('focus', handleFocus);
      input.addEventListener('blur', handleBlur);
      passwordInputRefs.current.add(input);
    });

    // 监听 DOM 变化（处理动态添加的密码框）
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node instanceof HTMLInputElement && node.type === 'password') {
            node.addEventListener('focus', handleFocus);
            node.addEventListener('blur', handleBlur);
            passwordInputRefs.current.add(node);
          } else if (node instanceof Element) {
            // 检查子元素
            const childPasswords = node.querySelectorAll?.('input[type="password"]');
            childPasswords?.forEach((input) => {
              if (input instanceof HTMLInputElement && !passwordInputRefs.current.has(input)) {
                input.addEventListener('focus', handleFocus);
                input.addEventListener('blur', handleBlur);
                passwordInputRefs.current.add(input);
              }
            });
          }
        });
        
        mutation.removedNodes.forEach((node) => {
          if (node instanceof HTMLInputElement && node.type === 'password') {
            node.removeEventListener('focus', handleFocus);
            node.removeEventListener('blur', handleBlur);
            passwordInputRefs.current.delete(node);
          }
        });
      });
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });

    return () => {
      observer.disconnect();
      passwordInputRefs.current.forEach((input) => {
        input.removeEventListener('focus', handleFocus);
        input.removeEventListener('blur', handleBlur);
      });
    };
  }, [handleFocus, handleBlur]);

  useEffect(() => {
    const cleanup = bindPasswordInputs();
    return cleanup;
  }, [bindPasswordInputs]);

  const setPasswordFocused = useCallback((focused: boolean) => {
    setIsPasswordFocused(focused);
  }, []);

  return {
    isPasswordFocused,
    setPasswordFocused,
  };
}

export default usePasswordWatch;
