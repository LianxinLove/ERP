import * as React from 'react';
import { Dialog as HeadlessDialog, DialogBackdrop, DialogPanel } from '@headlessui/react';
import { X } from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * Dialog 对话框组件
 *
 * @description 基于 Headless UI 的模态对话框组件
 *
 * @features
 * - 模态对话框
 * - 表单输入支持（无焦点冲突）
 * - 键盘交互支持（ESC 关闭）
 * - 点击遮罩关闭
 * - 深色模式支持
 */

interface DialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  children: React.ReactNode;
}

export function Dialog({ open, onOpenChange, children }: DialogProps) {
  return (
    <HeadlessDialog open={open} onClose={onOpenChange} className="relative z-50">
      {children}
    </HeadlessDialog>
  );
}

export function DialogTrigger({ asChild = false, children }: { asChild?: boolean; children: React.ReactNode }) {
  return <>{children}</>;
}

export function DialogPortal({ children }: { children: React.ReactNode }) {
  return (
    <div className="fixed inset-0 z-50 flex w-screen items-center justify-center p-4">
      {children}
    </div>
  );
}

export function DialogOverlay() {
  return (
    <DialogBackdrop className="fixed inset-0 bg-black/80 transition-opacity data-[closed]:opacity-0 data-[open]:opacity-100" />
  );
}

interface DialogContentProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  onClose?: () => void;
}

export const DialogContent = React.forwardRef<HTMLDivElement, DialogContentProps>(
  ({ className = '', children, onClose, ...props }, ref) => {
    return (
      <DialogPortal>
        <DialogOverlay />
        <DialogPanel
          ref={ref}
          className={cn(
            'relative w-full max-w-lg transform rounded-lg border bg-background p-6 shadow-lg transition-all data-[closed]:translate-y-4 data-[closed]:opacity-0 data-[open]:translate-y-0 data-[open]:opacity-100',
            className
          )}
          {...props}
        >
          {children}
          {onClose && (
            <button
              onClick={onClose}
              className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
            >
              <X className="h-4 w-4" />
              <span className="sr-only">关闭</span>
            </button>
          )}
        </DialogPanel>
      </DialogPortal>
    );
  }
);
DialogContent.displayName = 'DialogContent';

export function DialogHeader({ className = '', children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn('flex flex-col space-y-2 text-center sm:text-left', className)} {...props}>
      {children}
    </div>
  );
}

export function DialogFooter({ className = '', children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn('flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2', className)} {...props}>
      {children}
    </div>
  );
}

export const DialogTitle = React.forwardRef<
  HTMLHeadingElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className = '', children, ...props }, ref) => (
  <h2 ref={ref} className={cn('text-lg font-semibold', className)} {...props}>
    {children}
  </h2>
));
DialogTitle.displayName = 'DialogTitle';

export const DialogDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className = '', children, ...props }, ref) => (
  <p ref={ref} className={cn('text-sm text-muted-foreground', className)} {...props}>
    {children}
  </p>
));
DialogDescription.displayName = 'DialogDescription';
