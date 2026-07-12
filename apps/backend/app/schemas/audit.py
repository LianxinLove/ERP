"""
审计日志Schema
"""

from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field
from enum import Enum


class AuditActionTypeEnum(str, Enum):
    """审计操作类型枚举"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    SUBMIT = "submit"
    APPROVE = "approve"
    REJECT = "reject"
    CANCEL = "cancel"
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    EXPORT = "export"
    IMPORT = "import"
    CONFIG_UPDATE = "config_update"
    PERMISSION_CHANGE = "permission_change"
    OTHER = "other"


class AuditLogLevelEnum(str, Enum):
    """审计日志级别枚举"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditLogDetailResponse(BaseModel):
    """审计日志明细响应"""
    id: int
    field_name: str
    field_label: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    value_type: str

    class Config:
        from_attributes = True


class AuditLogResponse(BaseModel):
    """审计日志响应"""
    id: int
    action_type: AuditActionTypeEnum
    module: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    entity_name: Optional[str] = None
    user_id: Optional[int] = None
    username: Optional[str] = None
    ip_address: Optional[str] = None
    request_method: Optional[str] = None
    request_url: Optional[str] = None
    old_value: Optional[dict] = None
    new_value: Optional[dict] = None
    changes: Optional[List[str]] = None
    description: Optional[str] = None
    level: AuditLogLevelEnum
    status: str
    error_message: Optional[str] = None
    request_id: Optional[str] = None
    session_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogDetailResponse(BaseModel):
    """审计日志详情响应（含明细）"""
    audit_log: AuditLogResponse
    details: List[AuditLogDetailResponse]


class AuditLogQuery(BaseModel):
    """审计日志查询参数"""
    action_type: Optional[AuditActionTypeEnum] = None
    module: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    user_id: Optional[int] = None
    username: Optional[str] = None
    level: Optional[AuditLogLevelEnum] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    keyword: Optional[str] = None  # 搜索关键词（描述、实体名称）
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class AuditLogExportRequest(BaseModel):
    """审计日志导出请求"""
    action_type: Optional[AuditActionTypeEnum] = None
    module: Optional[str] = None
    entity_type: Optional[str] = None
    user_id: Optional[int] = None
    level: Optional[AuditLogLevelEnum] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    format: str = Field(default="csv", pattern="^(csv|excel)$")


class AuditLogStatistics(BaseModel):
    """审计日志统计"""
    total_count: int
    action_type_stats: dict
    module_stats: dict
    daily_stats: List[dict]
    error_count: int
    warning_count: int
