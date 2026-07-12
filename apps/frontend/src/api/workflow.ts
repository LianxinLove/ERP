/**
 * 审批流程API
 *
 * @description 工作流引擎的API调用
 */

import { apiClient } from '@/lib/api/client';
import type {
  WorkflowDefinition,
  WorkflowDefinitionDetail,
  CreateWorkflowDefinitionRequest,
  UpdateWorkflowDefinitionRequest,
  WorkflowInstance,
  CreateWorkflowInstanceRequest,
  WorkflowTask,
  WorkflowProgress,
  ApproveRequest,
  RejectRequest,
  ReturnRequest,
} from '@/types/workflow';

/**
 * 审批流程API类
 */
class WorkflowAPI {
  // ============ 流程定义相关 ============

  /**
   * 获取流程定义列表
   */
  async getDefinitions(category?: string): Promise<WorkflowDefinition[]> {
    const params = category ? { category } : {};
    const response = await apiClient.get('/api/workflows/definitions', { params });
    return response.data;
  }

  /**
   * 获取流程定义详情
   */
  async getDefinition(definitionId: number): Promise<WorkflowDefinitionDetail> {
    const response = await apiClient.get(`/api/workflows/definitions/${definitionId}`);
    return response.data;
  }

  /**
   * 创建流程定义
   */
  async createDefinition(data: CreateWorkflowDefinitionRequest): Promise<WorkflowDefinition> {
    const response = await apiClient.post('/api/workflows/definitions', data);
    return response.data;
  }

  /**
   * 更新流程定义
   */
  async updateDefinition(
    definitionId: number,
    data: UpdateWorkflowDefinitionRequest
  ): Promise<WorkflowDefinition> {
    const response = await apiClient.put(`/api/workflows/definitions/${definitionId}`, data);
    return response.data;
  }

  /**
   * 删除流程定义
   */
  async deleteDefinition(definitionId: number): Promise<void> {
    await apiClient.delete(`/api/workflows/definitions/${definitionId}`);
  }

  // ============ 流程实例相关 ============

  /**
   * 启动流程实例
   */
  async startInstance(workflowId: number, data: CreateWorkflowInstanceRequest): Promise<WorkflowInstance> {
    const response = await apiClient.post('/api/workflows/instances', null, {
      params: { workflow_id: workflowId },
      data,
    });
    return response.data;
  }

  /**
   * 获取流程实例详情
   */
  async getInstance(instanceId: number): Promise<WorkflowInstance> {
    const response = await apiClient.get(`/api/workflows/instances/${instanceId}`);
    return response.data;
  }

  /**
   * 获取流程进度
   */
  async getInstanceProgress(instanceId: number): Promise<WorkflowProgress> {
    const response = await apiClient.get(`/api/workflows/instances/${instanceId}/progress`);
    return response.data;
  }

  // ============ 审批任务相关 ============

  /**
   * 获取我的待办任务
   */
  async getMyPendingTasks(): Promise<WorkflowTask[]> {
    const response = await apiClient.get('/api/workflows/tasks/pending');
    return response.data;
  }

  /**
   * 审批通过
   */
  async approveTask(taskId: number, data: ApproveRequest): Promise<void> {
    await apiClient.post(`/api/workflows/tasks/${taskId}/approve`, data);
  }

  /**
   * 审批拒绝
   */
  async rejectTask(taskId: number, data: RejectRequest): Promise<void> {
    await apiClient.post(`/api/workflows/tasks/${taskId}/reject`, data);
  }

  /**
   * 退回任务
   */
  async returnTask(taskId: number, data: ReturnRequest): Promise<void> {
    await apiClient.post(`/api/workflows/tasks/${taskId}/return`, data);
  }
}

/**
 * 导出审批流程API实例
 */
export const workflowApi = new WorkflowAPI();
