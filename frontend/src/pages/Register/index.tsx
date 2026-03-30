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

const registerSchema = z
  .object({
    email: z.string().min(1, '请输入邮箱').email('请输入有效的邮箱地址'),
    password: z
      .string()
      .min(8, '密码至少 8 位')
      .regex(/[A-Z]/, '密码必须包含大写字母')
      .regex(/[a-z]/, '密码必须包含小写字母')
      .regex(/[0-9]/, '密码必须包含数字'),
    confirmPassword: z.string(),
    nickname: z.string().optional(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: '两次输入的密码不一致',
    path: ['confirmPassword'],
  });

type RegisterForm = z.infer<typeof registerSchema>;

const MailIcon = () => (
  <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M4 6h16v12H4z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="m4 8 8 6 8-6" />
  </svg>
);

const UserIcon = () => (
  <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
    <circle cx="12" cy="8" r="3.5" strokeWidth={1.8} />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M5 19a7 7 0 0 1 14 0" />
  </svg>
);

const LockIcon = () => (
  <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M7 10V8a5 5 0 0 1 10 0v2" />
    <rect x="5" y="10" width="14" height="10" rx="3" strokeWidth={1.8} />
  </svg>
);

export default function Register() {
  const navigate = useNavigate();
  const { register: registerUser, isLoading, error } = useAuthStore();
  const [activePasswordField, setActivePasswordField] = useState<'password' | 'confirm' | null>(null);

  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      email: '',
      nickname: '',
      password: '',
      confirmPassword: '',
    },
  });

  const { field: emailField } = useController({ control, name: 'email' });
  const { field: nicknameField } = useController({ control, name: 'nickname' });
  const { field: passwordField } = useController({ control, name: 'password' });
  const { field: confirmPasswordField } = useController({
    control,
    name: 'confirmPassword',
  });

  const onSubmit = async (data: RegisterForm) => {
    try {
      await registerUser(data.email, data.password, data.nickname);
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
            eyebrow="WELCOME"
            title="创建你的账号"
            description="30 秒完成设置，开始建立属于你的 AI 资讯流，并持续收藏你的灵感重点。"
            passwordActive={activePasswordField !== null}
            footer={
              <p className="text-sm text-stone-500">
                已有账号？{' '}
                <Link to="/login" className="font-semibold text-[#ff6b3d] transition hover:text-[#f05626]">
                  立即登录
                </Link>
              </p>
            }
          >
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
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
                label="昵称（可选）"
                type="text"
                placeholder="给自己起个记忆点"
                error={errors.nickname?.message}
                disabled={isLoading}
                leftIcon={<UserIcon />}
                className="h-14 rounded-2xl border-amber-100 bg-white text-base focus:border-[#ff6b3d] focus:ring-[#ff6b3d]/15"
                value={nicknameField.value ?? ''}
                name={nicknameField.name}
                ref={nicknameField.ref}
                onChange={nicknameField.onChange}
                onBlur={nicknameField.onBlur}
              />

              <Input
                label="密码"
                type="password"
                placeholder="至少 8 位，包含大小写字母和数字"
                error={errors.password?.message}
                disabled={isLoading}
                hint="角色会在你输入密码时闭眼，帮助保护输入隐私。"
                leftIcon={<LockIcon />}
                className="h-14 rounded-2xl border-amber-100 bg-white text-base focus:border-[#ff6b3d] focus:ring-[#ff6b3d]/15"
                value={passwordField.value}
                name={passwordField.name}
                ref={passwordField.ref}
                onChange={passwordField.onChange}
                onFocus={() => setActivePasswordField('password')}
                onBlur={() => {
                  setActivePasswordField((current) => (current === 'password' ? null : current));
                  passwordField.onBlur();
                }}
              />

              <Input
                label="确认密码"
                type="password"
                placeholder="再次输入密码"
                error={errors.confirmPassword?.message}
                disabled={isLoading}
                leftIcon={<LockIcon />}
                className="h-14 rounded-2xl border-amber-100 bg-white text-base focus:border-[#ff6b3d] focus:ring-[#ff6b3d]/15"
                value={confirmPasswordField.value}
                name={confirmPasswordField.name}
                ref={confirmPasswordField.ref}
                onChange={confirmPasswordField.onChange}
                onFocus={() => setActivePasswordField('confirm')}
                onBlur={() => {
                  setActivePasswordField((current) => (current === 'confirm' ? null : current));
                  confirmPasswordField.onBlur();
                }}
              />

              <div className="rounded-2xl bg-amber-50/80 px-4 py-3 text-xs leading-5 text-stone-500">
                创建账号即表示你同意服务条款与隐私政策。你的邮箱仅用于账号验证，不会公开展示。
              </div>

              <Button
                type="submit"
                fullWidth
                loading={isLoading}
                size="lg"
                className="rounded-2xl bg-[#ff6b3d] py-3.5 text-base font-semibold shadow-[0_18px_35px_rgba(255,107,61,0.24)] hover:bg-[#f05626] active:bg-[#db4a1d]"
              >
                创建账号
              </Button>
            </form>
          </AuthPageLayout>
        </div>
      </div>
    </Layout>
  );
}
