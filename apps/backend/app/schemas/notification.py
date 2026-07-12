"""
通知系统Schema
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class NotificationTypeEnum(str, Enum):
    """通知类型枚举"""
    SYSTEM = "system"
    WORKFLOW = "workflow"
    REMINDER = "reminder"
    ANNOUNCEMENT = "announcement"
    MESSAGE = "message"


class NotificationChannelEnum(str, Enum):
    """通知渠道枚举"""
    INBOX = "inbox"
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"


class NotificationPriorityEnum(str, Enum):
    """通知优先级枚举"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationStatusEnum(str, Enum):
    """通知状态枚举"""
    PENDING = "pending"
    SENT = "sent"
    READ = "read"
    FAILED = "failed"
    EXPIRED = "expired"


class NotificationResponse(BaseModel):
    """通知响应"""
    id: int
    type: NotificationTypeEnum
    title: str
    content: Optional[str] = None
    link: Optional[str] = None
    sender_id: Optional[int] = None
    receiver_id: int
    priority: NotificationPriorityEnum
    status: NotificationStatusEnum
    read_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    expire_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationCreate(BaseModel):
    """创建通知"""
    receiver_id: int
    type: NotificationTypeEnum
    title: str
    content: Optional[str] = None
    link: Optional[str] = None
    priority: NotificationPriorityEnum = NotificationPriorityEnum.NORMAL
    expire_hours: Optional[int] = Field(None, description="过期小时数")


class NotificationBatchCreate(BaseModel):
    """批量创建通知"""
    receiver_ids: List[int]
    type: NotificationTypeEnum
    title: str
    content: Optional[str] = None
    link: Optional[str] = None
    priority: NotificationPriorityEnum = NotificationPriorityEnum.NORMAL
    expire_hours: Optional[int] = None


class NotificationTemplateResponse(BaseModel):
    """通知模板响应"""
    id: int
    code: str
    name: str
    type: NotificationTypeEnum
    title_template: str
    content_template: Optional[str] = None
    variables: Optional[List[str]] = None
    channels: Optional[List[str]] = None
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationTemplateCreate(BaseModel):
    """创建通知模板"""
    code: str
    name: str
    type: NotificationTypeEnum
    title_template: str
    content_template: Optional[str] = None
    variables: Optional[List[str]] = None
    channels: Optional[List[str]] = None
    description: Optional[str] = None


class NotificationPreferenceResponse(BaseModel):
    """通知偏好设置响应"""
    id: int
    user_id: int
    notification_type: Optional[str] = None
    inbox_enabled: bool
    email_enabled: bool
    sms_enabled: bool
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationPreferenceUpdate(BaseModel):
    """更新通知偏好设置"""
    notification_type: Optional[str] = None
    inbox_enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None


class UnreadCountResponse(BaseModel):
    """未读消息数响应"""
    total: int
    by_type: dict
