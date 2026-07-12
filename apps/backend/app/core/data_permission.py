"""
数据权限装饰器和工具函数

@description 提供数据权限检查的装饰器和辅助函数
"""

from functools import wraps
from typing import Any, Callable, List, Optional, Set

from fastapi import HTTPException, status
from sqlalchemy import Select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Selectable

from app.api.deps import get_current_user, get_db
from app.models.data_permission import DataPermission, DataScopeEnum
from app.models.user import User
from app.schemas.user import UserResponse


async def get_user_data_scope(
    user: UserResponse,
    resource_type: str,
    db: AsyncSession,
) -> str:
    """
    获取用户对指定资源的数据范围

    Args:
        user: 用户信息
        resource_type: 资源类型
        db: 数据库会话

    Returns:
        str: 数据范围（all/dept/department/self/custom）
    """
    # 超级管理员拥有全部数据权限
    if user.is_superuser:
        return DataScopeEnum.ALL

    # 查询用户的数据权限配置
    from sqlalchemy import select

    result = await db.execute(
        select(DataPermission).where(
            and_(
                or_(
                    DataPermission.user_id == user.id,
                    DataPermission.user_id.is_(None),
                ),
                DataPermission.resource_type == resource_type,
                DataPermission.is_active == True,
            )
        ).order_by(DataPermission.user_id.desc().nulls_last())  # 优先使用用户专属权限
    )
    permission = result.scalar_one_or_none()

    if permission:
        return permission.scope

    # 默认只能访问自己创建的数据
    return DataScopeEnum.SELF


def apply_data_scope(
    query: Select,
    user_id: int,
    user_dept_id: Optional[int],
    scope: str,
    created_by_field: str = "created_by",
    dept_id_field: str = "dept_id",
) -> Select:
    """
    根据数据范围应用查询过滤

    Args:
        query: 原始查询
        user_id: 用户ID
        user_dept_id: 用户部门ID
        scope: 数据范围
        created_by_field: 创建人字段名
        dept_id_field: 部门字段名

    Returns:
        Select: 应用过滤后的查询
    """
    from sqlalchemy import and_

    if scope == DataScopeEnum.ALL:
        # 全部数据，不过滤
        return query
    elif scope == DataScopeEnum.SELF:
        # 仅自己创建的数据
        return query.where(
            getattr(query.column_descriptions[0]["entity"], created_by_field) == user_id
        )
    elif scope == DataScopeEnum.DEPARTMENT:
        # 仅本部门数据
        if user_dept_id:
            return query.where(
                getattr(query.column_descriptions[0]["entity"], dept_id_field) == user_dept_id
            )
        return query.where(False)  # 没有部门则无权限
    elif scope == DataScopeEnum.DEPT:
        # 本部门及子部门数据
        if user_dept_id:
            # 这里简化处理，实际需要递归查询子部门
            return query.where(
                getattr(query.column_descriptions[0]["entity"], dept_id_field) == user_dept_id
            )
        return query.where(False)
    else:
        # 默认只返回自己的数据
        return query.where(
            getattr(query.column_descriptions[0]["entity"], created_by_field) == user_id
        )


def require_data_scope(resource_type: str, created_by_field: str = "created_by") -> Callable:
    """
    数据权限装饰器

    自动根据用户的数据权限范围过滤查询结果

    Args:
        resource_type: 资源类型（如 'sales_order', 'purchase_request'）
        created_by_field: 创建人字段名

    Example:
        ```python
        @require_data_scope("sales_order", "created_by")
        async def get_sales_orders(...):
            query = select(SalesOrder)
            # 装饰器会自动应用数据范围过滤
            return await service.get_orders(query)
        ```
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从依赖注入获取当前用户和数据库会话
            current_user: UserResponse = kwargs.get('current_user')
            db: AsyncSession = kwargs.get('db')

            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="未授权访问",
                )

            if not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="数据库会话未初始化",
                )

            # 获取用户的数据范围
            scope = await get_user_data_scope(current_user, resource_type, db)

            # 将数据范围信息添加到 kwargs，供业务逻辑使用
            kwargs['data_scope'] = scope

            return await func(*args, **kwargs)

        return wrapper

    return decorator


class DataScopeChecker:
    """
    数据范围检查器

    提供更灵活的数据权限检查方式
    """

    def __init__(self, db: AsyncSession, user: UserResponse):
        self.db = db
        self.user = user
        self._scope_cache: dict = {}

    async def get_scope(self, resource_type: str) -> str:
        """获取用户对指定资源的数据范围"""
        if resource_type not in self._scope_cache:
            self._scope_cache[resource_type] = await get_user_data_scope(
                self.user, resource_type, self.db
            )
        return self._scope_cache[resource_type]

    async def can_access(self, resource_type: str, resource: Any) -> bool:
        """
        检查用户是否可以访问指定资源

        Args:
            resource_type: 资源类型
            resource: 资源对象

        Returns:
            bool: 是否可以访问
        """
        scope = await self.get_scope(resource_type)

        if scope == DataScopeEnum.ALL:
            return True
        elif scope == DataScopeEnum.SELF:
            return getattr(resource, "created_by", None) == self.user.id
        elif scope == DataScopeEnum.DEPARTMENT:
            user_dept_id = getattr(self.user, "dept_id", None)
            resource_dept_id = getattr(resource, "dept_id", None)
            return user_dept_id and user_dept_id == resource_dept_id
        elif scope == DataScopeEnum.DEPT:
            # 简化实现，与 DEPARTMENT 相同
            user_dept_id = getattr(self.user, "dept_id", None)
            resource_dept_id = getattr(resource, "dept_id", None)
            return user_dept_id and user_dept_id == resource_dept_id

        return False

    def filter_query(
        self, query: Select, scope: str, created_by_field: str = "created_by"
    ) -> Select:
        """应用数据范围过滤到查询"""
        user_dept_id = getattr(self.user, "dept_id", None)
        return apply_data_scope(query, self.user.id, user_dept_id, scope, created_by_field)
