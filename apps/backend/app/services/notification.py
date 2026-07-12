"""
通知系统服务
"""

from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from sqlalchemy import and_, or_, desc
from sqlalchemy.orm import Session

from app.models.notification import (
    Notification,
    NotificationTemplate,
    NotificationPreference,
    NotificationLog,
    NotificationType,
    NotificationChannel,
    NotificationPriority,
    NotificationStatus,
)
from app.schemas.notification import (
    NotificationCreate,
    NotificationBatchCreate,
    NotificationTemplateCreate,
    NotificationPreferenceUpdate,
)


class NotificationService:
    """通知服务"""

    def __init__(self, db: Session):
        self.db = db

    def create_notification(
        self,
        data: NotificationCreate,
        sender_id: Optional[int] = None,
    ) -> Notification:
        """
        创建通知

        Args:
            data: 通知数据
            sender_id: 发送人ID

        Returns:
            Notification: 创建的通知对象
        """
        # 计算过期时间
        expire_at = None
        if data.expire_hours:
            expire_at = datetime.now() + timedelta(hours=data.expire_hours)

        notification = Notification(
            type=data.type,
            title=data.title,
            content=data.content,
            link=data.link,
            sender_id=sender_id,
            receiver_id=data.receiver_id,
            priority=data.priority,
            status=NotificationStatus.PENDING,
            expire_at=expire_at,
            created_at=datetime.now(),
        )

        self.db.add(notification)
        self.db.flush()

        return notification

    def create_batch_notifications(
        self,
        data: NotificationBatchCreate,
        sender_id: Optional[int] = None,
    ) -> List[Notification]:
        """
        批量创建通知

        Args:
            data: 批量通知数据
            sender_id: 发送人ID

        Returns:
            List[Notification]: 创建的通知列表
        """
        notifications = []

        # 计算过期时间
        expire_at = None
        if data.expire_hours:
            expire_at = datetime.now() + timedelta(hours=data.expire_hours)

        for receiver_id in data.receiver_ids:
            notification = Notification(
                type=data.type,
                title=data.title,
                content=data.content,
                link=data.link,
                sender_id=sender_id,
                receiver_id=receiver_id,
                priority=data.priority,
                status=NotificationStatus.PENDING,
                expire_at=expire_at,
                created_at=datetime.now(),
            )
            self.db.add(notification)
            notifications.append(notification)

        self.db.flush()

        return notifications

    def send_notification(self, notification_id: int) -> bool:
        """
        发送通知

        Args:
            notification_id: 通知ID

        Returns:
            bool: 是否发送成功
        """
        notification = (
            self.db.query(Notification)
            .filter(Notification.id == notification_id)
            .first()
        )

        if not notification:
            return False

        # 检查是否过期
        if notification.expire_at and notification.expire_at < datetime.now():
            notification.status = NotificationStatus.EXPIRED
            return False

        # 检查用户偏好设置
        preference = (
            self.db.query(NotificationPreference)
            .filter(
                and_(
                    NotificationPreference.user_id == notification.receiver_id,
                    or_(
                        NotificationPreference.notification_type == None,
                        NotificationPreference.notification_type == notification.type.value,
                    ),
                )
            )
            .first()
        )

        # 默认启用站内消息
        inbox_enabled = True
        if preference:
            inbox_enabled = preference.inbox_enabled

        if not inbox_enabled:
            return False

        # 更新状态为已发送
        notification.status = NotificationStatus.SENT
        notification.sent_at = datetime.now()

        # 记录日志
        log = NotificationLog(
            notification_id=notification_id,
            channel=NotificationChannel.INBOX,
            status="success",
            sent_at=datetime.now(),
            created_at=datetime.now(),
        )
        self.db.add(log)

        return True

    def get_user_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Notification], int]:
        """
        获取用户通知列表

        Args:
            user_id: 用户ID
            unread_only: 是否只返回未读消息
            page: 页码
            page_size: 每页数量

        Returns:
            Tuple[List[Notification], int]: (通知列表, 总数)
        """
        q = self.db.query(Notification).filter(
            Notification.receiver_id == user_id
        )

        if unread_only:
            q = q.filter(Notification.status != NotificationStatus.READ)

        # 排除已过期的
        q = q.filter(
            or_(
                Notification.expire_at == None,
                Notification.expire_at > datetime.now(),
            )
        )

        # 获取总数
        total = q.count()

        # 分页和排序
        notifications = (
            q.order_by(
                desc(Notification.priority),
                desc(Notification.created_at),
            )
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return notifications, total

    def get_unread_count(self, user_id: int) -> dict:
        """
        获取用户未读消息数

        Args:
            user_id: 用户ID

        Returns:
            dict: {total: 总数, by_type: {type: count}}
        """
        # 总未读数
        total = (
            self.db.query(Notification)
            .filter(
                and_(
                    Notification.receiver_id == user_id,
                    Notification.status != NotificationStatus.READ,
                )
            )
            .count()
        )

        # 按类型统计
        from sqlalchemy import func

        type_stats = (
            self.db.query(Notification.type, func.count(Notification.id))
            .filter(
                and_(
                    Notification.receiver_id == user_id,
                    Notification.status != NotificationStatus.READ,
                )
            )
            .group_by(Notification.type)
            .all()
        )

        by_type = {t.value: c for t, c in type_stats}

        return {"total": total, "by_type": by_type}

    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """
        标记通知为已读

        Args:
            notification_id: 通知ID
            user_id: 用户ID

        Returns:
            bool: 是否成功
        """
        notification = (
            self.db.query(Notification)
            .filter(
                and_(
                    Notification.id == notification_id,
                    Notification.receiver_id == user_id,
                )
            )
            .first()
        )

        if not notification:
            return False

        notification.status = NotificationStatus.READ
        notification.read_at = datetime.now()

        return True

    def mark_all_as_read(self, user_id: int) -> int:
        """
        标记所有通知为已读

        Args:
            user_id: 用户ID

        Returns:
            int: 标记的数量
        """
        count = (
            self.db.query(Notification)
            .filter(
                and_(
                    Notification.receiver_id == user_id,
                    Notification.status != NotificationStatus.READ,
                )
            )
            .update(
                {
                    "status": NotificationStatus.READ,
                    "read_at": datetime.now(),
                }
            )
        )

        return count

    def delete_notification(self, notification_id: int, user_id: int) -> bool:
        """
        删除通知

        Args:
            notification_id: 通知ID
            user_id: 用户ID

        Returns:
            bool: 是否成功
        """
        notification = (
            self.db.query(Notification)
            .filter(
                and_(
                    Notification.id == notification_id,
                    Notification.receiver_id == user_id,
                )
            )
            .first()
        )

        if not notification:
            return False

        self.db.delete(notification)

        return True


class NotificationTemplateService:
    """通知模板服务"""

    def __init__(self, db: Session):
        self.db = db

    def create_template(self, data: NotificationTemplateCreate) -> NotificationTemplate:
        """创建通知模板"""
        import json

        template = NotificationTemplate(
            code=data.code,
            name=data.name,
            type=data.type,
            title_template=data.title_template,
            content_template=data.content_template,
            variables=json.dumps(data.variables) if data.variables else None,
            channels=json.dumps(data.channels) if data.channels else None,
            description=data.description,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        self.db.add(template)
        self.db.flush()

        return template

    def get_template(self, code: str) -> Optional[NotificationTemplate]:
        """获取通知模板"""
        return (
            self.db.query(NotificationTemplate)
            .filter(
                and_(
                    NotificationTemplate.code == code,
                    NotificationTemplate.is_active == True,
                )
            )
            .first()
        )

    def get_templates(
        self,
        type: Optional[NotificationType] = None,
        is_active: Optional[bool] = None,
    ) -> List[NotificationTemplate]:
        """获取通知模板列表"""
        q = self.db.query(NotificationTemplate)

        if type:
            q = q.filter(NotificationTemplate.type == type)
        if is_active is not None:
            q = q.filter(NotificationTemplate.is_active == is_active)

        return q.order_by(NotificationTemplate.id).all()


class NotificationPreferenceService:
    """通知偏好设置服务"""

    def __init__(self, db: Session):
        self.db = db

    def get_user_preference(self, user_id: int) -> NotificationPreference:
        """获取用户通知偏好设置"""
        preference = (
            self.db.query(NotificationPreference)
            .filter(NotificationPreference.user_id == user_id)
            .first()
        )

        if not preference:
            # 创建默认设置
            preference = NotificationPreference(
                user_id=user_id,
                inbox_enabled=True,
                email_enabled=False,
                sms_enabled=False,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            self.db.add(preference)
            self.db.flush()

        return preference

    def update_preference(
        self,
        user_id: int,
        data: NotificationPreferenceUpdate,
    ) -> NotificationPreference:
        """更新用户通知偏好设置"""
        preference = self.get_user_preference(user_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(preference, field, value)

        preference.updated_at = datetime.now()

        return preference
