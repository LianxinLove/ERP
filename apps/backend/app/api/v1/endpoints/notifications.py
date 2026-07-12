"""
通知系统API端点
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.core.permissions import require_permission
from app.models.user import User
from app.schemas.notification import (
    NotificationResponse,
    NotificationCreate,
    NotificationBatchCreate,
    NotificationTemplateResponse,
    NotificationTemplateCreate,
    NotificationPreferenceResponse,
    NotificationPreferenceUpdate,
    UnreadCountResponse,
)
from app.services.notification import (
    NotificationService,
    NotificationTemplateService,
    NotificationPreferenceService,
)

router = APIRouter(prefix="/notifications", tags=["通知系统"])


@router.post("/", summary="创建通知")
@require_permission("notification.create")
async def create_notification(
    data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建通知"""
    service = NotificationService(db)
    notification = service.create_notification(data, sender_id=current_user.id)

    # 自动发送
    service.send_notification(notification.id)

    return NotificationResponse.model_validate(notification)


@router.post("/batch", summary="批量创建通知")
@require_permission("notification.create")
async def create_batch_notifications(
    data: NotificationBatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """批量创建通知"""
    service = NotificationService(db)
    notifications = service.create_batch_notifications(data, sender_id=current_user.id)

    # 自动发送
    for notification in notifications:
        service.send_notification(notification.id)

    return {
        "message": f"成功创建 {len(notifications)} 条通知",
        "count": len(notifications),
    }


@router.get("/my", summary="获取我的通知")
async def get_my_notifications(
    unread_only: bool = Query(False, description="是否只返回未读消息"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取当前用户的通知列表"""
    service = NotificationService(db)
    notifications, total = service.get_user_notifications(
        current_user.id,
        unread_only=unread_only,
        page=page,
        page_size=page_size,
    )

    return {
        "items": [NotificationResponse.model_validate(n) for n in notifications],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/my/unread-count", summary="获取未读消息数")
async def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取当前用户的未读消息数"""
    service = NotificationService(db)
    count = service.get_unread_count(current_user.id)

    return UnreadCountResponse(**count)


@router.put("/my/{notification_id}/read", summary="标记通知为已读")
async def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """标记通知为已读"""
    service = NotificationService(db)
    success = service.mark_as_read(notification_id, current_user.id)

    if not success:
        raise HTTPException(status_code=404, detail="通知不存在")

    return {"message": "已标记为已读"}


@router.put("/my/read-all", summary="标记所有通知为已读")
async def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """标记所有通知为已读"""
    service = NotificationService(db)
    count = service.mark_all_as_read(current_user.id)

    return {"message": f"已标记 {count} 条通知为已读", "count": count}


@router.delete("/my/{notification_id}", summary="删除通知")
async def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除通知"""
    service = NotificationService(db)
    success = service.delete_notification(notification_id, current_user.id)

    if not success:
        raise HTTPException(status_code=404, detail="通知不存在")

    return {"message": "删除成功"}


# ===== 通知模板 =====

@router.post("/templates", summary="创建通知模板")
@require_permission("notification.template.create")
async def create_template(
    data: NotificationTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建通知模板"""
    service = NotificationTemplateService(db)
    template = service.create_template(data)

    return NotificationTemplateResponse.model_validate(template)


@router.get("/templates", summary="获取通知模板列表")
@require_permission("notification.template.read")
async def get_templates(
    type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
):
    """获取通知模板列表"""
    service = NotificationTemplateService(db)
    templates = service.get_templates(type=type, is_active=is_active)

    return {
        "items": [NotificationTemplateResponse.model_validate(t) for t in templates]
    }


# ===== 通知偏好设置 =====

@router.get("/my/preference", summary="获取我的通知偏好设置")
async def get_my_preference(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取当前用户的通知偏好设置"""
    service = NotificationPreferenceService(db)
    preference = service.get_user_preference(current_user.id)

    return NotificationPreferenceResponse.model_validate(preference)


@router.put("/my/preference", summary="更新通知偏好设置")
async def update_preference(
    data: NotificationPreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新当前用户的通知偏好设置"""
    service = NotificationPreferenceService(db)
    preference = service.update_preference(current_user.id, data)

    return NotificationPreferenceResponse.model_validate(preference)
