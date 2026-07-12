"""
附件管理数据模型

@description 支持文件上传、下载、预览和权限控制

@models
- Attachment: 附件主表
- AttachmentCategory: 附件分类表
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, BigInteger, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class AttachmentStorageType(str, enum.Enum):
    """附件存储类型"""
    LOCAL = "local"  # 本地存储
    OSS = "oss"  # 对象存储
    DATABASE = "database"  # 数据库存储（小文件）


class AttachmentStatus(str, enum.Enum):
    """附件状态"""
    UPLOADING = "uploading"  # 上传中
    ACTIVE = "active"  # 正常
    ARCHIVED = "archived"  # 已归档
    DELETED = "deleted"  # 已删除


class Attachment(Base):
    """
    附件表

    @description 存储文件附件信息

    @attributes
    - id: 附件ID
    - file_name: 文件名
    - original_name: 原始文件名
    - file_path: 文件路径（相对路径）
    - file_size: 文件大小（字节）
    - file_type: 文件类型（MIME类型）
    - file_extension: 文件扩展名
    - file_md5: 文件MD5值（用于去重）
    - storage_type: 存储类型
    - entity_type: 关联实体类型（如：sales_order, purchase_request）
    - entity_id: 关联实体ID
    - category_id: 分类ID
    - uploaded_by: 上传人ID
    - description: 描述
    - download_count: 下载次数
    - status: 状态
    - is_deleted: 是否删除
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # 文件信息
    file_name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="文件名"
    )
    original_name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="原始文件名"
    )
    file_path: Mapped[str] = mapped_column(
        String(500), nullable=False, comment="文件路径"
    )
    file_size: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="文件大小（字节）"
    )
    file_type: Mapped[Optional[str]] = mapped_column(
        String(100), comment="文件类型（MIME）"
    )
    file_extension: Mapped[Optional[str]] = mapped_column(
        String(20), comment="文件扩展名"
    )
    file_md5: Mapped[Optional[str]] = mapped_column(
        String(32), index=True, comment="文件MD5"
    )

    # 存储信息
    storage_type: Mapped[str] = mapped_column(
        SQLEnum(AttachmentStorageType),
        default=AttachmentStorageType.LOCAL,
        nullable=False,
        comment="存储类型"
    )

    # 关联信息
    entity_type: Mapped[Optional[str]] = mapped_column(
        String(100), index=True, comment="关联实体类型"
    )
    entity_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, index=True, comment="关联实体ID"
    )
    category_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("attachment_categories.id"), comment="分类ID"
    )

    # 上传信息
    uploaded_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id"), index=True, comment="上传人ID"
    )
    upload_ip: Mapped[Optional[str]] = mapped_column(
        String(50), comment="上传IP"
    )

    # 其他信息
    description: Mapped[Optional[str]] = mapped_column(
        Text, comment="描述"
    )
    download_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="下载次数"
    )
    status: Mapped[str] = mapped_column(
        SQLEnum(AttachmentStatus),
        default=AttachmentStatus.ACTIVE,
        nullable=False,
        index=True,
        comment="状态"
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True, comment="是否删除"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, index=True, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="更新时间"
    )

    # 关系
    category = relationship("AttachmentCategory", back_populates="attachments")
    uploader = relationship("User", foreign_keys=[uploaded_by])


class AttachmentCategory(Base):
    """
    附件分类表

    @description 附件分类管理

    @attributes
    - id: 分类ID
    - name: 分类名称
    - code: 分类编码
    - description: 描述
    - allowed_types: 允许的文件类型（JSON数组）
    - max_size: 最大文件大小（字节）
    - is_active: 是否启用
    - sort_order: 排序
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "attachment_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="分类名称"
    )
    code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="分类编码"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, comment="描述"
    )
    allowed_types: Mapped[Optional[str]] = mapped_column(
        Text, comment="允许的文件类型（逗号分隔）"
    )
    max_size: Mapped[Optional[int]] = mapped_column(
        BigInteger, comment="最大文件大小（字节）"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, comment="是否启用"
    )
    sort_order: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="排序"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="更新时间"
    )

    # 关系
    attachments = relationship("Attachment", back_populates="category")
