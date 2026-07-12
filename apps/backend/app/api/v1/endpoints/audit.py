"""
审计日志API端点
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.core.permissions import require_permission
from app.core.audit import get_request_context
from app.models.user import User
from app.schemas.audit import (
    AuditLogResponse,
    AuditLogDetailResponse,
    AuditLogQuery,
    AuditLogStatistics,
)
from app.services.audit import AuditService

router = APIRouter(prefix="/audit", tags=["审计日志"])


@router.get("/logs", summary="获取审计日志列表")
@require_permission("audit.log.read")
async def get_audit_logs(
    request: Request,
    action_type: Optional[str] = Query(None, description="操作类型"),
    module: Optional[str] = Query(None, description="模块名称"),
    entity_type: Optional[str] = Query(None, description="实体类型"),
    entity_id: Optional[int] = Query(None, description="实体ID"),
    user_id: Optional[int] = Query(None, description="用户ID"),
    username: Optional[str] = Query(None, description="用户名"),
    level: Optional[str] = Query(None, description="日志级别"),
    status: Optional[str] = Query(None, description="操作状态"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    keyword: Optional[str] = Query(None, description="关键词"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取审计日志列表

    支持多种筛选条件和分页
    """
    service = AuditService(db)

    # 构建查询参数
    query = AuditLogQuery(
        action_type=action_type,
        module=module,
        entity_type=entity_type,
        entity_id=entity_id,
        user_id=user_id,
        username=username,
        level=level,
        status=status,
        start_date=start_date,
        end_date=end_date,
        keyword=keyword,
        page=page,
        page_size=page_size,
    )

    logs, total = service.get_audit_logs(query)

    return {
        "items": [AuditLogResponse.model_validate(log) for log in logs],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/logs/{log_id}", summary="获取审计日志详情")
@require_permission("audit.log.read")
async def get_audit_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取审计日志详情（含字段级别变更明细）
    """
    service = AuditService(db)
    result = service.get_audit_log_with_details(log_id)

    if not result:
        raise HTTPException(status_code=404, detail="审计日志不存在")

    return result


@router.get("/entities/{entity_type}/{entity_id}/history", summary="获取实体变更历史")
@require_permission("audit.log.read")
async def get_entity_history(
    entity_type: str,
    entity_id: int,
    limit: int = Query(50, ge=1, le=200, description="返回数量限制"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取指定实体的完整变更历史
    """
    service = AuditService(db)
    history = service.get_entity_history(entity_type, entity_id, limit)

    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "history": [AuditLogResponse.model_validate(log) for log in history],
    }


@router.get("/users/{user_id}/activity", summary="获取用户活动记录")
@require_permission("audit.log.read")
async def get_user_activity(
    user_id: int,
    days: int = Query(30, ge=1, le=365, description="查询天数"),
    limit: int = Query(100, ge=1, le=500, description="返回数量限制"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取指定用户的活动记录
    """
    service = AuditService(db)
    activity = service.get_user_activity(user_id, days, limit)

    return {
        "user_id": user_id,
        "days": days,
        "activity": [AuditLogResponse.model_validate(log) for log in activity],
    }


@router.get("/statistics", summary="获取审计日志统计")
@require_permission("audit.log.read")
async def get_audit_statistics(
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取审计日志统计数据

    包括：总数、操作类型分布、模块分布、每日统计等
    """
    service = AuditService(db)
    stats = service.get_statistics(start_date, end_date)

    return stats


@router.get("/modules", summary="获取所有模块列表")
@require_permission("audit.log.read")
async def get_modules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取所有有审计日志的模块列表
    """
    service = AuditService(db)
    modules = service.get_modules()

    return {"modules": [m[0] for m in modules]}
