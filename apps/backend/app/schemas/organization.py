"""
组织架构相关的 Pydantic 模型

@description 部门、职位、员工档案的请求/响应模型
"""

from datetime import datetime, date
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.core.sanitization import sanitize_string


# ============ 部门模型 ============

class DepartmentBase(BaseModel):
    """
    部门基础模型
    """
    name: str = Field(..., description="部门名称")
    code: str = Field(..., description="部门编码")
    parent_id: Optional[int] = Field(None, description="父部门ID")
    sort_order: int = Field(0, description="排序")
    leader_id: Optional[int] = Field(None, description="部门负责人ID")
    description: Optional[str] = Field(None, description="部门描述")

    @field_validator('name')
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """清理部门名称，防止XSS"""
        return sanitize_string(v)

    @field_validator('description')
    @classmethod
    def sanitize_description(cls, v: Optional[str]) -> Optional[str]:
        """清理部门描述，防止XSS"""
        return sanitize_string(v) if v else v


class DepartmentCreate(DepartmentBase):
    """
    创建部门请求模型
    """
    pass


class DepartmentUpdate(BaseModel):
    """
    更新部门请求模型
    """
    name: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None
    leader_id: Optional[int] = None
    description: Optional[str] = None


class DepartmentResponse(DepartmentBase):
    """
    部门响应模型
    """
    id: int
    level: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DepartmentTree(DepartmentResponse):
    """
    部门树形结构模型
    """
    children: List["DepartmentTree"] = []

    model_config = {"from_attributes": True}


# ============ 职位模型 ============

class PositionBase(BaseModel):
    """
    职位基础模型
    """
    name: str = Field(..., description="职位名称")
    code: str = Field(..., description="职位编码")
    level: int = Field(..., description="职级")
    description: Optional[str] = Field(None, description="职位描述")

    @field_validator('name')
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """清理职位名称，防止XSS"""
        return sanitize_string(v)

    @field_validator('description')
    @classmethod
    def sanitize_description(cls, v: Optional[str]) -> Optional[str]:
        """清理职位描述，防止XSS"""
        return sanitize_string(v) if v else v


class PositionCreate(PositionBase):
    """
    创建职位请求模型
    """
    pass


class PositionUpdate(BaseModel):
    """
    更新职位请求模型
    """
    name: Optional[str] = None
    level: Optional[int] = None
    description: Optional[str] = None


class PositionResponse(PositionBase):
    """
    职位响应模型
    """
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ============ 员工档案模型 ============

class EmployeeProfileBase(BaseModel):
    """
    员工档案基础模型
    """
    user_id: int = Field(..., description="用户ID")
    employee_no: str = Field(..., description="员工编号")
    department_id: Optional[int] = Field(None, description="部门ID")
    position_id: Optional[int] = Field(None, description="职位ID")
    entry_date: Optional[date] = Field(None, description="入职日期")
    status: str = Field("active", description="状态")


class EmployeeProfileCreate(EmployeeProfileBase):
    """
    创建员工档案请求模型
    """
    pass


class EmployeeProfileUpdate(BaseModel):
    """
    更新员工档案请求模型
    """
    department_id: Optional[int] = None
    position_id: Optional[int] = None
    entry_date: Optional[date] = None
    status: Optional[str] = None


class EmployeeProfileResponse(EmployeeProfileBase):
    """
    员工档案响应模型
    """
    id: int
    created_at: datetime
    updated_at: datetime
    # 关联信息
    department: Optional[DepartmentResponse] = None
    position: Optional[PositionResponse] = None

    model_config = {"from_attributes": True}


class EmployeeDetailResponse(EmployeeProfileResponse):
    """
    员工详情响应模型
    """
    # 用户信息
    user_id: int
    username: str
    email: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
