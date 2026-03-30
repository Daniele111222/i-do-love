import type { ReactNode } from 'react';
import { AuthBall } from '@/components/AuthBall';

export interface AuthPageLayoutProps {
  eyebrow: string;
  title: string;
  description: string;
  children: ReactNode;
  footer?: ReactNode;
  passwordActive?: boolean;
}

export function AuthPageLayout({
  eyebrow,
  title,
  description,
  children,
  footer,
  passwordActive = false,
}: AuthPageLayoutProps) {
  return (
    <div className="relative overflow-hidden rounded-[2rem] border border-amber-100/80 bg-[#fffdf7] shadow-[0_30px_80px_rgba(168,111,51,0.12)]">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(255,243,210,0.9),_transparent_36%),radial-gradient(circle_at_bottom_left,_rgba(255,232,177,0.65),_transparent_32%),radial-gradient(circle_at_right_center,_rgba(255,245,225,0.9),_transparent_40%)]" />

      <div className="relative grid min-h-[720px] lg:grid-cols-[1.05fr_0.95fr]">
        <section className="flex items-center justify-center px-8 py-14 lg:px-14">
          <div className="w-full max-w-[420px]">
            <div className="mx-auto h-[320px] w-full max-w-[320px]">
              <AuthBall
                className="h-full w-full"
                size={1.35}
                trackCursor
                passwordMode="controlled"
                isPasswordActive={passwordActive}
              />
            </div>

            <div className="mt-10 max-w-[320px]">
              <h2 className="text-[2rem] font-semibold leading-[1.1] tracking-[-0.03em] text-stone-800">
                把你的 AI 灵感入口，
                <br />
                安顿下来
              </h2>
              <p className="mt-4 text-sm leading-6 text-stone-500">
                创建账号后即可开始定制资讯节奏、收藏重点内容，并持续追踪你的兴趣主题。
              </p>
            </div>
          </div>
        </section>

        <section className="flex items-center px-6 py-8 lg:px-10 lg:py-10">
          <div className="w-full rounded-[1.75rem] border border-amber-100/80 bg-white/96 p-8 shadow-[0_24px_64px_rgba(150,100,42,0.10)] backdrop-blur-sm lg:p-10">
            <div className="inline-flex rounded-full bg-amber-50 px-3 py-1 text-xs font-semibold tracking-[0.16em] text-amber-700">
              {eyebrow}
            </div>
            <h1 className="mt-5 text-4xl font-semibold tracking-[-0.04em] text-stone-900">
              {title}
            </h1>
            <p className="mt-3 text-sm leading-6 text-stone-500">{description}</p>

            <div className="mt-8">{children}</div>

            {footer ? <div className="mt-6 text-center">{footer}</div> : null}
          </div>
        </section>
      </div>
    </div>
  );
}

export default AuthPageLayout;
