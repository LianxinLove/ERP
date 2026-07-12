'use client';

/**
 * Toast 提供者组件
 *
 * @description 提供全局 Toast 通知功能
 *
 * @features
 * - 支持多种通知类型
 * - 自定义位置和样式
 * - 自动消失和手动关闭
 */

import { Toaster as SonnerToaster } from 'sonner';

/**
 * Toast 提供者组件
 *
 * @returns Toast 组件容器
 */
export function ToastProvider() {
  return (
    <SonnerToaster
      position="top-right"
      expand={false}
      richColors
      closeButton
      duration={3000}
      toastOptions={{
        classNames: {
          toast: 'toast',
          description: 'toast-description',
          actionButton: 'toast-action-button',
          cancelButton: 'toast-cancel-button',
          closeButton: 'toast-close-button',
        },
      }}
    />
  );
}
