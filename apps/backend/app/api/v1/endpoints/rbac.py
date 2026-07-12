"""
RBAC API 端点

@description 角色和权限管理的 API 接口
"""

from datetime import datetime, timezone
from typing import Annotated, List
from fastapi import APIRouter, Depends, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_current_superuser, get_db
from app.core.permissions import clear_permission_cache
from app.schemas.rbac import (
    PermissionCreate,
    PermissionUpdate,
    PermissionResponse,
    PermissionImportRequest,
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    RoleListResponse,
    AssignRoleRequest,
    BatchAssignRoleRequest,
    BatchAssignDifferentRolesRequest,
    BatchAssignPermissionRequest,
)
from app.schemas.user import UserResponse
from app.services.rbac import PermissionService, RoleService, UserRoleService

router = APIRouter()


# ============ 权限相关端点 ============

@router.get("/permissions", response_model=List[PermissionResponse])
async def get_permissions(
    module: Annotated[str | None, Query(description="按模块筛选")] = None,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    获取权限列表

    支持按模块筛选
    """
    service = PermissionService(db)
    return await service.get_permissions(module=module)


@router.get("/permissions/{permission_id}", response_model=PermissionResponse)
async def get_permission(
    permission_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取权限详情（需要超级管理员权限）"""
    service = PermissionService(db)
    return await service.get_permission(permission_id)


@router.post("/permissions", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
async def create_permission(
    data: PermissionCreate,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """创建权限（需要超级管理员权限）"""
    service = PermissionService(db)
    return await service.create_permission(data)


@router.put("/permissions/{permission_id}", response_model=PermissionResponse)
async def update_permission(
    permission_id: int,
    data: PermissionUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """更新权限（需要超级管理员权限）"""
    service = PermissionService(db)
    return await service.update_permission(permission_id, data)


@router.delete("/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(
    permission_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """删除权限（需要超级管理员权限）"""
    service = PermissionService(db)
    await service.delete_permission(permission_id)


@router.get("/permissions/export")
async def export_permissions(
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    导出所有权限为 JSON（需要超级管理员权限）

    返回包含所有权限的 JSON 文件
    """
    service = PermissionService(db)
    permissions = await service.get_permissions()

    # 转换为可序列化的字典列表
    export_data = [
        {
            "name": p.name,
            "code": p.code,
            "module": p.module,
            "description": p.description,
            "parent_id": p.parent_id,
        }
        for p in permissions
    ]

    return JSONResponse(
        content={
            "version": "1.0",
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "count": len(export_data),
            "permissions": export_data,
        },
        headers={
            "Content-Disposition": 'attachment; filename="permissions.json"'
        }
    )


@router.post("/permissions/import", status_code=status.HTTP_200_OK)
async def import_permissions(
    data: PermissionImportRequest,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    导入权限（需要超级管理员权限）

    从 JSON 数据导入权限，可选择覆盖已存在的权限
    """
    service = PermissionService(db)

    # 转换为字典列表
    permissions_data = [p.model_dump() for p in data.permissions]

    result = await service.import_permissions(permissions_data, data.overwrite)

    return {
        "message": "权限导入完成",
        "created": result["created"],
        "updated": result["updated"],
        "skipped": result["skipped"],
        "errors": result["errors"]
    }


# ============ 角色相关端点 ============

@router.get("/roles", response_model=List[RoleListResponse])
async def get_roles(
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取角色列表"""
    service = RoleService(db)
    return await service.get_roles()


@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取角色详情"""
    service = RoleService(db)
    return await service.get_role(role_id)


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    data: RoleCreate,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """创建角色（需要超级管理员权限）"""
    service = RoleService(db)
    return await service.create_role(data)


@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    data: RoleUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """更新角色（需要超级管理员权限）"""
    service = RoleService(db)
    return await service.update_role(role_id, data)


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """删除角色（需要超级管理员权限）"""
    service = RoleService(db)
    await service.delete_role(role_id)


@router.post("/roles/{role_id}/permissions", status_code=status.HTTP_204_NO_CONTENT)
async def assign_role_permissions(
    role_id: int,
    permission_ids: List[int],
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    为角色分配权限（需要超级管理员权限）

    分配后会清除相关用户的权限缓存
    """
    service = RoleService(db)
    await service.assign_permissions(role_id, permission_ids)

    # 清除相关用户的权限缓存
    # TODO: 实现清除特定角色所有用户缓存的逻辑


@router.post("/roles/batch/permissions", status_code=status.HTTP_200_OK)
async def batch_assign_role_permissions(
    data: BatchAssignPermissionRequest,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    批量为角色分配相同的权限（需要超级管理员权限）

    为多个角色分配相同的权限列表
    """
    service = RoleService(db)
    count = await service.batch_assign_permissions(data.role_ids, data.permission_ids)

    # TODO: 清除所有拥有这些角色的用户的权限缓存

    return {"message": f"成功为 {count} 个角色分配权限"}


# ============ 用户角色相关端点 ============

@router.get("/users/{user_id}/roles", response_model=List[RoleResponse])
async def get_user_roles(
    user_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取用户的角色列表"""
    service = UserRoleService(db)
    return await service.get_user_roles(user_id)


@router.post("/users/{user_id}/roles", status_code=status.HTTP_204_NO_CONTENT)
async def assign_user_roles(
    user_id: int,
    data: AssignRoleRequest,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    为用户分配角色（需要超级管理员权限）

    分配后会清除用户的权限缓存
    """
    service = UserRoleService(db)
    await service.assign_user_roles(user_id, data)

    # 清除用户权限缓存
    clear_permission_cache(user_id)


@router.post("/users/batch/roles", status_code=status.HTTP_200_OK)
async def batch_assign_user_roles(
    data: BatchAssignRoleRequest,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    批量为用户分配相同的角色（需要超级管理员权限）

    为多个用户分配相同的角色列表
    """
    service = UserRoleService(db)
    count = await service.batch_assign_roles(data.user_ids, data.role_ids)

    # 清除所有受影响用户的权限缓存
    for user_id in data.user_ids:
        clear_permission_cache(user_id)

    return {"message": f"成功为 {count} 个用户分配角色"}


@router.post("/users/batch/roles/different", status_code=status.HTTP_200_OK)
async def batch_assign_different_roles(
    data: BatchAssignDifferentRolesRequest,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    批量为用户分配不同的角色（需要超级管理员权限）

    为每个用户分配不同的角色列表
    """
    service = UserRoleService(db)
    # 转换为字典列表
    assignments = [{"user_id": a.user_id, "role_ids": a.role_ids} for a in data.assignments]
    count = await service.batch_assign_different_roles(assignments)

    # 清除所有受影响用户的权限缓存
    for assignment in data.assignments:
        clear_permission_cache(assignment.user_id)

    return {"message": f"成功为 {count} 个用户分配角色"}


@router.get("/users/me/permissions")
async def get_my_permissions(
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户的所有权限"""
    service = UserRoleService(db)
    permissions = await service.get_user_permissions(current_user.id)
    return {"permissions": list(permissions)}
