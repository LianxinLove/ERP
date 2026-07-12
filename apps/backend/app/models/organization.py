"""
组织架构数据模型

@description 部门、职位、员工档案的数据库模型
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Department(Base):
    """
    部门模型

    Attributes:
        id: 主键ID
        name: 部门名称
        code: 部门编码（唯一）
        parent_id: 父部门ID
        level: 层级
        sort_order: 排序
        leader_id: 部门负责人ID
        description: 部门描述
        created_at: 创建时间
        updated_at: 更新时间
        created_by: 创建人ID
        updated_by: 更新人ID
        is_deleted: 是否删除
        deleted_at: 删除时间
    """

    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("departments.id", ondelete="SET NULL"), index=True
    )
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    leader_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    description: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    created_by: Mapped[Optional[int]] = mapped_column()
    updated_by: Mapped[Optional[int]] = mapped_column()
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # 关系
    parent: Mapped[Optional["Department"]] = relationship(
        "Department", remote_side=[id], backref="children"
    )
    leader: Mapped[Optional["User"]] = relationship("User", foreign_keys=[leader_id])
    employees: Mapped[list["EmployeeProfile"]] = relationship(
        "EmployeeProfile", back_populates="department"
    )

    def __repr__(self) -> str:
        return f"<Department(id={self.id}, name='{self.name}', code='{self.code}')>"


class Position(Base):
    """
    职位模型

    Attributes:
        id: 主键ID
        name: 职位名称
        code: 职位编码（唯一）
        level: 职级
        description: 职位描述
        created_at: 创建时间
        updated_at: 更新时间
        is_deleted: 是否删除
        deleted_at: 删除时间
    """

    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # 关系
    employees: Mapped[list["EmployeeProfile"]] = relationship(
        "EmployeeProfile", back_populates="position"
    )

    def __repr__(self) -> str:
        return f"<Position(id={self.id}, name='{self.name}', code='{self.code}')>"


class EmployeeProfile(Base):
    """
    员工档案模型

    Attributes:
        id: 主键ID
        user_id: 用户ID（唯一）
        employee_no: 员工编号（唯一）
        department_id: 部门ID
        position_id: 职位ID
        entry_date: 入职日期
        status: 状态（active-在职，resigned-离职）
        created_at: 创建时间
        updated_at: 更新时间
        is_deleted: 是否删除
        deleted_at: 删除时间
    """

    __tablename__ = "employee_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    employee_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    department_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("departments.id", ondelete="SET NULL"), index=True
    )
    position_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("positions.id", ondelete="SET NULL"), index=True
    )
    entry_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # 关系
    user: Mapped["User"] = relationship("User", back_populates="employee_profile")
    department: Mapped[Optional["Department"]] = relationship("Department", back_populates="employees")
    position: Mapped[Optional["Position"]] = relationship("Position", back_populates="employees")

    def __repr__(self) -> str:
        return f"<EmployeeProfile(id={self.id}, employee_no='{self.employee_no}', status='{self.status}')>"


# 更新User模型添加关系
from app.models.user import User

# 添加User模型的employee_profile关系（需要在User模型中定义）
