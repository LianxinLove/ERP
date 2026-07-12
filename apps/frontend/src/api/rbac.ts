/**
 * RBAC API
 * @description 角色权限管理相关的 API 调用
 */

import { apiClient } from '@/lib/api/client';
import type {
  Permission,
  PermissionCreate,
  PermissionUpdate,
  Role,
  RoleCreate,
  RoleUpdate,
  RoleListItem,
  AssignRoleRequest,
  UserRoleResponse,
  DataPermission,
  DataPermissionCreate,
  DataScope,
  BatchAssignRoleRequest,
  BatchAssignPermissionRequest,
  PermissionImportRequest,
  PermissionExportData,
} from '@/types/rbac';

/**
 * 权限 API 类
 */
class PermissionAPI {
  /**
   * 获取所有权限
   */
  async getPermissions(module?: string): Promise<Permission[]> {
    const params = module ? { module } : {};
    const response = await apiClient.get<Permission[]>('/api/rbac/permissions', { params });
    return response.data;
  }

  /**
   * 获取权限详情
   */
  async getPermission(id: number): Promise<Permission> {
    const response = await apiClient.get<Permission>(`/api/rbac/permissions/${id}`);
    return response.data;
  }

  /**
   * 创建权限
   */
  async createPermission(data: PermissionCreate): Promise<Permission> {
    const response = await apiClient.post<Permission>('/api/rbac/permissions', data);
    return response.data;
  }

  /**
   * 更新权限
   */
  async updatePermission(id: number, data: PermissionUpdate): Promise<Permission> {
    const response = await apiClient.put<Permission>(`/api/rbac/permissions/${id}`, data);
    return response.data;
  }

  /**
   * 删除权限（软删除）
   */
  async deletePermission(id: number): Promise<void> {
    await apiClient.delete(`/api/rbac/permissions/${id}`);
  }

  /**
   * 导入权限
   */
  async importPermissions(data: PermissionImportRequest): Promise<{
    created: number;
    updated: number;
    skipped: number;
    errors: Array<{ code: string; error: string }>;
  }> {
    const response = await apiClient.post('/api/rbac/permissions/import', data);
    return response.data;
  }

  /**
   * 导出权限
   */
  async exportPermissions(): Promise<PermissionExportData[]> {
    const response = await apiClient.get<PermissionExportData[]>('/api/rbac/permissions/export');
    return response.data;
  }
}

/**
 * 角色 API 类
 */
class RoleAPI {
  /**
   * 获取所有角色
   */
  async getRoles(): Promise<RoleListItem[]> {
    const response = await apiClient.get<RoleListItem[]>('/api/rbac/roles');
    return response.data;
  }

  /**
   * 获取角色详情
   */
  async getRole(id: number): Promise<Role> {
    const response = await apiClient.get<Role>(`/api/rbac/roles/${id}`);
    return response.data;
  }

  /**
   * 创建角色
   */
  async createRole(data: RoleCreate): Promise<Role> {
    const response = await apiClient.post<Role>('/api/rbac/roles', data);
    return response.data;
  }

  /**
   * 更新角色
   */
  async updateRole(id: number, data: RoleUpdate): Promise<Role> {
    const response = await apiClient.put<Role>(`/api/rbac/roles/${id}`, data);
    return response.data;
  }

  /**
   * 删除角色
   */
  async deleteRole(id: number): Promise<void> {
    await apiClient.delete(`/api/rbac/roles/${id}`);
  }

  /**
   * 为角色分配权限
   */
  async assignPermissions(roleId: number, permissionIds: number[]): Promise<void> {
    await apiClient.post(`/api/rbac/roles/${roleId}/permissions`, { permission_ids: permissionIds });
  }

  /**
   * 批量为角色分配权限
   */
  async batchAssignPermissions(data: BatchAssignPermissionRequest): Promise<number> {
    const response = await apiClient.post<{ count: number }>('/api/rbac/roles/batch-permissions', data);
    return response.data.count;
  }
}

/**
 * 用户角色 API 类
 */
class UserRoleAPI {
  /**
   * 为用户分配角色
   */
  async assignUserRoles(userId: number, data: AssignRoleRequest): Promise<void> {
    await apiClient.post(`/api/rbac/users/${userId}/roles`, data);
  }

  /**
   * 获取用户的角色列表
   */
  async getUserRoles(userId: number): Promise<Role[]> {
    const response = await apiClient.get<Role[]>(`/api/rbac/users/${userId}/roles`);
    return response.data;
  }

  /**
   * 获取用户的所有权限编码
   */
  async getUserPermissions(userId: number): Promise<Set<string>> {
    const response = await apiClient.get<{ permissions: string[] }>(`/api/rbac/users/${userId}/permissions`);
    return new Set(response.data.permissions);
  }

  /**
   * 批量为用户分配角色
   */
  async batchAssignRoles(data: BatchAssignRoleRequest): Promise<number> {
    const response = await apiClient.post<{ count: number }>('/api/rbac/users/batch-roles', data);
    return response.data.count;
  }

  /**
   * 移除用户角色
   */
  async removeUserRole(userId: number, roleId: number): Promise<void> {
    await apiClient.delete(`/api/rbac/users/${userId}/roles/${roleId}`);
  }
}

/**
 * 数据权限 API 类
 */
class DataPermissionAPI {
  /**
   * 获取用户的数据范围
   */
  async getUserDataScope(userId: number, resourceType: string): Promise<DataScope> {
    const response = await apiClient.get<{ scope: DataScope }>(
      `/api/data-permissions/users/${userId}/scope`,
      { params: { resource_type: resourceType } }
    );
    return response.data.scope;
  }

  /**
   * 创建数据权限
   */
  async createPermission(data: DataPermissionCreate): Promise<DataPermission> {
    const response = await apiClient.post<DataPermission>('/api/data-permissions', data);
    return response.data;
  }

  /**
   * 获取用户的数据权限列表
   */
  async getUserPermissions(userId: number): Promise<DataPermission[]> {
    const response = await apiClient.get<DataPermission[]>(`/api/data-permissions/users/${userId}`);
    return response.data;
  }

  /**
   * 更新数据权限
   */
  async updatePermission(id: number, data: Partial<DataPermissionCreate>): Promise<DataPermission> {
    const response = await apiClient.put<DataPermission>(`/api/data-permissions/${id}`, data);
    return response.data;
  }

  /**
   * 删除数据权限
   */
  async deletePermission(id: number): Promise<void> {
    await apiClient.delete(`/api/data-permissions/${id}`);
  }

  /**
   * 根据资源类型获取数据权限
   */
  async getByResourceType(resourceType: string): Promise<DataPermission[]> {
    const response = await apiClient.get<DataPermission[]>(`/api/data-permissions/resource/${resourceType}`);
    return response.data;
  }
}

/**
 * 导出 API 实例
 */
export const permissionApi = new PermissionAPI();
export const roleApi = new RoleAPI();
export const userRoleApi = new UserRoleAPI();
export const dataPermissionApi = new DataPermissionAPI();

// 统一导出
export const rbacApi = {
  permission: permissionApi,
  role: roleApi,
  userRole: userRoleApi,
  dataPermission: dataPermissionApi,
};
