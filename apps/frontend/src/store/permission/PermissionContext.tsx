'use client';

/**
 * 权限上下文
 *
 * @description 提供全局权限检查功能
 *
 * @features
 * - 权限检查
 * - 角色检查
 * - 权限缓存
 * - 自动刷新
 */

import { createContext, useContext, useEffect, useState, useCallback, type ReactNode } from 'react';
import { useQuery } from '@tanstack/react-query';

import type { Role } from '@/types/rbac';
import type { User } from '@/types/auth';

/**
 * 权限上下文值
 */
interface PermissionContextValue {
  permissions: Set<string>;
  roles: Role[];
  isLoading: boolean;
  hasPermission: (permission: string) => boolean;
  hasAnyPermission: (permissions: string[]) => boolean;
  hasAllPermissions: (permissions: string[]) => boolean;
  hasRole: (roleCode: string) => boolean;
  refreshPermissions: () => Promise<void>;
}

const PermissionContext = createContext<PermissionContextValue | undefined>(undefined);

/**
 * 权限提供者属性
 */
interface PermissionProviderProps {
  children: ReactNode;
  user: User | null;
}

/**
 * 权限提供者组件
 */
export function PermissionProvider({ children, user }: PermissionProviderProps) {
  const [permissions, setPermissions] = useState<Set<string>>(new Set());
  const [roles, setRoles] = useState<Role[]>([]);

  // 获取用户权限
  const {
    data: userPermissions,
    isLoading,
    refetch: refreshPermissions,
  } = useQuery({
    queryKey: ['rbac', 'user', 'permissions', user?.id],
    queryFn: async () => {
      if (!user) return { permissions: [], roles: [] };

      const response = await fetch('/api/rbac/users/me/permissions', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('获取权限失败');
      }

      const data = await response.json();
      return data;
    },
    enabled: !!user,
    staleTime: 10 * 60 * 1000, // 10分钟
  });

  // 更新权限和角色
  useEffect(() => {
    if (userPermissions) {
      setPermissions(new Set(userPermissions.permissions || []));
      // TODO: 获取用户角色
    } else {
      setPermissions(new Set());
      setRoles([]);
    }
  }, [userPermissions]);

  /**
   * 检查是否拥有指定权限
   */
  const hasPermission = useCallback(
    (permission: string) => {
      return permissions.has(permission);
    },
    [permissions]
  );

  /**
   * 检查是否拥有任意一个权限
   */
  const hasAnyPermission = useCallback(
    (perms: string[]) => {
      return perms.some(perm => permissions.has(perm));
    },
    [permissions]
  );

  /**
   * 检查是否拥有所有权限
   */
  const hasAllPermissions = useCallback(
    (perms: string[]) => {
      return perms.every(perm => permissions.has(perm));
    },
    [permissions]
  );

  /**
   * 检查是否拥有指定角色
   */
  const hasRole = useCallback(
    (roleCode: string) => {
      if (user?.is_superuser) return true;
      return roles.some(role => role.code === roleCode);
    },
    [roles, user]
  );

  const value: PermissionContextValue = {
    permissions,
    roles,
    isLoading,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    hasRole,
    refreshPermissions: async () => {
      await refreshPermissions();
    },
  };

  return <PermissionContext.Provider value={value}>{children}</PermissionContext.Provider>;
}

/**
 * 使用权限上下文
 *
 * @throws {Error} 如果不在PermissionProvider内使用
 * @returns 权限上下文值
 */
export function usePermission() {
  const context = useContext(PermissionContext);
  if (!context) {
    throw new Error('usePermission 必须在 PermissionProvider 内使用');
  }
  return context;
}
