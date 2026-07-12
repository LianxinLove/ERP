"""
组织架构 API 端点

@description 部门、职位、员工档案的 API 接口
"""

from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_current_superuser, get_db
from app.core.permissions import require_permission
from app.schemas.organization import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
    DepartmentTree,
    PositionCreate,
    PositionUpdate,
    PositionResponse,
    EmployeeProfileCreate,
    EmployeeProfileUpdate,
    EmployeeProfileResponse,
    EmployeeDetailResponse,
)
from app.schemas.user import UserResponse
from app.services.organization import (
    DepartmentService,
    PositionService,
    EmployeeService,
)

router = APIRouter()


# ============ 部门相关端点 ============

@router.get("/departments", response_model=List[DepartmentResponse])
async def get_departments(
    as_tree: Annotated[bool, Query(description="是否返回树形结构")] = False,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    获取部门列表

    支持树形结构返回
    """
    service = DepartmentService(db)
    return await service.get_departments(as_tree=as_tree)


@router.get("/departments/{department_id}", response_model=DepartmentResponse)
async def get_department(
    department_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取部门详情"""
    service = DepartmentService(db)
    return await service.get_department(department_id)


@router.post("/departments", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(
    data: DepartmentCreate,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """创建部门（需要超级管理员权限）"""
    service = DepartmentService(db)
    return await service.create_department(data)


@router.put("/departments/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: int,
    data: DepartmentUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """更新部门（需要超级管理员权限）"""
    service = DepartmentService(db)
    return await service.update_department(department_id, data)


@router.delete("/departments/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    department_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """删除部门（需要超级管理员权限）"""
    service = DepartmentService(db)
    await service.delete_department(department_id)


# ============ 职位相关端点 ============

@router.get("/positions", response_model=List[PositionResponse])
async def get_positions(
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取职位列表"""
    service = PositionService(db)
    return await service.get_positions()


@router.get("/positions/{position_id}", response_model=PositionResponse)
async def get_position(
    position_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取职位详情"""
    service = PositionService(db)
    return await service.get_position(position_id)


@router.post("/positions", response_model=PositionResponse, status_code=status.HTTP_201_CREATED)
async def create_position(
    data: PositionCreate,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """创建职位（需要超级管理员权限）"""
    service = PositionService(db)
    return await service.create_position(data)


@router.put("/positions/{position_id}", response_model=PositionResponse)
async def update_position(
    position_id: int,
    data: PositionUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """更新职位（需要超级管理员权限）"""
    service = PositionService(db)
    return await service.update_position(position_id, data)


@router.delete("/positions/{position_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_position(
    position_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """删除职位（需要超级管理员权限）"""
    service = PositionService(db)
    await service.delete_position(position_id)


# ============ 员工档案相关端点 ============

@router.get("/employees", response_model=List[EmployeeDetailResponse])
async def get_employees(
    department_id: Annotated[Optional[int], Query(description="按部门筛选")] = None,
    position_id: Annotated[Optional[int], Query(description="按职位筛选")] = None,
    status_filter: Annotated[Optional[str], Query(description="按状态筛选", alias="status")] = None,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    获取员工列表

    支持按部门、职位、状态筛选
    """
    service = EmployeeService(db)
    return await service.get_employees(
        department_id=department_id,
        position_id=position_id,
        status=status_filter,
    )


@router.get("/employees/{employee_id}", response_model=EmployeeDetailResponse)
async def get_employee_profile(
    employee_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取员工档案详情"""
    service = EmployeeService(db)
    return await service.get_employee_profile(employee_id)


@router.post("/employees", response_model=EmployeeDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_employee_profile(
    data: EmployeeProfileCreate,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """创建员工档案（需要超级管理员权限）"""
    service = EmployeeService(db)
    return await service.create_employee_profile(data)


@router.put("/employees/{employee_id}", response_model=EmployeeDetailResponse)
async def update_employee_profile(
    employee_id: int,
    data: EmployeeProfileUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """更新员工档案（需要超级管理员权限）"""
    service = EmployeeService(db)
    return await service.update_employee_profile(employee_id, data)
