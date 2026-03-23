/**
 * 首页
 */
import { Link } from 'react-router-dom';
import { Layout } from '@/layout';
import { Button } from '@/components/common';

export default function Home() {
  return (
    <Layout>
      {/* Hero 区域 */}
      <div className="text-center mb-16">
        <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
          探索 AI 资讯的全新方式
        </h2>
        <p className="text-xl text-gray-600 dark:text-gray-400 mb-8 max-w-2xl mx-auto">
          AI News Hub 是您的一站式 AI 资讯聚合平台，
          支持 OpenClaw 智能体接入，带来全新的智能阅读体验。
        </p>

        <div className="flex justify-center gap-4">
          <Link to="/register">
            <Button size="lg">开始使用</Button>
          </Link>
          <Link to="/login">
            <Button variant="outline" size="lg">
              登录
            </Button>
          </Link>
        </div>
      </div>

      {/* 功能卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
        {/* 特性 1 */}
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm">
          <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-lg flex items-center justify-center mb-4">
            <svg
              className="w-6 h-6 text-primary-600 dark:text-primary-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"
              />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            AI 资讯聚合
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            聚合来自多个源的 AI 相关资讯，为您呈现最全面、最及时的 AI 动态。
          </p>
        </div>

        {/* 特性 2 */}
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm">
          <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-lg flex items-center justify-center mb-4">
            <svg
              className="w-6 h-6 text-primary-600 dark:text-primary-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
              />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            Agents 友好
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            支持 OpenClaw 等 AI 智能体标准化接入，让您的爬虫和智能体轻松集成。
          </p>
        </div>

        {/* 特性 3 */}
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm">
          <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-lg flex items-center justify-center mb-4">
            <svg
              className="w-6 h-6 text-primary-600 dark:text-primary-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 10V3L4 14h7v7l9-11h-7z"
              />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            创新交互体验
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            独特的 3D 拟人化交互动画，带来耳目一新的浏览体验。
          </p>
        </div>
      </div>

      {/* 预留区域提示 */}
      <div className="text-center p-8 bg-gray-200 dark:bg-gray-700 rounded-xl">
        <p className="text-gray-600 dark:text-gray-300">
          更多功能（AI 智能问答、RAG 知识库）正在开发中...
        </p>
      </div>
    </Layout>
  );
}
