import * as React from 'react';
import { cn } from '@/lib/utils';

/**
 * Textarea 文本域组件
 *
 * @description 多行文本输入组件
 *
 * @features
 * - 自动调整大小
 * - 支持所有标准textarea属性
 * - 统一样式
 *
 * @example
 * ```tsx
 * <Textarea placeholder="请输入审批意见..." rows={4} />
 * ```
 */
export interface TextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {}

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, ...props }, ref) => {
    return (
      <textarea
        className={cn(
          'flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
          className
        )}
        ref={ref}
        {...props}
      />
    );
  }
);
Textarea.displayName = 'Textarea';

export { Textarea };
