/**
 * 注册页面
 */
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button, Input } from '@/components/common';
import { Layout } from '@/layout';
import { useAuthStore } from '@/stores/authStore';

// 表单验证 schema
const registerSchema = z.object({
  email: z.string().min(1, '请输入邮箱').email('请输入有效的邮箱地址'),
  password: z
    .string()
    .min(8, '密码至少8个字符')
    .regex(/[A-Z]/, '密码必须包含大写字母')
    .regex(/[a-z]/, '密码必须包含小写字母')
    .regex(/[0-9]/, '密码必须包含数字'),
  confirmPassword: z.string(),
  nickname: z.string().optional(),
}).refine((data) => data.password === data.confirmPassword, {
  message: '两次密码输入不一致',
  path: ['confirmPassword'],
});

type RegisterForm = z.infer<typeof registerSchema>;

export default function Register() {
  const navigate = useNavigate();
  const { register: registerUser, isLoading, error } = useAuthStore();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterForm) => {
    try {
      await registerUser(data.email, data.password, data.nickname);
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
              创建账号
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              加入 AI News Hub
            </p>
          </div>

          {/* 注册表单 */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
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

              {/* 昵称（可选） */}
              <Input
                label="昵称（可选）"
                type="text"
                placeholder="你的昵称"
                error={errors.nickname?.message}
                disabled={isLoading}
                {...register('nickname')}
              />

              {/* 密码 */}
              <Input
                label="密码"
                type="password"
                placeholder="至少8个字符，包含大小写和数字"
                error={errors.password?.message}
                disabled={isLoading}
                hint="密码至少8个字符，包含大小写字母和数字"
                {...register('password')}
              />

              {/* 确认密码 */}
              <Input
                label="确认密码"
                type="password"
                placeholder="再次输入密码"
                error={errors.confirmPassword?.message}
                disabled={isLoading}
                {...register('confirmPassword')}
              />

              {/* 提交按钮 */}
              <Button
                type="submit"
                fullWidth
                loading={isLoading}
                size="lg"
              >
                注册
              </Button>
            </form>

            {/* 登录链接 */}
            <div className="mt-6 text-center">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                已有账号？{' '}
                <Link
                  to="/login"
                  className="text-primary-600 hover:text-primary-700 font-medium"
                >
                  立即登录
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
