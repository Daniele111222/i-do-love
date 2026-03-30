import { useState, useEffect, useCallback, useRef } from 'react';

interface PasswordWatchResult {
  isPasswordFocused: boolean;
  // eslint-disable-next-line no-unused-vars
  setPasswordFocused(nextFocused: boolean): void;
}

export function usePasswordWatch(): PasswordWatchResult {
  const [isPasswordFocused, setIsPasswordFocused] = useState(false);
  const passwordInputRefs = useRef<Set<HTMLInputElement>>(new Set());

  const handleFocus = useCallback(() => {
    setIsPasswordFocused(true);
  }, []);

  const handleBlur = useCallback(() => {
    setIsPasswordFocused(false);
  }, []);

  const bindPasswordInputs = useCallback(() => {
    passwordInputRefs.current.forEach((input) => {
      input.removeEventListener('focus', handleFocus);
      input.removeEventListener('blur', handleBlur);
    });
    passwordInputRefs.current.clear();

    const passwordInputs = document.querySelectorAll<HTMLInputElement>('input[type="password"]');
    passwordInputs.forEach((input) => {
      input.addEventListener('focus', handleFocus);
      input.addEventListener('blur', handleBlur);
      passwordInputRefs.current.add(input);
    });

    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node instanceof HTMLInputElement && node.type === 'password') {
            node.addEventListener('focus', handleFocus);
            node.addEventListener('blur', handleBlur);
            passwordInputRefs.current.add(node);
          } else if (node instanceof Element) {
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
  }, [handleBlur, handleFocus]);

  useEffect(() => {
    const cleanup = bindPasswordInputs();
    return cleanup;
  }, [bindPasswordInputs]);

  const setPasswordFocused = useCallback((nextFocused: boolean) => {
    setIsPasswordFocused(nextFocused);
  }, []);

  return {
    isPasswordFocused,
    setPasswordFocused,
  };
}

export default usePasswordWatch;
