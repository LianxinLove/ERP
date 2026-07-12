import { cn } from '@/lib/utils';

/**
 * Skeleton 骨架屏组件
 *
 * @description 用于在内容加载时显示占位符
 *
 * @features
 * - 动画效果
 * - 可配置尺寸
 * - 用于加载状态指示
 */
function Skeleton({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn('animate-pulse rounded-md bg-muted', className)}
      {...props}
    />
  );
}

export { Skeleton };
