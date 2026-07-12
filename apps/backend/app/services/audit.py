"""
审计日志服务
"""

from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from sqlalchemy import and_, or_, func, desc
from sqlalchemy.orm import Session

from app.models.audit import AuditLog, AuditLogDetail, AuditActionType, AuditLogLevel
from app.schemas.audit import (
    AuditLogQuery,
    AuditLogResponse,
    AuditLogDetailResponse,
    AuditLogExportRequest,
    AuditLogStatistics,
)


class AuditService:
    """审计日志服务"""

    def __init__(self, db: Session):
        self.db = db

    def get_audit_logs(
        self,
        query: AuditLogQuery,
    ) -> Tuple[List[AuditLog], int]:
        """
        获取审计日志列表

        Args:
            query: 查询参数

        Returns:
            Tuple[List[AuditLog], int]: (日志列表, 总数)
        """
        # 构建查询
        q = self.db.query(AuditLog)

        # 筛选条件
        if query.action_type:
            q = q.filter(AuditLog.action_type == query.action_type.value)
        if query.module:
            q = q.filter(AuditLog.module == query.module)
        if query.entity_type:
            q = q.filter(AuditLog.entity_type == query.entity_type)
        if query.entity_id:
            q = q.filter(AuditLog.entity_id == query.entity_id)
        if query.user_id:
            q = q.filter(AuditLog.user_id == query.user_id)
        if query.username:
            q = q.filter(AuditLog.username.like(f"%{query.username}%"))
        if query.level:
            q = q.filter(AuditLog.level == query.level.value)
        if query.status:
            q = q.filter(AuditLog.status == query.status)
        if query.start_date:
            q = q.filter(AuditLog.created_at >= query.start_date)
        if query.end_date:
            q = q.filter(AuditLog.created_at <= query.end_date)
        if query.keyword:
            q = q.filter(
                or_(
                    AuditLog.description.like(f"%{query.keyword}%"),
                    AuditLog.entity_name.like(f"%{query.keyword}%"),
                )
            )

        # 获取总数
        total = q.count()

        # 分页和排序
        logs = (
            q.order_by(desc(AuditLog.created_at))
            .offset((query.page - 1) * query.page_size)
            .limit(query.page_size)
            .all()
        )

        return logs, total

    def get_audit_log(self, log_id: int) -> Optional[AuditLog]:
        """
        获取审计日志详情

        Args:
            log_id: 日志ID

        Returns:
            Optional[AuditLog]: 审计日志对象
        """
        return self.db.query(AuditLog).filter(AuditLog.id == log_id).first()

    def get_audit_log_with_details(self, log_id: int) -> Optional[dict]:
        """
        获取审计日志详情（含明细）

        Args:
            log_id: 日志ID

        Returns:
            Optional[dict]: 包含明细的审计日志
        """
        log = self.get_audit_log(log_id)
        if not log:
            return None

        details = (
            self.db.query(AuditLogDetail)
            .filter(AuditLogDetail.audit_log_id == log_id)
            .all()
        )

        return {
            "audit_log": AuditLogResponse.model_validate(log),
            "details": [AuditLogDetailResponse.model_validate(d) for d in details],
        }

    def get_entity_history(
        self,
        entity_type: str,
        entity_id: int,
        limit: int = 50,
    ) -> List[AuditLog]:
        """
        获取实体的变更历史

        Args:
            entity_type: 实体类型
            entity_id: 实体ID
            limit: 返回数量限制

        Returns:
            List[AuditLog]: 变更历史列表
        """
        return (
            self.db.query(AuditLog)
            .filter(
                and_(
                    AuditLog.entity_type == entity_type,
                    AuditLog.entity_id == entity_id,
                )
            )
            .order_by(desc(AuditLog.created_at))
            .limit(limit)
            .all()
        )

    def get_user_activity(
        self,
        user_id: int,
        days: int = 30,
        limit: int = 100,
    ) -> List[AuditLog]:
        """
        获取用户活动记录

        Args:
            user_id: 用户ID
            days: 查询天数
            limit: 返回数量限制

        Returns:
            List[AuditLog]: 活动记录列表
        """
        start_date = datetime.now() - timedelta(days=days)

        return (
            self.db.query(AuditLog)
            .filter(
                and_(
                    AuditLog.user_id == user_id,
                    AuditLog.created_at >= start_date,
                )
            )
            .order_by(desc(AuditLog.created_at))
            .limit(limit)
            .all()
        )

    def get_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> AuditLogStatistics:
        """
        获取审计日志统计

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            AuditLogStatistics: 统计数据
        """
        # 默认统计最近30天
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()

        # 基础查询
        q = self.db.query(AuditLog).filter(
            and_(
                AuditLog.created_at >= start_date,
                AuditLog.created_at <= end_date,
            )
        )

        # 总数
        total_count = q.count()

        # 按操作类型统计
        action_type_stats = (
            q.with_entities(AuditLog.action_type, func.count(AuditLog.id))
            .group_by(AuditLog.action_type)
            .all()
        )
        action_type_stats = {at: count for at, count in action_type_stats}

        # 按模块统计
        module_stats = (
            q.with_entities(AuditLog.module, func.count(AuditLog.id))
            .group_by(AuditLog.module)
            .all()
        )
        module_stats = {m: count for m, count in module_stats}

        # 按日期统计（每日）
        daily_stats = (
            q.with_entities(
                func.date(AuditLog.created_at).label("date"),
                func.count(AuditLog.id).label("count"),
            )
            .group_by(func.date(AuditLog.created_at))
            .all()
        )
        daily_stats = [{"date": str(d), "count": c} for d, c in daily_stats]

        # 错误和警告数
        error_count = (
            self.db.query(func.count(AuditLog.id))
            .filter(
                and_(
                    AuditLog.created_at >= start_date,
                    AuditLog.created_at <= end_date,
                    AuditLog.level == AuditLogLevel.ERROR,
                )
            )
            .scalar()
        )

        warning_count = (
            self.db.query(func.count(AuditLog.id))
            .filter(
                and_(
                    AuditLog.created_at >= start_date,
                    AuditLog.created_at <= end_date,
                    AuditLog.level == AuditLogLevel.WARNING,
                )
            )
            .scalar()
        )

        return AuditLogStatistics(
            total_count=total_count,
            action_type_stats=action_type_stats,
            module_stats=module_stats,
            daily_stats=daily_stats,
            error_count=error_count,
            warning_count=warning_count,
        )

    def get_modules(self) -> List[str]:
        """
        获取所有模块列表

        Returns:
            List[str]: 模块列表
        """
        return (
            self.db.query(AuditLog.module)
            .distinct()
            .order_by(AuditLog.module)
            .all()
        )

    def delete_old_logs(self, days: int = 90) -> int:
        """
        删除旧的审计日志

        Args:
            days: 保留天数

        Returns:
            int: 删除的数量
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        # 只删除INFO级别的日志，保留WARNING及以上级别
        delete_count = (
            self.db.query(AuditLog)
            .filter(
                and_(
                    AuditLog.created_at < cutoff_date,
                    AuditLog.level == AuditLogLevel.INFO,
                )
            )
            .delete()
        )

        self.db.commit()
        return delete_count
