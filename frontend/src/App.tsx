/**
 * 应用根组件
 */
import { Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';
import { routes } from '@/routes';

// 加载中 fallback
function LoadingFallback() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
    </div>
  );
}

/**
 * App 根组件
 * 使用 routes 配置渲染路由
 */
function App() {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <Routes>
        {routes.map((route) => (
          <Route
            key={route.path}
            path={route.path}
            element={route.element}
          />
        ))}
      </Routes>
    </Suspense>
  );
}

export default App;
