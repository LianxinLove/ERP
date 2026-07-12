"""
数据权限模型

@description 行级数据权限控制，支持用户只能访问自己创建的数据
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class DataPermission(Base):
    """
    数据权限模型

    定义用户对特定资源的数据访问范围

    Attributes:
        id: 主键ID
        user_id: 用户ID（NULL表示适用于所有用户）
        role_id: 角色ID（NULL表示不限定角色）
        resource_type: 资源类型（如 'sales_order', 'purchase_request'）
        scope: 数据范围（all/dept/department/self/custom）
        scope_config: 范围配置（JSON格式）
        is_active: 是否启用
        created_at: 创建时间
        updated_at: 更新时间
    """

    __tablename__ = "data_permissions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    role_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"), index=True
    )
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    scope: Mapped[str] = mapped_column(String(20), nullable=False, default="self")
    scope_config: Mapped[Optional[str]] = mapped_column(Text)  # JSON配置
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<DataPermission(resource_type='{self.resource_type}', scope='{self.scope}')>"


class DataScopeEnum:
    """
    数据范围枚举

    - all: 全部数据
    - dept: 本部门及子部门数据
    - department: 仅本部门数据
    - self: 仅自己创建的数据
    - custom: 自定义范围（通过scope_config配置）
    """

    ALL = "all"          # 全部数据
    DEPT = "dept"        # 本部门及子部门
    DEPARTMENT = "department"  # 仅本部门
    SELF = "self"        # 仅自己创建的数据
    CUSTOM = "custom"    # 自定义范围
