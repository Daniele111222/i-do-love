/* eslint-disable react-hooks/refs */
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useController, useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button, Input } from '@/components/common';
import { AuthPageLayout } from '@/components/AuthPageLayout';
import { Layout } from '@/layout';
import { useAuthStore } from '@/stores/authStore';

const loginSchema = z.object({
  email: z.string().email('请输入有效的邮箱地址'),
  password: z.string().min(1, '请输入密码'),
});

type LoginForm = z.infer<typeof loginSchema>;

const MailIcon = () => (
  <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M4 6h16v12H4z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="m4 8 8 6 8-6" />
  </svg>
);

const LockIcon = () => (
  <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M7 10V8a5 5 0 0 1 10 0v2" />
    <rect x="5" y="10" width="14" height="10" rx="3" strokeWidth={1.8} />
  </svg>
);

export default function Login() {
  const navigate = useNavigate();
  const { login, isLoading, error } = useAuthStore();
  const [isPasswordActive, setIsPasswordActive] = useState(false);

  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const { field: emailField } = useController({
    control,
    name: 'email',
  });

  const { field: passwordField } = useController({
    control,
    name: 'password',
  });

  const onSubmit = async (data: LoginForm) => {
    try {
      await login(data.email, data.password);
      navigate('/');
    } catch {
      // Error state is handled by the auth store.
    }
  };

  return (
    <Layout>
      <div className="min-h-[calc(100vh-64px)] bg-[#fff7df] px-4 py-8 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <AuthPageLayout
            eyebrow="WELCOME BACK"
            title="欢迎回来"
            description="登录后即可继续查看你的 AI 资讯流、收藏清单与个性化追踪内容。"
            passwordActive={isPasswordActive}
            footer={
              <p className="text-sm text-stone-500">
                还没有账号？{' '}
                <Link to="/register" className="font-semibold text-[#ff6b3d] transition hover:text-[#f05626]">
                  立即注册
                </Link>
              </p>
            }
          >
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
              {error ? (
                <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
                  {error}
                </div>
              ) : null}

              <Input
                label="邮箱"
                type="email"
                placeholder="hello@yourmail.com"
                error={errors.email?.message}
                disabled={isLoading}
                leftIcon={<MailIcon />}
                className="h-14 rounded-2xl border-amber-100 bg-white text-base focus:border-[#ff6b3d] focus:ring-[#ff6b3d]/15"
                value={emailField.value}
                name={emailField.name}
                ref={emailField.ref}
                onChange={emailField.onChange}
                onBlur={emailField.onBlur}
              />

              <Input
                label="密码"
                type="password"
                placeholder="请输入密码"
                error={errors.password?.message}
                disabled={isLoading}
                leftIcon={<LockIcon />}
                className="h-14 rounded-2xl border-amber-100 bg-white text-base focus:border-[#ff6b3d] focus:ring-[#ff6b3d]/15"
                value={passwordField.value}
                name={passwordField.name}
                ref={passwordField.ref}
                onChange={passwordField.onChange}
                onFocus={() => setIsPasswordActive(true)}
                onBlur={() => {
                  setIsPasswordActive(false);
                  passwordField.onBlur();
                }}
              />

              <p className="text-xs leading-5 text-stone-500">
                输入密码时，角色会暂时闭眼，帮助你更安心地完成登录。
              </p>

              <Button
                type="submit"
                fullWidth
                loading={isLoading}
                size="lg"
                className="rounded-2xl bg-[#ff6b3d] py-3.5 text-base font-semibold shadow-[0_18px_35px_rgba(255,107,61,0.24)] hover:bg-[#f05626] active:bg-[#db4a1d]"
              >
                登录
              </Button>
            </form>
          </AuthPageLayout>
        </div>
      </div>
    </Layout>
  );
}
