/**
 * Input 输入框组件
 * 支持多种状态和类型
 */
import { forwardRef, InputHTMLAttributes, ReactNode, useState, useId } from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

// 输入框尺寸
type InputSize = 'sm' | 'md' | 'lg';
// 输入框类型
type InputType = 'text' | 'email' | 'password' | 'number' | 'search' | 'url';

interface InputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size' | 'type'> {
  /** 标签 */
  label?: string;
  /** 输入框类型 */
  type?: InputType;
  /** 错误信息 */
  error?: string;
  /** 提示文字 */
  hint?: string;
  /** 尺寸 */
  size?: InputSize;
  /** 左侧图标 */
  leftIcon?: ReactNode;
  /** 右侧图标 */
  rightIcon?: ReactNode;
  /** 是否加载中 */
  loading?: boolean;
  /** 全宽 */
  fullWidth?: boolean;
}

const sizeStyles: Record<InputSize, string> = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-base',
  lg: 'px-5 py-3 text-lg',
};

/**
 * Input 组件
 *
 * @example
 * ```tsx
 * <Input label="邮箱" type="email" placeholder="请输入邮箱" error={errors.email} />
 * ```
 */
export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      label,
      type = 'text',
      error,
      hint,
      size = 'md',
      leftIcon,
      rightIcon,
      loading,
      fullWidth = true,
      className,
      disabled,
      id,
      ...props
    },
    ref
  ) => {
    const [showPassword, setShowPassword] = useState(false);
    const generatedId = useId();
    const inputId = id || generatedId;
    const isPassword = type === 'password';
    const actualType = isPassword ? (showPassword ? 'text' : 'password') : type;

    return (
      <div className={twMerge(clsx('flex flex-col gap-1', fullWidth && 'w-full'))}>
        {/* 标签 */}
        {label && (
          <label htmlFor={inputId} className="text-sm font-medium text-gray-700 dark:text-gray-300">
            {label}
          </label>
        )}

        {/* 输入框容器 */}
        <div className="relative">
          {/* 左侧图标 */}
          {leftIcon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">{leftIcon}</div>
          )}

          {/* 输入框 */}
          <input
            ref={ref}
            id={inputId}
            type={actualType}
            disabled={disabled || loading}
            className={twMerge(
              clsx(
                'block rounded-lg border bg-white dark:bg-gray-800',
                'text-gray-900 dark:text-gray-100',
                'placeholder:text-gray-400 dark:placeholder:text-gray-500',
                'transition-colors duration-200',
                sizeStyles[size],
                leftIcon && 'pl-10',
                (rightIcon || isPassword) && 'pr-10',
                'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent',
                error
                  ? 'border-red-500 focus:ring-red-500'
                  : 'border-gray-300 dark:border-gray-600',
                disabled && 'opacity-50 cursor-not-allowed bg-gray-100 dark:bg-gray-700',
                className
              )
            )}
            aria-invalid={error ? 'true' : 'false'}
            aria-describedby={
              error ? `${inputId}-error` : hint ? `${inputId}-hint` : undefined
            }
            {...props}
          />

          {/* 右侧图标 */}
          {rightIcon && !isPassword && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">{rightIcon}</div>
          )}

          {/* 密码显示切换 */}
          {isPassword && (
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              {showPassword ? (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              )}
            </button>
          )}

          {/* 加载指示器 */}
          {loading && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2">
              <svg className="animate-spin h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
            </div>
          )}
        </div>

        {/* 错误信息 */}
        {error && (
          <p id={`${inputId}-error`} className="text-sm text-red-500">
            {error}
          </p>
        )}

        {/* 提示文字 */}
        {hint && !error && (
          <p id={`${inputId}-hint`} className="text-sm text-gray-500 dark:text-gray-400">
            {hint}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input;
