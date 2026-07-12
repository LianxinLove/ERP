"""
通知系统数据模型

@description 支持站内消息、邮件、短信等多种通知方式

@models
- Notification: 通知主表
- NotificationTemplate: 通知模板表
- NotificationPreference: 通知偏好设置表
- NotificationLog: 通知发送日志表
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, BigInteger, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class NotificationType(str, enum.Enum):
    """通知类型"""
    SYSTEM = "system"  # 系统通知
    WORKFLOW = "workflow"  # 工作流通知
    REMINDER = "reminder"  # 提醒通知
    ANNOUNCEMENT = "announcement"  # 公告通知
    MESSAGE = "message"  # 私信


class NotificationChannel(str, enum.Enum):
    """通知渠道"""
    INBOX = "inbox"  # 站内消息
    EMAIL = "email"  # 邮件
    SMS = "sms"  # 短信
    WEBHOOK = "webhook"  # Webhook


class NotificationPriority(str, enum.Enum):
    """通知优先级"""
    LOW = "low"  # 低
    NORMAL = "normal"  # 普通
    HIGH = "high"  # 高
    URGENT = "urgent"  # 紧急


class NotificationStatus(str, enum.Enum):
    """通知状态"""
    PENDING = "pending"  # 待发送
    SENT = "sent"  # 已发送
    READ = "read"  # 已读
    FAILED = "failed"  # 发送失败
    EXPIRED = "expired"  # 已过期


class Notification(Base):
    """
    通知表

    @description 站内通知消息

    @attributes
    - id: 通知ID
    - type: 通知类型
    - title: 标题
    - content: 内容
    - link: 链接地址
    - sender_id: 发送人ID
    - receiver_id: 接收人ID
    - priority: 优先级
    - status: 状态
    - read_at: 已读时间
    - sent_at: 发送时间
    - expire_at: 过期时间
    - extra_data: 额外数据（JSON）
    - created_at: 创建时间
    """

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # 通知信息
    type: Mapped[str] = mapped_column(
        SQLEnum(NotificationType),
        default=NotificationType.SYSTEM,
        nullable=False,
        index=True,
        comment="通知类型"
    )
    title: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="标题"
    )
    content: Mapped[Optional[str]] = mapped_column(
        Text, comment="内容"
    )
    link: Mapped[Optional[str]] = mapped_column(
        String(500), comment="链接地址"
    )

    # 发送接收信息
    sender_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id"), comment="发送人ID"
    )
    receiver_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False, index=True, comment="接收人ID"
    )

    # 优先级和状态
    priority: Mapped[str] = mapped_column(
        SQLEnum(NotificationPriority),
        default=NotificationPriority.NORMAL,
        nullable=False,
        comment="优先级"
    )
    status: Mapped[str] = mapped_column(
        SQLEnum(NotificationStatus),
        default=NotificationStatus.PENDING,
        nullable=False,
        index=True,
        comment="状态"
    )

    # 时间信息
    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="已读时间"
    )
    sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, index=True, comment="发送时间"
    )
    expire_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="过期时间"
    )

    # 额外数据
    extra_data: Mapped[Optional[dict]] = mapped_column(
        JSON, comment="额外数据（JSON）"
    )

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, index=True, comment="创建时间"
    )

    # 关系
    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])


class NotificationTemplate(Base):
    """
    通知模板表

    @description 通知消息模板

    @attributes
    - id: 模板ID
    - code: 模板编码
    - name: 模板名称
    - type: 通知类型
    - title_template: 标题模板
    - content_template: 内容模板
    - variables: 变量列表（JSON）
    - channels: 支持的渠道（JSON数组）
    - description: 描述
    - is_active: 是否启用
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "notification_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="模板编码"
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="模板名称"
    )
    type: Mapped[str] = mapped_column(
        SQLEnum(NotificationType),
        nullable=False,
        comment="通知类型"
    )
    title_template: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="标题模板"
    )
    content_template: Mapped[Optional[str]] = mapped_column(
        Text, comment="内容模板"
    )
    variables: Mapped[Optional[str]] = None  # JSON - 变量列表
    channels: Mapped[Optional[str]] = None  # JSON - 支持的渠道
    description: Mapped[Optional[str]] = mapped_column(
        Text, comment="描述"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, comment="是否启用"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="更新时间"
    )


class NotificationPreference(Base):
    """
    通知偏好设置表

    @description 用户的通知接收偏好

    @attributes
    - id: 设置ID
    - user_id: 用户ID
    - notification_type: 通知类型
    - inbox_enabled: 是否接收站内消息
    - email_enabled: 是否接收邮件
    - sms_enabled: 是否接收短信
    - quiet_hours_start: 免打扰开始时间
    - quiet_hours_end: 免打扰结束时间
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "notification_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False, unique=True, comment="用户ID"
    )
    notification_type: Mapped[Optional[str]] = mapped_column(
        String(50), comment="通知类型（null表示全部）"
    )

    # 渠道开关
    inbox_enabled: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, comment="站内消息开关"
    )
    email_enabled: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="邮件开关"
    )
    sms_enabled: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="短信开关"
    )

    # 免打扰
    quiet_hours_start: Mapped[Optional[str]] = mapped_column(
        String(5), comment="免打扰开始时间（HH:MM）"
    )
    quiet_hours_end: Mapped[Optional[str]] = mapped_column(
        String(5), comment="免打扰结束时间（HH:MM）"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="更新时间"
    )

    # 关系
    user = relationship("User")


class NotificationLog(Base):
    """
    通知发送日志表

    @description 记录通知的发送情况

    @attributes
    - id: 日志ID
    - notification_id: 通知ID
    - channel: 发送渠道
    - status: 状态
    - error_message: 错误信息
    - sent_at: 发送时间
    - created_at: 创建时间
    """

    __tablename__ = "notification_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    notification_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("notifications.id"), nullable=False, comment="通知ID"
    )
    channel: Mapped[str] = mapped_column(
        SQLEnum(NotificationChannel),
        nullable=False,
        comment="发送渠道"
    )
    status: Mapped[str] = mapped_column(
        String(20), default="pending", nullable=False, comment="状态"
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text, comment="错误信息"
    )
    sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="发送时间"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )
