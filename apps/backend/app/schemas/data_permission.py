"""
数据权限相关的 Pydantic 模型
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DataPermissionBase(BaseModel):
    """数据权限基础模型"""
    resource_type: str = Field(..., description="资源类型")
    scope: str = Field(..., description="数据范围（all/dept/department/self/custom）")
    scope_config: Optional[str] = Field(None, description="范围配置（JSON格式）")


class DataPermissionCreate(DataPermissionBase):
    """创建数据权限请求模型"""
    user_id: Optional[int] = Field(None, description="用户ID（与role_id二选一）")
    role_id: Optional[int] = Field(None, description="角色ID（与user_id二选一）")


class DataPermissionUpdate(BaseModel):
    """更新数据权限请求模型"""
    resource_type: Optional[str] = None
    scope: Optional[str] = None
    scope_config: Optional[str] = None
    is_active: Optional[bool] = None


class DataPermissionResponse(DataPermissionBase):
    """数据权限响应模型"""
    id: int
    user_id: Optional[int]
    role_id: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DataScopeResponse(BaseModel):
    """数据范围查询响应"""
    resource_type: str
    scope: str
    scope_description: str
