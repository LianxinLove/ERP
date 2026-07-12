'use client';

/**
 * 权限要求装饰器组件
 *
 * @description 当用户没有权限时显示提示信息
 */

import { type ReactNode } from 'react';
import { AlertCircle } from 'lucide-react';
import { usePermission } from '@/store/permission/PermissionContext';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

/**
 * 权限要求组件属性
 */
interface RequirePermissionProps {
  children: ReactNode;
  /** 权限编码 */
  permission?: string;
  /** 角色编码 */
  role?: string;
  /** 提示标题 */
  title?: string;
  /** 提示描述 */
  description?: string;
}

/**
 * 权限要求组件
 *
 * @example
 * ```tsx
 * <RequirePermission permission="user.create">
 *   <UserCreateForm />
 * </RequirePermission>
 * ```
 */
export function RequirePermission({
  children,
  permission,
  role,
  title = '权限不足',
  description = '您没有权限执行此操作，请联系管理员。',
}: RequirePermissionProps) {
  const { hasPermission, hasRole } = usePermission();

  let hasAccess = true;

  if (permission && !hasPermission(permission)) {
    hasAccess = false;
  }

  if (role && !hasRole(role)) {
    hasAccess = false;
  }

  if (!hasAccess) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>{title}</AlertTitle>
        <AlertDescription>{description}</AlertDescription>
      </Alert>
    );
  }

  return <>{children}</>;
}
