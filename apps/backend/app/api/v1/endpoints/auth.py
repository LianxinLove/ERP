"""
认证端点

@description 用户认证相关的API接口

@features
- 用户注册
- 用户登录
- Token刷新
- 登出
- 获取当前用户信息
- 忘记密码
- 重置密码
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status, Body
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.deps import get_db, get_current_user, get_client_ip
from app.schemas.user import (
    AuthResponse,
    UserResponse,
    RegisterRequest,
    LoginRequest,
    RefreshTokenRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from app.services.auth import AuthService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


# ============ 测试端点 ============

@router.get("/ping")
async def ping():
    """简单的ping测试"""
    return {"pong": True}


@router.get("/test")
async def test_endpoint():
    """测试端点"""
    from app.schemas.user import AuthResponse, UserResponse
    from datetime import datetime

    user_response = UserResponse(
        id=1,
        username='admin',
        email='admin@test.com',
        full_name='Test Admin',
        is_active=True,
        is_superuser=False,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    auth_response = AuthResponse(
        access_token='test_token',
        refresh_token='test_refresh',
        token_type='bearer',
        expires_in=3600,
        user=user_response
    )
    return auth_response


# ============ API端点 ============

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    reg_request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    用户注册

    创建新用户账户，返回访问令牌和刷新令牌

    Args:
        request: FastAPI 请求对象（用于速率限制）
        reg_request: 注册请求数据
        db: 数据库会话

    Returns:
        AuthResponse: 包含访问令牌、刷新令牌和用户信息

    Raises:
        400: 用户名或邮箱已存在
    """
    auth_service = AuthService(db)
    return await auth_service.register(reg_request, ip_address=None)


@router.post("/login", response_model=AuthResponse)
async def login(
    login_request: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    用户登录

    验证用户名和密码，返回访问令牌和刷新令牌

    Args:
        login_request: 登录请求数据
        request: FastAPI 请求对象（用于获取客户端IP）
        db: 数据库会话

    Returns:
        AuthResponse: 包含访问令牌、刷新令牌和用户信息

    Raises:
        401: 用户名或密码错误
        400: 用户已被禁用
    """
    # 获取客户端IP
    ip_address = request.client.host if request.client else None

    auth_service = AuthService(db)
    return await auth_service.login(login_request, ip_address=ip_address)


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    刷新访问令牌

    使用刷新令牌获取新的访问令牌

    Args:
        request: 包含刷新令牌的请求
        db: 数据库会话

    Returns:
        AuthResponse: 新的访问令牌、刷新令牌和用户信息

    Raises:
        401: 刷新令牌无效
    """
    auth_service = AuthService(db)
    return await auth_service.refresh_token(request)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    authorization: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())],
    db: AsyncSession = Depends(get_db),
):
    """
    用户登出

    撤销当前会话，使访问令牌失效

    Args:
        authorization: Bearer Token凭证
        db: 数据库会话
    """
    auth_service = AuthService(db)
    await auth_service.logout(authorization.credentials)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """
    获取当前用户信息

    返回当前登录用户的详细信息

    Args:
        current_user: 当前用户

    Returns:
        UserResponse: 当前用户信息
    """
    return current_user


@router.post("/forgot-password")
async def forgot_password(
    fp_request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    忘记密码

    发送密码重置邮件（实际项目中应发送邮件）

    Args:
        fp_request: 包含邮箱的请求
        db: 数据库会话

    Returns:
        dict: 成功消息
    """
    auth_service = AuthService(db)
    await auth_service.forgot_password(fp_request.email)

    return {"message": "如果该邮箱存在，重置邮件已发送"}


@router.post("/reset-password")
async def reset_password(
    rp_request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    重置密码

    使用重置令牌设置新密码

    Args:
        req: FastAPI 请求对象（用于速率限制）
        rp_request: 包含重置令牌和新密码的请求
        db: 数据库会话

    Returns:
        dict: 成功消息

    Raises:
        400: 令牌无效或已过期
    """
    auth_service = AuthService(db)
    await auth_service.reset_password(rp_request.token, rp_request.new_password)

    return {"message": "密码重置成功"}
