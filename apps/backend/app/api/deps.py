"""
依赖注入模块

@description API路由的依赖函数，用于获取数据库会话、当前用户等
"""

import logging
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session, get_db as get_database
from app.core.exceptions import UnauthorizedError
from app.services.auth import AuthService
from app.schemas.user import UserResponse

logger = logging.getLogger(__name__)


# ============ 数据库依赖 ============

async def get_db() -> AsyncSession:
    """
    获取数据库会话

    Yields:
        AsyncSession: 数据库会话实例
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


# ============ 认证依赖 ============

security = HTTPBearer(auto_error=False)


async def get_current_user(
    authorization: Annotated[HTTPAuthorizationCredentials | None, Depends(security)] = None,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    获取当前登录用户

    Args:
        authorization: HTTP Bearer Token
        db: 数据库会话

    Returns:
        UserResponse: 当前用户信息

    Raises:
        HTTPException: 未授权时返回401
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证令牌",
        )

    try:
        auth_service = AuthService(db)
        return await auth_service.get_current_user(authorization.credentials)
    except UnauthorizedError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


async def get_current_user_optional(
    authorization: Annotated[HTTPAuthorizationCredentials | None, Depends(security)] = None,
    db: AsyncSession = Depends(get_db),
) -> UserResponse | None:
    """
    获取当前登录用户（可选）

    当没有提供Token时返回None，而不是抛出异常

    Args:
        authorization: HTTP Bearer Token（可选）
        db: 数据库会话

    Returns:
        UserResponse | None: 当前用户信息或None
    """
    if not authorization:
        return None

    try:
        auth_service = AuthService(db)
        return await auth_service.get_current_user(authorization.credentials)
    except Exception as e:
        logger.debug(f"Optional auth failed: {e}")
        return None


async def get_current_superuser(
    current_user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    """
    获取当前超级用户

    验证当前用户是否为超级管理员

    Args:
        current_user: 当前用户

    Returns:
        UserResponse: 当前用户信息

    Raises:
        HTTPException: 非超级管理员时返回403
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要超级管理员权限",
        )
    return current_user


# ============ 其他依赖 ============

async def get_client_ip(
    x_forwarded_for: Annotated[str | None, Header()] = None,
    x_real_ip: Annotated[str | None, Header()] = None,
) -> str | None:
    """
    获取客户端真实IP地址

    Args:
        x_forwarded_for: X-Forwarded-For 头
        x_real_ip: X-Real-IP 头

    Returns:
        str | None: 客户端IP地址
    """
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    if x_real_ip:
        return x_real_ip
    return None
