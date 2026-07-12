"""
审计日志装饰器和工具函数

@description 提供审计日志记录的装饰器和工具函数
"""

from functools import wraps
from typing import Optional, Any, Callable, List
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import Request
from contextlib import contextmanager

from app.models.audit import AuditLog, AuditLogDetail, AuditActionType, AuditLogLevel


class AuditContext:
    """审计上下文，存储当前请求的审计信息"""

    def __init__(
        self,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_method: Optional[str] = None,
        request_url: Optional[str] = None,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ):
        self.user_id = user_id
        self.username = username
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.request_method = request_method
        self.request_url = request_url
        self.request_id = request_id
        self.session_id = session_id


class AuditLogger:
    """审计日志记录器"""

    def __init__(self, db: Session):
        self.db = db

    def log(
        self,
        action_type: AuditActionType,
        module: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        entity_name: Optional[str] = None,
        old_value: Optional[dict] = None,
        new_value: Optional[dict] = None,
        changes: Optional[list] = None,
        description: Optional[str] = None,
        level: AuditLogLevel = AuditLogLevel.INFO,
        status: str = "success",
        error_message: Optional[str] = None,
        context: Optional[AuditContext] = None,
    ) -> AuditLog:
        """
        记录审计日志

        Args:
            action_type: 操作类型
            module: 模块名称
            entity_type: 实体类型
            entity_id: 实体ID
            entity_name: 实体名称
            old_value: 变更前的值
            new_value: 变更后的值
            changes: 变更字段列表
            description: 操作描述
            level: 日志级别
            status: 操作状态
            error_message: 错误信息
            context: 审计上下文

        Returns:
            AuditLog: 创建的审计日志对象
        """
        audit_log = AuditLog(
            action_type=action_type,
            module=module,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_name=entity_name,
            old_value=old_value,
            new_value=new_value,
            changes=changes,
            description=description,
            level=level,
            status=status,
            error_message=error_message,
            created_at=datetime.now(),
        )

        # 从上下文填充信息
        if context:
            audit_log.user_id = context.user_id
            audit_log.username = context.username
            audit_log.ip_address = context.ip_address
            audit_log.user_agent = context.user_agent
            audit_log.request_method = context.request_method
            audit_log.request_url = context.request_url
            audit_log.request_id = context.request_id
            audit_log.session_id = context.session_id

        self.db.add(audit_log)
        self.db.flush()  # 获取ID，但不提交

        return audit_log

    def log_details(
        self,
        audit_log_id: int,
        field_name: str,
        field_label: Optional[str] = None,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None,
        value_type: str = "string",
    ):
        """
        记录审计日志明细

        Args:
            audit_log_id: 审计日志ID
            field_name: 字段名称
            field_label: 字段显示名称
            old_value: 旧值
            new_value: 新值
            value_type: 值类型
        """
        detail = AuditLogDetail(
            audit_log_id=audit_log_id,
            field_name=field_name,
            field_label=field_label,
            old_value=old_value,
            new_value=new_value,
            value_type=value_type,
        )
        self.db.add(detail)

    def log_with_details(
        self,
        action_type: AuditActionType,
        module: str,
        changes_dict: dict,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        entity_name: Optional[str] = None,
        old_value: Optional[dict] = None,
        new_value: Optional[dict] = None,
        description: Optional[str] = None,
        level: AuditLogLevel = AuditLogLevel.INFO,
        status: str = "success",
        error_message: Optional[str] = None,
        context: Optional[AuditContext] = None,
    ) -> AuditLog:
        """
        记录审计日志（含明细）

        Args:
            action_type: 操作类型
            module: 模块名称
            changes_dict: 变更字典 {field_name: {"label": "显示名称", "old": "旧值", "new": "新值"}}
            entity_type: 实体类型
            entity_id: 实体ID
            entity_name: 实体名称
            old_value: 变更前的值
            new_value: 变更后的值
            description: 操作描述
            level: 日志级别
            status: 操作状态
            error_message: 错误信息
            context: 审计上下文

        Returns:
            AuditLog: 创建的审计日志对象
        """
        # 创建主日志
        audit_log = self.log(
            action_type=action_type,
            module=module,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_name=entity_name,
            old_value=old_value,
            new_value=new_value,
            changes=list(changes_dict.keys()),
            description=description,
            level=level,
            status=status,
            error_message=error_message,
            context=context,
        )

        # 创建明细
        for field_name, change_info in changes_dict.items():
            field_label = change_info.get("label", field_name)
            old_val = change_info.get("old")
            new_val = change_info.get("new")

            # 确定值类型
            value_type = "string"
            if old_val is not None or new_val is not None:
                if isinstance(old_val, (int, float)) or isinstance(new_val, (int, float)):
                    value_type = "number"
                elif isinstance(old_val, dict) or isinstance(new_val, dict):
                    value_type = "json"

            self.log_details(
                audit_log_id=audit_log.id,
                field_name=field_name,
                field_label=field_label,
                old_value=str(old_val) if old_val is not None else None,
                new_value=str(new_val) if new_val is not None else None,
                value_type=value_type,
            )

        return audit_log


