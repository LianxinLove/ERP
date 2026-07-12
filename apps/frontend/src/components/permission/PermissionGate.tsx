'use client';

/**
 * 权限门控组件
 *
 * @description 根据权限控制子组件的显示
 *
 * @features
 * - 权限检查
 * - 角色检查
 * - 多权限组合
 * - 回退内容
 */

import { type ReactNode } from 'react';
import { usePermission } from '@/store/permission/PermissionContext';

/**
 * 权限门控组件属性
 */
interface PermissionGateProps {
  children: ReactNode;
  /** 权限编码（满足其一即可） */
  permissions?: string | string[];
  /** 角色编码（满足其一即可） */
  roles?: string | string[];
  /** 是否需要全部权限 */
  requireAll?: boolean;
  /** 无权限时显示的内容 */
  fallback?: ReactNode;
  /** 无权限时显示为禁用状态 */
  hide?: boolean;
}

/**
 * 权限门控组件
 *
 * @example
 * ```tsx
 * // 单个权限
 * <PermissionGate permissions="user.create">
 *   <Button>创建用户</Button>
 * </PermissionGate>
 *
 * // 多个权限（满足其一）
 * <PermissionGate permissions={["user.edit", "user.delete"]}>
 *   <Button>编辑或删除</Button>
 * </PermissionGate>
 *
 * // 多个权限（全部需要）
 * <PermissionGate permissions={["user.view", "user.edit"]} requireAll={true}>
 *   <Button>查看和编辑</Button>
 * </PermissionGate>
 *
 * // 角色检查
 * <PermissionGate roles="admin">
 *   <Button>管理员功能</Button>
 * </PermissionGate>
 * ```
 */
export function PermissionGate({
  children,
  permissions,
  roles,
  requireAll = false,
  fallback = null,
  hide = true,
}: PermissionGateProps) {
  const { hasAnyPermission, hasAllPermissions, hasRole } = usePermission();

  let hasAccess = true;

  // 检查权限
  if (permissions) {
    const perms = Array.isArray(permissions) ? permissions : [permissions];

    if (requireAll) {
      hasAccess = hasAllPermissions(perms);
    } else {
      hasAccess = hasAnyPermission(perms);
    }
  }

  // 检查角色
  if (hasAccess && roles) {
    const roleCodes = Array.isArray(roles) ? roles : [roles];
    hasAccess = roleCodes.some(code => hasRole(code));
  }

  // 无权限时的处理
  if (!hasAccess) {
    if (hide) {
      return null;
    }

    if (fallback) {
      return <>{fallback}</>;
    }

    // 默认返回禁用状态的子组件
    return <DisabledWrapper>{children}</DisabledWrapper>;
  }

  return <>{children}</>;
}

/**
 * 禁用状态包装器
 */
function DisabledWrapper({ children }: { children: ReactNode }) {
  return (
    <div className="opacity-50 pointer-events-none" title="您没有权限执行此操作">
      {children}
    </div>
  );
}

/**
 * 权限按钮组件
 */
interface PermissionButtonProps extends PermissionGateProps {
  onClick?: () => void;
  disabled?: boolean;
  className?: string;
}

export function PermissionButton({
  children,
  permissions,
  roles,
  requireAll = false,
  onClick,
  disabled = false,
  className = '',
}: PermissionButtonProps) {
  const { hasAnyPermission, hasAllPermissions, hasRole } = usePermission();

  let hasAccess = true;

  if (permissions) {
    const perms = Array.isArray(permissions) ? permissions : [permissions];
    hasAccess = requireAll ? hasAllPermissions(perms) : hasAnyPermission(perms);
  }

  if (hasAccess && roles) {
    const roleCodes = Array.isArray(roles) ? roles : [roles];
    hasAccess = roleCodes.some(code => hasRole(code));
  }

  return (
    <button
      onClick={onClick}
      disabled={disabled || !hasAccess}
      className={className}
      title={!hasAccess ? '您没有权限执行此操作' : ''}
    >
      {children}
    </button>
  );
}
