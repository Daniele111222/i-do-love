/**
 * Layout 组件 - 基础布局
 * 包含 Header + 内容区域 + Footer
 */
import { ReactNode } from 'react';
import { Header } from '../components/Header';

interface LayoutProps {
  /** 子元素 */
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      {/* 顶部导航栏 */}
      <Header />

      {/* 主内容区域 */}
      <main className="flex-1">
        {children}
      </main>

      {/* 页脚 */}
      <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <p className="text-center text-gray-500 dark:text-gray-400">
            © 2026 AI News Hub. 基于 MIT 许可证开源。
          </p>
        </div>
      </footer>
    </div>
  );
}
