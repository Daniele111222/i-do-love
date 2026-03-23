/**
 * 登录页面
 */
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button, Input } from '@/components/common';
import { Layout } from '@/layout';
import { useAuthStore } from '@/stores/authStore';

// 表单验证 schema
const loginSchema = z.object({
  email: z.string().email('请输入有效的邮箱地址'),
  password: z.string().min(1, '请输入密码'),
});

type LoginForm = z.infer<typeof loginSchema>;

export default function Login() {
  const navigate = useNavigate();
  const { login, isLoading, error } = useAuthStore();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginForm) => {
    try {
      await login(data.email, data.password);
      navigate('/');
    } catch {
      // 错误已在 store 中处理
    }
  };

  return (
    <Layout>
      <div className="flex items-center justify-center min-h-[calc(100vh-64px)] px-4">
        <div className="w-full max-w-md">
          {/* 标题 */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              欢迎回来
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              登录到 AI News Hub
            </p>
          </div>

          {/* 登录表单 */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              {/* 错误提示 */}
              {error && (
                <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                  <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
                </div>
              )}

              {/* 邮箱 */}
              <Input
                label="邮箱"
                type="email"
                placeholder="your@email.com"
                error={errors.email?.message}
                disabled={isLoading}
                {...register('email')}
              />

              {/* 密码 */}
              <Input
                label="密码"
                type="password"
                placeholder="请输入密码"
                error={errors.password?.message}
                disabled={isLoading}
                {...register('password')}
              />

              {/* 提交按钮 */}
              <Button
                type="submit"
                fullWidth
                loading={isLoading}
                size="lg"
              >
                登录
              </Button>
            </form>

            {/* 注册链接 */}
            <div className="mt-6 text-center">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                还没有账号？{' '}
                <Link
                  to="/register"
                  className="text-primary-600 hover:text-primary-700 font-medium"
                >
                  立即注册
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
