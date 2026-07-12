"""
数据权限管理 API 端点

@description 数据权限管理的 API 接口
"""

from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_current_superuser, get_db
from app.schemas.data_permission import (
    DataPermissionCreate,
    DataPermissionUpdate,
    DataPermissionResponse,
    DataScopeResponse,
)
from app.schemas.user import UserResponse
from app.services.data_permission import DataPermissionService

router = APIRouter()


# ============ 数据权限管理端点 ============

@router.get("/data-permissions", response_model=List[DataPermissionResponse])
async def get_data_permissions(
    resource_type: Annotated[Optional[str], Query(description="资源类型筛选")] = None,
    user_id: Annotated[Optional[int], Query(description="用户ID筛选")] = None,
    role_id: Annotated[Optional[int], Query(description="角色ID筛选")] = None,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    获取数据权限列表（需要超级管理员权限）

    支持按资源类型、用户、角色筛选
    """
    service = DataPermissionService(db)
    return await service.get_permissions(
        resource_type=resource_type,
        user_id=user_id,
        role_id=role_id,
    )


@router.get("/data-permissions/{permission_id}", response_model=DataPermissionResponse)
async def get_data_permission(
    permission_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取数据权限详情（需要超级管理员权限）"""
    service = DataPermissionService(db)
    return await service.get_permission(permission_id)


@router.post("/data-permissions", response_model=DataPermissionResponse, status_code=status.HTTP_201_CREATED)
async def create_data_permission(
    data: DataPermissionCreate,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    创建数据权限（需要超级管理员权限）

    可以为特定用户或角色设置数据访问范围
    """
    service = DataPermissionService(db)
    return await service.create_permission(data)


@router.put("/data-permissions/{permission_id}", response_model=DataPermissionResponse)
async def update_data_permission(
    permission_id: int,
    data: DataPermissionUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """更新数据权限（需要超级管理员权限）"""
    service = DataPermissionService(db)
    return await service.update_permission(permission_id, data)


@router.delete("/data-permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_data_permission(
    permission_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """删除数据权限（需要超级管理员权限）"""
    service = DataPermissionService(db)
    await service.delete_permission(permission_id)


# ============ 数据范围查询端点 ============

@router.get("/my-data-scope", response_model=List[DataScopeResponse])
async def get_my_data_scopes(
    resource_types: Annotated[str, Query(description="资源类型列表，逗号分隔")] = "",
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    获取当前用户的数据范围

    返回用户对指定资源的访问范围
    """
    service = DataPermissionService(db)

    if resource_types:
        types_list = resource_types.split(",")
    else:
        # 默认查询所有资源类型
        types_list = [
            "sales_order",
            "purchase_request",
            "purchase_order",
            "customer",
            "supplier",
            "product",
            "warehouse",
        ]

    scope_descriptions = {
        "all": "全部数据",
        "dept": "本部门及子部门数据",
        "department": "仅本部门数据",
        "self": "仅自己创建的数据",
        "custom": "自定义范围",
    }

    results = []
    for resource_type in types_list:
        scope = await service.get_user_effective_scope(current_user.id, resource_type.strip())
        results.append(
            DataScopeResponse(
                resource_type=resource_type.strip(),
                scope=scope,
                scope_description=scope_descriptions.get(scope, "未知范围"),
            )
        )

    return results
