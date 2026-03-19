/**
 * Card 卡片组件
 * 通用的内容容器
 */
import { HTMLAttributes, ReactNode } from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  /** 卡片标题 */
  title?: string;
  /** 副标题 */
  subtitle?: string;
  /** 卡片头部操作区域 */
  headerAction?: ReactNode;
  /** 卡片底部操作区域 */
  footer?: ReactNode;
  /** 是否悬浮效果 */
  hoverable?: boolean;
  /** 子元素 */
  children: ReactNode;
}

interface CardImageProps extends HTMLAttributes<HTMLDivElement> {
  /** 图片地址 */
  src: string;
  /** 图片替代文字 */
  alt: string;
  /** 图片高度 */
  height?: 'sm' | 'md' | 'lg';
}

interface CardContentProps extends HTMLAttributes<HTMLDivElement> {
  /** 子元素 */
  children: ReactNode;
}

/**
 * Card 组件
 *
 * @example
 * ```tsx
 * <Card title="文章标题" subtitle="2024-01-01" hoverable>
 *   <Card.Content><p>内容...</p></Card.Content>
 * </Card>
 * ```
 */
export function Card({
  title,
  subtitle,
  headerAction,
  footer,
  hoverable = false,
  children,
  className,
  ...props
}: CardProps) {
  return (
    <div
      className={twMerge(
        clsx(
          'bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700',
          'overflow-hidden',
          hoverable && 'transition-shadow duration-200 hover:shadow-md',
          className
        )
      )}
      {...props}
    >
      {/* 头部 */}
      {(title || subtitle || headerAction) && (
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <div>
            {title && (
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{title}</h3>
            )}
            {subtitle && (
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">{subtitle}</p>
            )}
          </div>
          {headerAction && <div>{headerAction}</div>}
        </div>
      )}

      {/* 内容 */}
      <div className="px-6 py-4">{children}</div>

      {/* 底部 */}
      {footer && (
        <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
          {footer}
        </div>
      )}
    </div>
  );
}

/**
 * Card.Image 子组件
 */
Card.Image = function CardImage({ src, alt, height = 'md', className, ...props }: CardImageProps) {
  const heightStyles = { sm: 'h-32', md: 'h-48', lg: 'h-64' };
  return (
    <div className={twMerge(clsx('w-full overflow-hidden', heightStyles[height], className))} {...props}>
      <img src={src} alt={alt} className="w-full h-full object-cover" />
    </div>
  );
};

/**
 * Card.Content 子组件
 */
Card.Content = function CardContent({ children, className, ...props }: CardContentProps) {
  return (
    <div className={clsx('', className)} {...props}>
      {children}
    </div>
  );
};

export default Card;
