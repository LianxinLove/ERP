/**
 * 组织架构相关类型定义
 *
 * @description 前后端共享的组织架构类型
 */

/**
 * 部门信息
 */
export interface Department {
  id: number;
  name: string;
  code: string;
  parent_id?: number;
  level: number;
  sort_order: number;
  leader_id?: number;
  description?: string;
  created_at: string;
  updated_at: string;
}

/**
 * 部门树形结构
 */
export interface DepartmentTree extends Department {
  children: DepartmentTree[];
}

/**
 * 创建部门请求
 */
export interface CreateDepartmentRequest {
  name: string;
  code: string;
  parent_id?: number;
  sort_order?: number;
  leader_id?: number;
  description?: string;
}

/**
 * 更新部门请求
 */
export interface UpdateDepartmentRequest {
  name?: string;
  parent_id?: number;
  sort_order?: number;
  leader_id?: number;
  description?: string;
}

/**
 * 职位信息
 */
export interface Position {
  id: number;
  name: string;
  code: string;
  level: number;
  description?: string;
  created_at: string;
  updated_at: string;
}

/**
 * 创建职位请求
 */
export interface CreatePositionRequest {
  name: string;
  code: string;
  level: number;
  description?: string;
}

/**
 * 更新职位请求
 */
export interface UpdatePositionRequest {
  name?: string;
  level?: number;
  description?: string;
}

/**
 * 员工档案信息
 */
export interface EmployeeProfile {
  id: number;
  user_id: number;
  employee_no: string;
  department_id?: number;
  position_id?: number;
  entry_date?: string;
  status: string;
  created_at: string;
  updated_at: string;
}

/**
 * 员工详情
 */
export interface EmployeeDetail extends EmployeeProfile {
  username: string;
  email: string;
  full_name?: string;
  phone?: string;
  department?: Department;
  position?: Position;
}

/**
 * 创建员工档案请求
 */
export interface CreateEmployeeRequest {
  user_id: number;
  employee_no: string;
  department_id?: number;
  position_id?: number;
  entry_date?: string;
  status?: string;
}

/**
 * 更新员工档案请求
 */
export interface UpdateEmployeeRequest {
  department_id?: number;
  position_id?: number;
  entry_date?: string;
  status?: string;
}

/**
 * 员工状态
 */
export type EmployeeStatus = 'active' | 'resigned' | 'probation' | 'leave';
