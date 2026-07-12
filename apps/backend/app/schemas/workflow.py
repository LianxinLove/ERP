"""
审批流程相关的 Pydantic 模型

@description 工作流引擎的请求/响应模型
"""

from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field


# ============ 流程定义模型 ============

class WorkflowDefinitionBase(BaseModel):
    """流程定义基础模型"""
    name: str = Field(..., description="流程名称")
    code: str = Field(..., description="流程编码")
    category: Optional[str] = Field(None, description="流程分类")
    description: Optional[str] = Field(None, description="流程描述")
    form_config: Optional[dict] = Field(None, description="表单配置")


class WorkflowDefinitionCreate(WorkflowDefinitionBase):
    """创建流程定义请求模型"""
    nodes: List[dict] = Field(..., description="节点列表")
    edges: List[dict] = Field(..., description="连线列表")


class WorkflowDefinitionUpdate(BaseModel):
    """更新流程定义请求模型"""
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    form_config: Optional[dict] = None
    is_active: Optional[bool] = None
    nodes: Optional[List[dict]] = None
    edges: Optional[List[dict]] = None


class WorkflowDefinitionResponse(WorkflowDefinitionBase):
    """流程定义响应模型"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ============ 流程实例模型 ============

class WorkflowInstanceBase(BaseModel):
    """流程实例基础模型"""
    workflow_id: int = Field(..., description="流程定义ID")
    title: str = Field(..., description="实例标题")
    business_key: Optional[str] = Field(None, description="业务键")
    form_data: Optional[dict] = Field(None, description="表单数据")


class WorkflowInstanceCreate(WorkflowInstanceBase):
    """创建流程实例请求模型"""
    pass


class WorkflowInstanceResponse(WorkflowInstanceBase):
    """流程实例响应模型"""
    id: int
    instance_no: str
    status: str
    current_node: Optional[str]
    initiator_id: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True}


# ============ 审批任务模型 ============

class WorkflowTaskResponse(BaseModel):
    """审批任务响应模型"""
    id: int
    instance_id: int
    instance_no: str
    instance_title: str
    node_key: str
    node_name: str
    assignee_id: Optional[int]
    status: str
    due_date: Optional[datetime]
    created_at: datetime
    completed_at: Optional[datetime]


class TaskListResponse(BaseModel):
    """任务列表响应模型"""
    id: int
    instance_id: int
    instance_title: str
    node_name: str
    status: str
    created_at: datetime


# ============ 审批操作模型 ============

class ApproveRequest(BaseModel):
    """审批通过请求模型"""
    comment: Optional[str] = Field(None, description="审批意见")
    attachments: Optional[List[dict]] = Field(None, description="附件")


class RejectRequest(BaseModel):
    """审批拒绝请求模型"""
    comment: str = Field(..., description="拒绝原因")
    attachments: Optional[List[dict]] = Field(None, description="附件")


class ReturnRequest(BaseModel):
    """退回请求模型"""
    comment: str = Field(..., description="退回原因")
    return_to_node: Optional[str] = Field(None, description="退回到指定节点")


class TransferRequest(BaseModel):
    """转办请求模型"""
    to_user_id: int = Field(..., description="转办给谁")
    comment: Optional[str] = Field(None, description="转办说明")


class AddSignRequest(BaseModel):
    """加签请求模型"""
    user_ids: List[int] = Field(..., min_length=1, description="加签用户列表")
    add_sign_type: str = Field(..., description="加签类型：before-前加签，after-后加签")
    comment: Optional[str] = Field(None, description="加签说明")


# ============ 审批记录模型 ============

class WorkflowApprovalResponse(BaseModel):
    """审批记录响应模型"""
    id: int
    task_id: int
    instance_id: int
    approver_id: int
    approver_name: str
    action: str
    comment: Optional[str]
    attachments: Optional[List[dict]]
    created_at: datetime


# ============ 流程进度模型 ============

class WorkflowProgressNode(BaseModel):
    """流程进度节点模型"""
    node_key: str
    node_name: str
    node_type: str
    status: str
    assignee_id: Optional[int]
    assignee_name: Optional[str]
    created_at: Optional[datetime]
    completed_at: Optional[datetime]


class WorkflowProgressResponse(BaseModel):
    """流程进度响应模型"""
    instance_id: int
    instance_no: str
    title: str
    status: str
    current_node: Optional[str]
    nodes: List[WorkflowProgressNode]
    approvals: List[WorkflowApprovalResponse]
