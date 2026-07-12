"""
附件管理服务
"""

import os
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from pathlib import Path
from sqlalchemy import and_, or_, desc
from sqlalchemy.orm import Session

from app.models.attachment import (
    Attachment,
    AttachmentCategory,
    AttachmentStorageType,
    AttachmentStatus,
)
from app.schemas.attachment import (
    AttachmentQuery,
    AttachmentCategoryCreate,
    AttachmentCategoryUpdate,
)


class AttachmentService:
    """附件管理服务"""

    def __init__(self, db: Session, upload_dir: str = "uploads"):
        self.db = db
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)

        # 按日期组织文件：uploads/YYYY/MM/DD/
        self.date_pattern = "%Y/%m/%d"

    def get_file_path(self, file_name: str, date: datetime = None) -> Path:
        """
        获取文件存储路径

        Args:
            file_name: 文件名
            date: 日期（默认使用当前日期）

        Returns:
            Path: 完整的文件路径
        """
        if date is None:
            date = datetime.now()

        date_path = date.strftime(self.date_pattern)
        full_path = self.upload_dir / date_path / file_name

        # 确保目录存在
        full_path.parent.mkdir(parents=True, exist_ok=True)

        return full_path

    def calculate_md5(self, file_path: Path) -> str:
        """
        计算文件MD5

        Args:
            file_path: 文件路径

        Returns:
            str: MD5值
        """
        md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                md5.update(chunk)
        return md5.hexdigest()

    def find_by_md5(self, file_md5: str) -> Optional[Attachment]:
        """
        根据MD5查找附件（用于去重）

        Args:
            file_md5: MD5值

        Returns:
            Optional[Attachment]: 找到的附件
        """
        return (
            self.db.query(Attachment)
            .filter(
                and_(
                    Attachment.file_md5 == file_md5,
                    Attachment.status == AttachmentStatus.ACTIVE,
                )
            )
            .first()
        )

    def create_attachment(
        self,
        original_name: str,
        file_content: bytes,
        file_type: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        category_id: Optional[int] = None,
        uploaded_by: Optional[int] = None,
        description: Optional[str] = None,
        upload_ip: Optional[str] = None,
    ) -> Attachment:
        """
        创建附件

        Args:
            original_name: 原始文件名
            file_content: 文件内容
            file_type: 文件类型
            entity_type: 关联实体类型
            entity_id: 关联实体ID
            category_id: 分类ID
            uploaded_by: 上传人ID
            description: 描述
            upload_ip: 上传IP

        Returns:
            Attachment: 创建的附件对象
        """
        # 生成唯一文件名
        file_extension = Path(original_name).suffix
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = os.urandom(4).hex()
        file_name = f"{timestamp}_{unique_id}{file_extension}"

        # 获取文件路径
        file_path = self.get_file_path(file_name)
        relative_path = file_path.relative_to(self.upload_dir.parent)

        # 保存文件
        with open(file_path, "wb") as f:
            f.write(file_content)

        # 计算MD5
        file_md5 = self.calculate_md5(file_path)

        # 检查是否已存在相同文件
        existing = self.find_by_md5(file_md5)
        if existing:
            # 删除刚上传的文件
            file_path.unlink()
            return existing

        # 创建附件记录
        attachment = Attachment(
            file_name=file_name,
            original_name=original_name,
            file_path=str(relative_path),
            file_size=len(file_content),
            file_type=file_type,
            file_extension=file_extension.lstrip("."),
            file_md5=file_md5,
            storage_type=AttachmentStorageType.LOCAL,
            entity_type=entity_type,
            entity_id=entity_id,
            category_id=category_id,
            uploaded_by=uploaded_by,
            upload_ip=upload_ip,
            description=description,
            status=AttachmentStatus.ACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        self.db.add(attachment)
        self.db.flush()

        return attachment

    def get_attachment(self, attachment_id: int) -> Optional[Attachment]:
        """
        获取附件

        Args:
            attachment_id: 附件ID

        Returns:
            Optional[Attachment]: 附件对象
        """
        return (
            self.db.query(Attachment)
            .filter(
                and_(
                    Attachment.id == attachment_id,
                    Attachment.is_deleted == False,
                )
            )
            .first()
        )

    def get_attachment_file(self, attachment_id: int) -> Optional[Tuple[Path, str]]:
        """
        获取附件文件

        Args:
            attachment_id: 附件ID

        Returns:
            Optional[Tuple[Path, str]]: (文件路径, 文件名) 或 None
        """
        attachment = self.get_attachment(attachment_id)
        if not attachment:
            return None

        if attachment.storage_type == AttachmentStorageType.LOCAL:
            file_path = self.upload_dir.parent / attachment.file_path
            if file_path.exists():
                return (file_path, attachment.original_name)

        return None

    def increment_download_count(self, attachment_id: int):
        """
        增加下载次数

        Args:
            attachment_id: 附件ID
        """
        self.db.query(Attachment).filter(Attachment.id == attachment_id).update(
            {"download_count": Attachment.download_count + 1}
        )

    def get_attachments(
        self,
        query: AttachmentQuery,
    ) -> Tuple[List[Attachment], int]:
        """
        获取附件列表

        Args:
            query: 查询参数

        Returns:
            Tuple[List[Attachment], int]: (附件列表, 总数)
        """
        # 构建查询
        q = self.db.query(Attachment).filter(Attachment.is_deleted == False)

        # 筛选条件
        if query.entity_type:
            q = q.filter(Attachment.entity_type == query.entity_type)
        if query.entity_id:
            q = q.filter(Attachment.entity_id == query.entity_id)
        if query.category_id:
            q = q.filter(Attachment.category_id == query.category_id)
        if query.uploaded_by:
            q = q.filter(Attachment.uploaded_by == query.uploaded_by)
        if query.status:
            q = q.filter(Attachment.status == query.status.value)
        if query.file_type:
            # 支持通配符匹配，如 image/*
            if "*" in query.file_type:
                pattern = query.file_type.replace("*", "%")
                q = q.filter(Attachment.file_type.like(pattern))
            else:
                q = q.filter(Attachment.file_type == query.file_type)
        if query.keyword:
            q = q.filter(
                or_(
                    Attachment.original_name.like(f"%{query.keyword}%"),
                    Attachment.description.like(f"%{query.keyword}%"),
                )
            )

        # 获取总数
        total = q.count()

        # 分页和排序
        attachments = (
            q.order_by(desc(Attachment.created_at))
            .offset((query.page - 1) * query.page_size)
            .limit(query.query.page_size)
            .all()
        )

        return attachments, total

    def delete_attachment(self, attachment_id: int, deleted_by: int) -> bool:
        """
        删除附件（软删除）

        Args:
            attachment_id: 附件ID
            deleted_by: 删除人ID

        Returns:
            bool: 是否成功
        """
        attachment = self.get_attachment(attachment_id)
        if not attachment:
            return False

        # 软删除
        attachment.is_deleted = True
        attachment.status = AttachmentStatus.DELETED
        attachment.updated_at = datetime.now()

        return True

    def hard_delete_attachment(self, attachment_id: int) -> bool:
        """
        硬删除附件（删除文件和记录）

        Args:
            attachment_id: 附件ID

        Returns:
            bool: 是否成功
        """
        attachment = self.get_attachment(attachment_id)
        if not attachment:
            return False

        # 删除文件
        if attachment.storage_type == AttachmentStorageType.LOCAL:
            file_path = self.upload_dir.parent / attachment.file_path
            if file_path.exists():
                file_path.unlink()

        # 删除记录
        self.db.delete(attachment)

        return True


class AttachmentCategoryService:
    """附件分类服务"""

    def __init__(self, db: Session):
        self.db = db

    def create_category(
        self,
        data: AttachmentCategoryCreate,
    ) -> AttachmentCategory:
        """
        创建附件分类

        Args:
            data: 分类数据

        Returns:
            AttachmentCategory: 创建的分类对象
        """
        category = AttachmentCategory(
            name=data.name,
            code=data.code,
            description=data.description,
            allowed_types=data.allowed_types,
            max_size=data.max_size,
            sort_order=data.sort_order,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        self.db.add(category)
        self.db.flush()

        return category

    def get_category(self, category_id: int) -> Optional[AttachmentCategory]:
        """获取附件分类"""
        return (
            self.db.query(AttachmentCategory)
            .filter(AttachmentCategory.id == category_id)
            .first()
        )

    def get_categories(
        self,
        is_active: Optional[bool] = None,
    ) -> List[AttachmentCategory]:
        """
        获取附件分类列表

        Args:
            is_active: 是否只返回启用的分类

        Returns:
            List[AttachmentCategory]: 分类列表
        """
        q = self.db.query(AttachmentCategory)

        if is_active is not None:
            q = q.filter(AttachmentCategory.is_active == is_active)

        return q.order_by(AttachmentCategory.sort_order).all()

    def update_category(
        self,
        category_id: int,
        data: AttachmentCategoryUpdate,
    ) -> Optional[AttachmentCategory]:
        """
        更新附件分类

        Args:
            category_id: 分类ID
            data: 更新数据

        Returns:
            Optional[AttachmentCategory]: 更新后的分类对象
        """
        category = self.get_category(category_id)
        if not category:
            return None

        # 更新字段
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)

        category.updated_at = datetime.now()

        return category

    def delete_category(self, category_id: int) -> bool:
        """
        删除附件分类

        Args:
            category_id: 分类ID

        Returns:
            bool: 是否成功
        """
        category = self.get_category(category_id)
        if not category:
            return False

        # 检查是否有附件使用此分类
        count = (
            self.db.query(Attachment)
            .filter(Attachment.category_id == category_id)
            .count()
        )
        if count > 0:
            raise ValueError(f"分类下还有 {count} 个附件，无法删除")

        self.db.delete(category)
        return True
