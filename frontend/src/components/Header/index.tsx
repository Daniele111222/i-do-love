/**
 * Header 组件 - 顶部导航栏
 */
import { Link } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import { Button } from '@/components/common';

export function Header() {
  const { user, isAuthenticated, isLoading, logout } = useAuthStore();

  return (
    <nav className="bg-white dark:bg-gray-800 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          {/* Logo */}
          <Link to="/" className="flex-shrink-0">
            <h1 className="text-2xl font-bold text-primary-600">
              AI News Hub
            </h1>
          </Link>

          {/* 导航链接 */}
          <div className="flex items-center gap-4">
            {isLoading ? (
              <span className="text-gray-500">加载中...</span>
            ) : isAuthenticated ? (
              <>
                <span className="text-gray-700 dark:text-gray-300">
                  欢迎, {user?.nickname || user?.email}
                </span>
                <Button variant="outline" size="sm" onClick={logout}>
                  登出
                </Button>
              </>
            ) : (
              <>
                <Link to="/login">
                  <Button variant="ghost" size="sm">
                    登录
                  </Button>
                </Link>
                <Link to="/register">
                  <Button size="sm">注册</Button>
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
