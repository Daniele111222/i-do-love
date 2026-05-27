import { Component, type ErrorInfo, type ReactNode } from 'react';
import { Button } from '@/components/ui/button';

interface AppErrorBoundaryProps {
  children: ReactNode;
}

interface AppErrorBoundaryState {
  hasError: boolean;
}

export class AppErrorBoundary extends Component<AppErrorBoundaryProps, AppErrorBoundaryState> {
  state: AppErrorBoundaryState = { hasError: false };

  static getDerivedStateFromError(): AppErrorBoundaryState {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('[AppErrorBoundary]', error, errorInfo);
  }

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        <main className="flex min-h-screen items-center justify-center bg-background px-6">
          <section className="max-w-md text-center">
            <p className="text-sm font-medium text-muted-foreground">Application error</p>
            <h1 className="mt-3 text-2xl font-semibold text-foreground">页面暂时无法显示</h1>
            <p className="mt-3 text-sm leading-6 text-muted-foreground">
              请刷新页面重试。如果问题持续出现，保留当前操作路径并检查最近的前端改动。
            </p>
            <Button className="mt-6" onClick={() => window.location.reload()}>
              刷新页面
            </Button>
          </section>
        </main>
      );
    }

    return this.props.children;
  }
}
