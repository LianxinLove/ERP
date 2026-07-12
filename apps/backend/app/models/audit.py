"""
审计日志数据模型

@description 记录系统所有操作和数据变更，用于安全审计和合规要求

@models
- AuditLog: 审计日志主表
- AuditLogDetail: 审计日志明细表（记录字段级别的变更）
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, BigInteger, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class AuditActionType(str, enum.Enum):
    """审计操作类型"""
    # 数据操作
    CREATE = "create"  # 创建
    UPDATE = "update"  # 更新
    DELETE = "delete"  # 删除

    # 业务操作
    SUBMIT = "submit"  # 提交
    APPROVE = "approve"  # 审批
    REJECT = "reject"  # 拒绝
    CANCEL = "cancel"  # 取消

    # 登录操作
    LOGIN = "login"  # 登录
    LOGOUT = "logout"  # 登出
    LOGIN_FAILED = "login_failed"  # 登录失败

    # 导入导出
    EXPORT = "export"  # 导出
    IMPORT = "import"  # 导入

    # 配置操作
    CONFIG_UPDATE = "config_update"  # 配置更新
    PERMISSION_CHANGE = "permission_change"  # 权限变更

    # 其他
    OTHER = "other"  # 其他


class AuditLogLevel(str, enum.Enum):
    """审计日志级别"""
    INFO = "info"  # 信息
    WARNING = "warning"  # 警告
    ERROR = "error"  # 错误
    CRITICAL = "critical"  # 严重"


class AuditLog(Base):
    """
    审计日志表

    @description 记录所有系统操作和数据变更

    @attributes
    - id: 日志ID
    - action_type: 操作类型
    - module: 模块名称
    - entity_type: 实体类型（表名）
    - entity_id: 实体ID
    - entity_name: 实体名称（用于显示）
    - user_id: 操作人ID
    - username: 操作人用户名（冗余，防止用户删除后无法追溯）
    - ip_address: IP地址
    - user_agent: 用户代理
    - request_method: 请求方法（GET/POST/PUT/DELETE）
    - request_url: 请求URL
    - old_value: 变更前的值（JSON）
    - new_value: 变更后的值（JSON）
    - changes: 变更字段列表（JSON）
    - description: 操作描述
    - level: 日志级别
    - status: 操作状态（success/failed/partial）
    - error_message: 错误信息（如果操作失败）
    - request_id: 请求ID（用于关联同一请求的多个操作）
    - session_id: 会话ID
    - created_at: 创建时间
    """

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # 操作信息
    action_type: Mapped[str] = mapped_column(
        SQLEnum(AuditActionType),
        nullable=False,
        index=True,
        comment="操作类型"
    )
    module: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True, comment="模块名称"
    )
    entity_type: Mapped[Optional[str]] = mapped_column(
        String(100), index=True, comment="实体类型（表名）"
    )
    entity_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, index=True, comment="实体ID"
    )
    entity_name: Mapped[Optional[str]] = mapped_column(
        String(200), comment="实体名称"
    )

    # 操作人信息
    user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id"), index=True, comment="操作人ID"
    )
    username: Mapped[Optional[str]] = mapped_column(
        String(100), index=True, comment="操作人用户名"
    )

    # 请求信息
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(50), comment="IP地址"
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        Text, comment="用户代理"
    )
    request_method: Mapped[Optional[str]] = mapped_column(
        String(10), comment="请求方法"
    )
    request_url: Mapped[Optional[str]] = mapped_column(
        String(500), comment="请求URL"
    )

    # 变更数据
    old_value: Mapped[Optional[dict]] = mapped_column(
        JSON, comment="变更前的值（JSON）"
    )
    new_value: Mapped[Optional[dict]] = mapped_column(
        JSON, comment="变更后的值（JSON）"
    )
    changes: Mapped[Optional[list]] = mapped_column(
        JSON, comment="变更字段列表（JSON）"
    )

    # 其他信息
    description: Mapped[Optional[str]] = mapped_column(
        Text, comment="操作描述"
    )
    level: Mapped[str] = mapped_column(
        SQLEnum(AuditLogLevel),
        default=AuditLogLevel.INFO,
        nullable=False,
        index=True,
        comment="日志级别"
    )
    status: Mapped[str] = mapped_column(
        String(20), default="success", comment="操作状态"
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text, comment="错误信息"
    )
    request_id: Mapped[Optional[str]] = mapped_column(
        String(100), index=True, comment="请求ID"
    )
    session_id: Mapped[Optional[str]] = mapped_column(
        String(100), index=True, comment="会话ID"
    )

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, index=True, comment="创建时间"
    )

    # 关系
    details = relationship(
        "AuditLogDetail",
        back_populates="audit_log",
        cascade="all, delete-orphan"
    )


class AuditLogDetail(Base):
    """
    审计日志明细表

    @description 记录字段级别的变更详情

    @attributes
    - id: 明细ID
    - audit_log_id: 审计日志ID
    - field_name: 字段名称
    - field_label: 字段显示名称
    - old_value: 旧值
    - new_value: 新值
    - value_type: 值类型（string/number/date/json）
    """

    __tablename__ = "audit_log_details"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    audit_log_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("audit_logs.id"),
        nullable=False,
        comment="审计日志ID"
    )
    field_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="字段名称"
    )
    field_label: Mapped[Optional[str]] = mapped_column(
        String(100), comment="字段显示名称"
    )
    old_value: Mapped[Optional[str]] = mapped_column(
        Text, comment="旧值"
    )
    new_value: Mapped[Optional[str]] = mapped_column(
        Text, comment="新值"
    )
    value_type: Mapped[str] = mapped_column(
        String(20), default="string", comment="值类型"
    )

    # 关系
    audit_log = relationship("AuditLog", back_populates="details")
