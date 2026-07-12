"""
权限装饰器和工具函数

@description 提供权限检查的装饰器和工具函数

@features
- require_permission 装饰器
- require_role 装饰器
- Redis/内存 权限缓存
"""

from functools import wraps
from typing import Callable, List, Optional, Set

from fastapi import Depends, HTTPException, status

from app.api.deps import get_current_user, get_db
from app.services.rbac import UserRoleService
from app.schemas.user import UserResponse
from app.schemas.rbac import PermissionResponse
from sqlalchemy.ext.asyncio import AsyncSession

# 导入 Redis 缓存模块
from app.core.redis_cache import (
    get_cached_permissions,
    set_cached_permissions,
    clear_permission_cache as redis_clear_cache,
)


def clear_permission_cache(user_id: int) -> None:
    """
    清除用户权限缓存（同步接口，兼容旧代码）

    Args:
        user_id: 用户ID
    """
    import asyncio
    # 在同步上下文中运行异步函数
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # 如果事件循环正在运行，创建任务
            asyncio.create_task(redis_clear_cache(user_id))
        else:
            # 如果没有事件循环，运行异步函数
            loop.run_until_complete(redis_clear_cache(user_id))
    except RuntimeError:
        # 如果没有事件循环，创建新的
        asyncio.run(redis_clear_cache(user_id))


async def clear_permission_cache_async(user_id: int) -> None:
    """
    清除用户权限缓存（异步接口）

    Args:
        user_id: 用户ID
    """
    await redis_clear_cache(user_id)


async def get_user_permissions(
    user: UserResponse,
    db: AsyncSession,
    use_cache: bool = True,
) -> Set[str]:
    """
    获取用户权限（带缓存）

    Args:
        user: 用户信息
        db: 数据库会话
        use_cache: 是否使用缓存，默认 True

    Returns:
        Set[str]: 权限编码集合
    """
    # 检查 Redis 缓存
    if use_cache:
        cached = await get_cached_permissions(user.id)
        if cached is not None:
            return cached

    # 从数据库获取
    service = UserRoleService(db)
    permissions = await service.get_user_permissions(user.id)

    # 缓存权限（TTL 1小时）
    if use_cache:
        await set_cached_permissions(user.id, permissions, ttl=3600)

    return permissions


def require_permission(*permissions: str) -> Callable:
    """
    权限检查装饰器

    Args:
        *permissions: 需要的权限编码（满足其中一个即可）

    Returns:
        装饰器函数

    Example:
        ```python
        @require_permission("user.create", "user.update")
        async def create_user(...):
            ...
        ```
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从依赖注入获取当前用户
            current_user: UserResponse = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="未授权访问",
                )

            # 超级管理员直接通过
            if current_user.is_superuser:
                return await func(*args, **kwargs)

            # 获取数据库会话
            db: AsyncSession = kwargs.get('db')
            if not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="数据库会话未初始化",
                )

            # 获取用户权限
            user_permissions = await get_user_permissions(current_user, db)

            # 检查是否拥有所需权限
            if not any(perm in user_permissions for perm in permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"需要权限: {'或'.join(permissions)}",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def require_role(*roles: str) -> Callable:
    """
    角色检查装饰器

    Args:
        *roles: 需要的角色编码（满足其中一个即可）

    Returns:
        装饰器函数

    Example:
        ```python
        @require_role("admin", "manager")
        async def admin_function(...):
            ...
        ```
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从依赖注入获取当前用户
            current_user: UserResponse = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="未授权访问",
                )

            # 超级管理员直接通过
            if current_user.is_superuser:
                return await func(*args, **kwargs)

            # 获取数据库会话
            db: AsyncSession = kwargs.get('db')
            if not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="数据库会话未初始化",
                )

            # 获取用户角色
            service = UserRoleService(db)
            user_roles = await service.get_user_roles(current_user.id)
            user_role_codes = {role.code for role in user_roles}

            # 检查是否拥有所需角色
            if not any(role in user_role_codes for role in roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"需要角色: {'或'.join(roles)}",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def require_superuser(func: Callable) -> Callable:
    """
    超级管理员检查装饰器

    Args:
        func: 要装饰的函数

    Returns:
        装饰后的函数

    Example:
        ```python
        @require_superuser
        async def system_config(...):
            ...
        ```
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        # 从依赖注入获取当前用户
        current_user: UserResponse = kwargs.get('current_user')
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="未授权访问",
            )

        # 检查是否为超级管理员
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要超级管理员权限",
            )

        return await func(*args, **kwargs)

    return wrapper