def audit_log(
    action_type: AuditActionType,
    module: str,
    entity_type_arg: str = "entity_type",
    entity_id_arg: str = "entity_id",
    entity_name_arg: str = "entity_name",
    description: Optional[str] = None,
    log_level: AuditLogLevel = AuditLogLevel.INFO,
):
    """
    审计日志装饰器

    Args:
        action_type: 操作类型
        module: 模块名称
        entity_type_arg: 实体类型参数名
        entity_id_arg: 实体ID参数名
        entity_name_arg: 实体名称参数名
        description: 操作描述
        log_level: 日志级别

    Usage:
        @audit_log(
            action_type=AuditActionType.UPDATE,
            module="sales",
            entity_type_arg="order_type",
            entity_id_arg="order_id",
        )
        async def update_sales_order(order_id: int, order_type: str, ...):
            ...
    """

    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # 获取审计上下文（从kwargs中传入）
            audit_context = kwargs.pop("_audit_context", None)
            db = kwargs.get("_db", None)

            if not audit_context or not db:
                # 没有审计上下文或数据库会话，直接执行函数
                return await func(*args, **kwargs)

            # 提取实体信息
            entity_type = kwargs.get(entity_type_arg)
            entity_id = kwargs.get(entity_id_arg)
            entity_name = kwargs.get(entity_name_arg)

            # 执行函数
            try:
                result = await func(*args, **kwargs)

                # 记录成功日志
                logger = AuditLogger(db)
                logger.log(
                    action_type=action_type,
                    module=module,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    entity_name=entity_name,
                    description=description,
                    level=log_level,
                    status="success",
                    context=audit_context,
                )

                return result

            except Exception as e:
                # 记录失败日志
                logger = AuditLogger(db)
                logger.log(
                    action_type=action_type,
                    module=module,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    entity_name=entity_name,
                    description=description,
                    level=AuditLogLevel.ERROR,
                    status="failed",
                    error_message=str(e),
                    context=audit_context,
                )
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 同步函数版本
            audit_context = kwargs.pop("_audit_context", None)
            db = kwargs.get("_db", None)

            if not audit_context or not db:
                return func(*args, **kwargs)

            entity_type = kwargs.get(entity_type_arg)
            entity_id = kwargs.get(entity_id_arg)
            entity_name = kwargs.get(entity_name_arg)

            try:
                result = func(*args, **kwargs)

                logger = AuditLogger(db)
                logger.log(
                    action_type=action_type,
                    module=module,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    entity_name=entity_name,
                    description=description,
                    level=log_level,
                    status="success",
                    context=audit_context,
                )

                return result

            except Exception as e:
                logger = AuditLogger(db)
                logger.log(
                    action_type=action_type,
                    module=module,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    entity_name=entity_name,
                    description=description,
                    level=AuditLogLevel.ERROR,
                    status="failed",
                    error_message=str(e),
                    context=audit_context,
                )
                raise

        # 根据函数类型返回对应的wrapper
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def get_request_context(request: Request) -> AuditContext:
    """
    从FastAPI请求中提取审计上下文

    Args:
        request: FastAPI请求对象

    Returns:
        AuditContext: 审计上下文
    """
    # 获取用户信息（从JWT token或其他方式）
    user = getattr(request.state, "user", None)
    user_id = user.id if user else None
    username = user.username if user else None

    # 获取请求信息
    client_host = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    request_method = request.method
    request_url = str(request.url)

    # 生成请求ID
    request_id = request.headers.get("x-request-id")

    # 获取会话ID
    session_id = request.headers.get("authorization", "")[:50]  # 简化处理

    return AuditContext(
        user_id=user_id,
        username=username,
        ip_address=client_host,
        user_agent=user_agent,
        request_method=request_method,
        request_url=request_url,
        request_id=request_id,
        session_id=session_id,
    )


@contextmanager
def audit_scope(db: Session, context: AuditContext):
    """
    审计作用域，用于在一段代码中自动记录审计日志

    Args:
        db: 数据库会话
        context: 审计上下文

    Usage:
        with audit_scope(db, context) as logger:
            logger.log(...)
    """
    logger = AuditLogger(db)
    try:
        yield logger
    finally:
        pass
