/* eslint-disable react-refresh/only-export-components */
/**
 * 路由配置
 * 集中管理所有路由定义
 */
import { lazy } from 'react';
import type { RouteObject } from 'react-router-dom';

// 路由路径常量
export const RoutePath = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  AUTH_BALL_TEST: '/auth-ball-test',
} as const;

// 使用 lazy 导入提升性能
const Home = lazy(() => import('@/pages/Home/index'));
const Login = lazy(() => import('@/pages/login/index'));
const Register = lazy(() => import('@/pages/Register/index'));
const AuthBallTest = lazy(() => import('@/pages/AuthBallTest/index'));

/**
 * 路由配置数组
 * 用于 react-router-dom 的 createBrowserRouter 或 Routes 组件
 */
export const routes: RouteObject[] = [
  {
    path: RoutePath.HOME,
    element: <Home />,
  },
  {
    path: RoutePath.LOGIN,
    element: <Login />,
  },
  {
    path: RoutePath.REGISTER,
    element: <Register />,
  },
  {
    path: RoutePath.AUTH_BALL_TEST,
    element: <AuthBallTest />,
  },
];

/**
 * 路由元数据（用于菜单、权限等场景）
 */
export const routeMeta: Record<string, { title: string; requiresAuth?: boolean }> = {
  [RoutePath.HOME]: { title: '首页' },
  [RoutePath.LOGIN]: { title: '登录' },
  [RoutePath.REGISTER]: { title: '注册' },
  [RoutePath.AUTH_BALL_TEST]: { title: 'AuthBall 测试' },
};
