/**
 * 组织架构API
 *
 * @description 部门、职位、员工档案的API调用
 */

import { apiClient } from '@/lib/api/client';
import type {
  Department,
  DepartmentTree,
  CreateDepartmentRequest,
  UpdateDepartmentRequest,
  Position,
  CreatePositionRequest,
  UpdatePositionRequest,
  EmployeeDetail,
  CreateEmployeeRequest,
  UpdateEmployeeRequest,
} from '@/types/organization';

/**
 * 组织架构API类
 */
class OrganizationAPI {
  // ============ 部门相关 ============

  /**
   * 获取部门列表
   */
  async getDepartments(asTree = false): Promise<Department[]> {
    const response = await apiClient.get('/api/org/departments', {
      params: { as_tree: asTree },
    });
    return response.data;
  }

  /**
   * 获取部门详情
   */
  async getDepartment(departmentId: number): Promise<Department> {
    const response = await apiClient.get(`/api/org/departments/${departmentId}`);
    return response.data;
  }

  /**
   * 创建部门
   */
  async createDepartment(data: CreateDepartmentRequest): Promise<Department> {
    const response = await apiClient.post('/api/org/departments', data);
    return response.data;
  }

  /**
   * 更新部门
   */
  async updateDepartment(departmentId: number, data: UpdateDepartmentRequest): Promise<Department> {
    const response = await apiClient.put(`/api/org/departments/${departmentId}`, data);
    return response.data;
  }

  /**
   * 删除部门
   */
  async deleteDepartment(departmentId: number): Promise<void> {
    await apiClient.delete(`/api/org/departments/${departmentId}`);
  }

  // ============ 职位相关 ============

  /**
   * 获取职位列表
   */
  async getPositions(): Promise<Position[]> {
    const response = await apiClient.get('/api/org/positions');
    return response.data;
  }

  /**
   * 获取职位详情
   */
  async getPosition(positionId: number): Promise<Position> {
    const response = await apiClient.get(`/api/org/positions/${positionId}`);
    return response.data;
  }

  /**
   * 创建职位
   */
  async createPosition(data: CreatePositionRequest): Promise<Position> {
    const response = await apiClient.post('/api/org/positions', data);
    return response.data;
  }

  /**
   * 更新职位
   */
  async updatePosition(positionId: number, data: UpdatePositionRequest): Promise<Position> {
    const response = await apiClient.put(`/api/org/positions/${positionId}`, data);
    return response.data;
  }

  /**
   * 删除职位
   */
  async deletePosition(positionId: number): Promise<void> {
    await apiClient.delete(`/api/org/positions/${positionId}`);
  }

  // ============ 员工档案相关 ============

  /**
   * 获取员工列表
   */
  async getEmployees(params?: {
    department_id?: number;
    position_id?: number;
    status?: string;
  }): Promise<EmployeeDetail[]> {
    const response = await apiClient.get('/api/org/employees', { params });
    return response.data;
  }

  /**
   * 获取员工详情
   */
  async getEmployee(employeeId: number): Promise<EmployeeDetail> {
    const response = await apiClient.get(`/api/org/employees/${employeeId}`);
    return response.data;
  }

  /**
   * 创建员工档案
   */
  async createEmployee(data: CreateEmployeeRequest): Promise<EmployeeDetail> {
    const response = await apiClient.post('/api/org/employees', data);
    return response.data;
  }

  /**
   * 更新员工档案
   */
  async updateEmployee(employeeId: number, data: UpdateEmployeeRequest): Promise<EmployeeDetail> {
    const response = await apiClient.put(`/api/org/employees/${employeeId}`, data);
    return response.data;
  }
}

/**
 * 导出组织架构API实例
 */
export const organizationApi = new OrganizationAPI();
