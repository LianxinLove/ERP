"""
审批流程 API 端点

@description 工作流引擎的 API 接口
"""

from typing import Annotated, List
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_current_superuser, get_db
from app.schemas.workflow import (
    WorkflowDefinitionCreate,
    WorkflowDefinitionUpdate,
    WorkflowDefinitionResponse,
    WorkflowInstanceCreate,
    WorkflowInstanceResponse,
    WorkflowProgressResponse,
    ApproveRequest,
    RejectRequest,
    ReturnRequest,
)
from app.schemas.user import UserResponse
from app.services.workflow import WorkflowEngineService, WorkflowDefinitionService

router = APIRouter()


# ============ 流程定义相关端点 ============

@router.get("/definitions", response_model=List[WorkflowDefinitionResponse])
async def get_workflow_definitions(
    category: Annotated[str | None, Query(description="按分类筛选")] = None,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取流程定义列表"""
    service = WorkflowDefinitionService(db)
    return await service.get_definitions(category=category)


@router.get("/definitions/{definition_id}")
async def get_workflow_definition(
    definition_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取流程定义详情（包含节点和连线）"""
    service = WorkflowDefinitionService(db)
    return await service.get_definition(definition_id)


@router.post("/definitions", response_model=WorkflowDefinitionResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow_definition(
    data: WorkflowDefinitionCreate,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """创建流程定义（需要超级管理员权限）"""
    service = WorkflowDefinitionService(db)
    return await service.create_definition(data)


@router.put("/definitions/{definition_id}", response_model=WorkflowDefinitionResponse)
async def update_workflow_definition(
    definition_id: int,
    data: WorkflowDefinitionUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """更新流程定义（需要超级管理员权限）"""
    service = WorkflowDefinitionService(db)
    return await service.update_definition(definition_id, data)


@router.delete("/definitions/{definition_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow_definition(
    definition_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """删除流程定义（需要超级管理员权限）"""
    service = WorkflowDefinitionService(db)
    await service.delete_definition(definition_id)


# ============ 流程实例相关端点 ============

@router.post("/instances", response_model=WorkflowInstanceResponse, status_code=status.HTTP_201_CREATED)
async def start_workflow_instance(
    workflow_id: Annotated[int, Query(description="流程定义ID")],
    data: WorkflowInstanceCreate,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """启动流程实例"""
    service = WorkflowEngineService(db)
    return await service.start_workflow(workflow_id, data, current_user.id)


@router.get("/instances/{instance_id}", response_model=WorkflowInstanceResponse)
async def get_workflow_instance(
    instance_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取流程实例详情"""
    service = WorkflowEngineService(db)
    return await service.get_instance(instance_id)


@router.get("/instances/{instance_id}/progress", response_model=WorkflowProgressResponse)
async def get_workflow_progress(
    instance_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取流程进度"""
    service = WorkflowEngineService(db)
    return await service.get_workflow_progress(instance_id)


# ============ 审批任务相关端点 ============

@router.get("/tasks/pending")
async def get_my_pending_tasks(
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取我的待办任务"""
    service = WorkflowEngineService(db)
    return await service.get_pending_tasks(current_user.id)


@router.post("/tasks/{task_id}/approve", status_code=status.HTTP_204_NO_CONTENT)
async def approve_task(
    task_id: int,
    data: ApproveRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """审批通过"""
    service = WorkflowEngineService(db)
    await service.approve_task(task_id, current_user.id, data.comment)


@router.post("/tasks/{task_id}/reject", status_code=status.HTTP_204_NO_CONTENT)
async def reject_task(
    task_id: int,
    data: RejectRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """审批拒绝"""
    service = WorkflowEngineService(db)
    await service.reject_task(task_id, current_user.id, data.comment)


@router.post("/tasks/{task_id}/return", status_code=status.HTTP_204_NO_CONTENT)
async def return_task(
    task_id: int,
    data: ReturnRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """退回任务"""
    service = WorkflowEngineService(db)
    await service.return_task(task_id, current_user.id, data.comment, data.return_to_node)
