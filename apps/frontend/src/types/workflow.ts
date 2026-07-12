/**
 * 审批流程相关类型定义
 *
 * @description 前后端共享的工作流类型
 */

/**
 * 节点类型
 */
export type NodeType = 'start' | 'end' | 'approval' | 'condition' | 'parallel';

/**
 * 任务状态
 */
export type TaskStatus = 'pending' | 'approved' | 'rejected' | 'returned' | 'cancelled';

/**
 * 实例状态
 */
export type InstanceStatus = 'running' | 'completed' | 'rejected' | 'cancelled';

/**
 * 审批操作类型
 */
export type ApprovalAction = 'approve' | 'reject' | 'return';

/**
 * 流程节点
 */
export interface WorkflowNode {
  id?: number;
  node_key: string;
  node_type: NodeType;
  name: string;
  config?: Record<string, any>;
  sort_order?: number;
}

/**
 * 流程连线
 */
export interface WorkflowEdge {
  id?: number;
  source_node: string;
  target_node: string;
  condition?: Record<string, any>;
}

/**
 * 流程定义
 */
export interface WorkflowDefinition {
  id: number;
  name: string;
  code: string;
  category?: string;
  description?: string;
  form_config?: Record<string, any>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * 流程定义详情
 */
export interface WorkflowDefinitionDetail extends WorkflowDefinition {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
}

/**
 * 创建流程定义请求
 */
export interface CreateWorkflowDefinitionRequest {
  name: string;
  code: string;
  category?: string;
  description?: string;
  form_config?: Record<string, any>;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
}

/**
 * 更新流程定义请求
 */
export interface UpdateWorkflowDefinitionRequest {
  name?: string;
  category?: string;
  description?: string;
  form_config?: Record<string, any>;
  is_active?: boolean;
  nodes?: WorkflowNode[];
  edges?: WorkflowEdge[];
}

/**
 * 流程实例
 */
export interface WorkflowInstance {
  id: number;
  workflow_id: number;
  instance_no: string;
  title: string;
  status: InstanceStatus;
  current_node?: string;
  business_key?: string;
  form_data?: Record<string, any>;
  initiator_id: number;
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

/**
 * 创建流程实例请求
 */
export interface CreateWorkflowInstanceRequest {
  workflow_id: number;
  title: string;
  business_key?: string;
  form_data?: Record<string, any>;
}

/**
 * 审批任务
 */
export interface WorkflowTask {
  id: number;
  instance_id: number;
  instance_title: string;
  node_key: string;
  node_name: string;
  assignee_id?: number;
  status: TaskStatus;
  due_date?: string;
  created_at: string;
  completed_at?: string;
}

/**
 * 审批记录
 */
export interface WorkflowApproval {
  id: number;
  task_id: number;
  instance_id: number;
  approver_id: number;
  approver_name: string;
  action: ApprovalAction;
  comment?: string;
  attachments?: any[];
  created_at: string;
}

/**
 * 流程进度节点
 */
export interface ProgressNode {
  node_key: string;
  node_name: string;
  node_type: NodeType;
  status: TaskStatus;
  assignee_id?: number;
  assignee_name?: string;
  created_at?: string;
  completed_at?: string;
}

/**
 * 流程进度
 */
export interface WorkflowProgress {
  instance_id: number;
  instance_no: string;
  title: string;
  status: InstanceStatus;
  current_node?: string;
  nodes: ProgressNode[];
  approvals: WorkflowApproval[];
}

/**
 * 审批通过请求
 */
export interface ApproveRequest {
  comment?: string;
  attachments?: any[];
}

/**
 * 审批拒绝请求
 */
export interface RejectRequest {
  comment: string;
  attachments?: any[];
}

/**
 * 退回请求
 */
export interface ReturnRequest {
  comment: string;
  return_to_node?: string;
}
