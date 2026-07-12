"""
RBAC 相关的 Pydantic 模型

@description 角色、权限的请求/响应模型
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ============ 权限模型 ============

class PermissionBase(BaseModel):
    """
    权限基础模型
    """
    name: str = Field(..., description="权限名称")
    code: str = Field(..., description="权限编码")
    module: str = Field(..., description="所属模块")
    description: Optional[str] = Field(None, description="权限描述")
    parent_id: Optional[int] = Field(None, description="父权限ID")


class PermissionCreate(PermissionBase):
    """
    创建权限请求模型
    """
    pass


class PermissionUpdate(BaseModel):
    """
    更新权限请求模型
    """
    name: Optional[str] = None
    description: Optional[str] = None


class PermissionExportData(BaseModel):
    """
    权限导出数据模型
    """
    name: str
    code: str
    module: str
    description: Optional[str] = None
    parent_id: Optional[int] = None


class PermissionImportRequest(BaseModel):
    """
    权限导入请求模型
    """
    permissions: List[PermissionExportData]
    overwrite: bool = Field(default=False, description="是否覆盖已存在的权限")


class PermissionResponse(PermissionBase):
    """
    权限响应模型
    """
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ============ 角色模型 ============

class RoleBase(BaseModel):
    """
    角色基础模型
    """
    name: str = Field(..., description="角色名称")
    code: str = Field(..., description="角色编码")
    description: Optional[str] = Field(None, description="角色描述")


class RoleCreate(RoleBase):
    """
    创建角色请求模型
    """
    permission_ids: Optional[List[int]] = Field(default=[], description="权限ID列表")


class RoleUpdate(BaseModel):
    """
    更新角色请求模型
    """
    name: Optional[str] = None
    description: Optional[str] = None
    permission_ids: Optional[List[int]] = None


class BatchAssignPermissionRequest(BaseModel):
    """
    批量分配权限请求模型
    """
    role_ids: List[int] = Field(..., min_length=1, description="角色ID列表")
    permission_ids: List[int] = Field(..., min_length=1, description="权限ID列表")


class RoleResponse(RoleBase):
    """
    角色响应模型
    """
    id: int
    is_system: bool
    created_at: datetime
    updated_at: datetime
    permissions: List[PermissionResponse] = []

    model_config = {"from_attributes": True}


class RoleListResponse(BaseModel):
    """
    角色列表响应模型
    """
    id: int
    name: str
    code: str
    description: Optional[str]
    is_system: bool
    permission_count: int = 0

    model_config = {"from_attributes": True}


# ============ 用户角色模型 ============

class AssignRoleRequest(BaseModel):
    """
    分配角色请求模型
    """
    role_ids: List[int] = Field(..., min_length=1, description="角色ID列表")


class BatchAssignRoleRequest(BaseModel):
    """
    批量分配角色请求模型
    """
    user_ids: List[int] = Field(..., min_length=1, description="用户ID列表")
    role_ids: List[int] = Field(..., min_length=1, description="角色ID列表")


class BatchRoleAssignmentItem(BaseModel):
    """
    批量角色分配单项
    """
    user_id: int
    role_ids: List[int]


class BatchAssignDifferentRolesRequest(BaseModel):
    """
    批量分配不同角色请求模型
    """
    assignments: List[BatchRoleAssignmentItem] = Field(..., min_length=1, description="用户角色分配列表")


class UserRoleResponse(BaseModel):
    """
    用户角色响应模型
    """
    id: int
    user_id: int
    role_id: int
    role: RoleResponse

    model_config = {"from_attributes": True}


# ============ 权限检查模型 ============

class PermissionCheckRequest(BaseModel):
    """
    权限检查请求模型
    """
    permission: str = Field(..., description="权限编码")
    resource_id: Optional[int] = Field(None, description="资源ID（可选，用于细粒度权限控制）")


class PermissionCheckResponse(BaseModel):
    """
    权限检查响应模型
    """
    has_permission: bool
    permission: str
