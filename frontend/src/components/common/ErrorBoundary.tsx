/**
 * ErrorBoundary - 错误边界组件
 * 捕获子组件的 JavaScript 错误，显示友好的 Fallback UI
 */
import { Component, type ReactNode } from 'react';

interface ErrorBoundaryProps {
  /** 子组件 */
  children: ReactNode;
  /** 自定义 Fallback 组件 */
  fallback?: ReactNode;
  /** 错误回调 */
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

/**
 * ErrorBoundary 组件
 * 
 * @example
 * ```tsx
 * <ErrorBoundary fallback={<div>出错了</div>}>
 *   <MyComponent />
 * </ErrorBoundary>
 * ```
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    console.error('[ErrorBoundary] Caught error:', error, errorInfo);
    this.props.onError?.(error, errorInfo);
  }

  render(): ReactNode {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="flex flex-col items-center justify-center h-full min-h-[200px] text-center p-4">
          <div className="text-4xl mb-3">😔</div>
          <h3 className="text-lg font-medium text-gray-700 dark:text-gray-200 mb-2">
            页面渲染出错
          </h3>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
            请刷新页面重试
          </p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            刷新页面
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
