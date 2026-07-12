/**
 * RBAC（角色权限控制）相关类型定义
 *
 * @description 前后端共享的权限类型
 */

/**
 * 权限信息
 */
export interface Permission {
  id: number;
  name: string;
  code: string;
  module: string;
  description?: string;
  parent_id?: number;
  created_at: string;
  updated_at: string;
}

/**
 * 创建权限请求
 */
export interface PermissionCreate {
  name: string;
  code: string;
  module: string;
  description?: string;
  parent_id?: number;
}

/**
 * 更新权限请求
 */
export interface PermissionUpdate {
  name?: string;
  description?: string;
}

/**
 * 角色信息
 */
export interface Role {
  id: number;
  name: string;
  code: string;
  description?: string;
  is_system: boolean;
  created_at: string;
  updated_at: string;
  permissions?: Permission[];
  permission_count?: number;
}

/**
 * 角色列表项
 */
export interface RoleListItem {
  id: number;
  name: string;
  code: string;
  description?: string;
  is_system: boolean;
  permission_count: number;
}

/**
 * 创建角色请求
 */
export interface RoleCreate {
  name: string;
  code: string;
  description?: string;
  permission_ids?: number[];
}

/**
 * 更新角色请求
 */
export interface RoleUpdate {
  name?: string;
  description?: string;
  permission_ids?: number[];
}

/**
 * 分配角色请求
 */
export interface AssignRoleRequest {
  role_ids: number[];
}

/**
 * 用户基础类型
 */
export interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
}

/**
 * 用户角色响应
 */
export interface UserRoleResponse {
  id: number;
  user_id: number;
  role_id: number;
  role: Role;
}

/**
 * 数据权限范围
 */
export type DataScope = 'all' | 'department' | 'self' | 'custom';

/**
 * 数据权限创建请求
 */
export interface DataPermissionCreate {
  user_id: number;
  resource_type: string;
  scope: DataScope;
  department_ids?: number[];
  user_ids?: number[];
}

/**
 * 数据权限响应
 */
export interface DataPermission {
  id: number;
  user_id: number;
  resource_type: string;
  scope: DataScope;
  department_ids?: number[];
  user_ids?: number[];
  created_at: string;
  updated_at: string;
}

/**
 * 批量分配角色请求
 */
export interface BatchAssignRoleRequest {
  user_ids: number[];
  role_ids: number[];
}

/**
 * 批量分配权限请求
 */
export interface BatchAssignPermissionRequest {
  role_ids: number[];
  permission_ids: number[];
}

/**
 * 权限导入请求
 */
export interface PermissionImportRequest {
  permissions: PermissionCreate[];
  overwrite: boolean;
}

/**
 * 权限导出数据
 */
export interface PermissionExportData {
  name: string;
  code: string;
  module: string;
  description?: string;
  parent_id?: number;
}

/**
 * 用户权限上下文
 */
export interface PermissionContextValue {
  permissions: Set<string>;
  roles: Role[];
  hasPermission: (permission: string) => boolean;
  hasAnyPermission: (permissions: string[]) => boolean;
  hasAllPermissions: (permissions: string[]) => boolean;
  hasRole: (roleCode: string) => boolean;
  refreshPermissions: () => Promise<void>;
}
