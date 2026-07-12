"""
附件管理Schema
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class AttachmentStorageTypeEnum(str, Enum):
    """附件存储类型枚举"""
    LOCAL = "local"
    OSS = "oss"
    DATABASE = "database"


class AttachmentStatusEnum(str, Enum):
    """附件状态枚举"""
    UPLOADING = "uploading"
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class AttachmentResponse(BaseModel):
    """附件响应"""
    id: int
    file_name: str
    original_name: str
    file_path: str
    file_size: int
    file_type: Optional[str] = None
    file_extension: Optional[str] = None
    file_md5: Optional[str] = None
    storage_type: AttachmentStorageTypeEnum
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    category_id: Optional[int] = None
    uploaded_by: Optional[int] = None
    description: Optional[str] = None
    download_count: int
    status: AttachmentStatusEnum
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AttachmentUploadResponse(BaseModel):
    """附件上传响应"""
    attachment_id: int
    file_name: str
    file_size: int
    file_type: Optional[str] = None
    upload_url: Optional[str] = None
    message: str


class AttachmentDownloadUrl(BaseModel):
    """附件下载URL"""
    download_url: str
    expires_in: int  # 过期时间（秒）


class AttachmentQuery(BaseModel):
    """附件查询参数"""
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    category_id: Optional[int] = None
    uploaded_by: Optional[int] = None
    status: Optional[AttachmentStatusEnum] = None
    file_type: Optional[str] = None  # 文件类型筛选（image/*, application/pdf等）
    keyword: Optional[str] = None  # 搜索关键词
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class AttachmentCategoryResponse(BaseModel):
    """附件分类响应"""
    id: int
    name: str
    code: str
    description: Optional[str] = None
    allowed_types: Optional[str] = None
    max_size: Optional[int] = None
    is_active: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AttachmentCategoryCreate(BaseModel):
    """创建附件分类"""
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=50)
    description: Optional[str] = None
    allowed_types: Optional[str] = None  # 如：image/*,application/pdf,.doc,.docx
    max_size: Optional[int] = None  # 字节
    sort_order: int = Field(default=0)


class AttachmentCategoryUpdate(BaseModel):
    """更新附件分类"""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    allowed_types: Optional[str] = None
    max_size: Optional[int] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None
