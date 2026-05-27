/* eslint-disable react-refresh/only-export-components -- route config exports metadata for navigation */
import { lazy } from 'react';
import type { RouteObject } from 'react-router-dom';
import { Layout } from '@/layout';

export const RoutePath = {
  HOME: '/',
} as const;

const Home = lazy(() => import('@/pages/Home/index'));

export const routes: RouteObject[] = [
  {
    path: RoutePath.HOME,
    element: <Layout />,
    children: [
      {
        index: true,
        element: <Home />,
      },
    ],
  },
];

export const routeMeta: Record<keyof typeof RoutePath, { title: string; requiresAuth?: boolean }> = {
  HOME: { title: '首页' },
};
