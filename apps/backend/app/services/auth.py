"""
认证服务

@description 用户认证相关的业务逻辑

@features
- 用户注册
- 用户登录
- Token刷新
- 密码重置
- 会话管理
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from hashlib import sha256

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import BadRequestError, NotFoundError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User, UserSession, PasswordReset
from app.schemas.user import (
    AuthResponse,
    RegisterRequest,
    LoginRequest,
    RefreshTokenRequest,
    TokenPayload,
    UserResponse,
)


class AuthService:
    """
    认证服务类

    处理用户注册、登录、Token管理等认证相关业务
    """

    def __init__(self, db: AsyncSession):
        """
        初始化认证服务

        Args:
            db: 数据库会话
        """
        self.db = db

    async def register(self, request: RegisterRequest, ip_address: Optional[str] = None) -> AuthResponse:
        """
        用户注册

        Args:
            request: 注册请求数据
            ip_address: 客户端IP地址

        Returns:
            AuthResponse: 认证响应，包含Token和用户信息

        Raises:
            BadRequestError: 用户名或邮箱已存在
        """
        # 检查用户名是否已存在
        result = await self.db.execute(select(User).where(User.username == request.username))
        if result.scalar_one_or_none():
            raise BadRequestError("用户名已存在")

        # 检查邮箱是否已存在
        result = await self.db.execute(select(User).where(User.email == request.email))
        if result.scalar_one_or_none():
            raise BadRequestError("邮箱已被使用")

        # 创建用户
        user = User(
            username=request.username,
            email=request.email,
            password_hash=get_password_hash(request.password),
            full_name=request.full_name,
            phone=request.phone,
            is_active=True,
            is_superuser=False,
            last_login_ip=ip_address,
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        # 创建会话并生成Token
        return await self._create_session(user, ip_address=ip_address)

    async def login(self, request: LoginRequest, ip_address: Optional[str] = None) -> AuthResponse:
        """
        用户登录

        Args:
            request: 登录请求数据
            ip_address: 客户端IP地址

        Returns:
            AuthResponse: 认证响应，包含Token和用户信息

        Raises:
            UnauthorizedError: 用户名或密码错误
            BadRequestError: 用户已被禁用
        """
        # 查找用户（支持用户名或邮箱登录）
        result = await self.db.execute(
            select(User).where(
                (User.username == request.username) | (User.email == request.username)
            )
        )
        user = result.scalar_one_or_none()

        if not user:
            raise UnauthorizedError("用户名或密码错误")

        # 验证密码
        if not verify_password(request.password, user.password_hash):
            raise UnauthorizedError("用户名或密码错误")

        # 检查用户状态
        if not user.is_active:
            raise BadRequestError("用户已被禁用")

        # 更新最后登录信息
        user.last_login_at = datetime.now(timezone.utc)
        user.last_login_ip = ip_address

        await self.db.commit()

        # 创建会话并生成Token
        return await self._create_session(user, ip_address=ip_address)

    async def refresh_token(self, request: RefreshTokenRequest) -> AuthResponse:
        """
        刷新访问令牌

        Args:
            request: 包含刷新令牌的请求

        Returns:
            AuthResponse: 新的认证响应

        Raises:
            UnauthorizedError: 刷新令牌无效
        """
        # 解码刷新令牌
        try:
            payload = decode_token(request.refresh_token)
            token_data = TokenPayload(**payload)
        except Exception:
            raise UnauthorizedError("无效的刷新令牌")

        # 验证Token类型
        if token_data.type != "refresh":
            raise UnauthorizedError("Token类型错误")

        # 查找用户
        result = await self.db.execute(select(User).where(User.id == int(token_data.sub)))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise UnauthorizedError("用户不存在或已被禁用")

        # 创建新的会话和Token
        return await self._create_session(user)

    async def logout(self, access_token: str) -> None:
        """
        用户登出

        Args:
            access_token: 访问令牌

        Note:
            通过撤销会话来实现登出
        """
        token_hash = self._hash_token(access_token)

        result = await self.db.execute(
            select(UserSession).where(UserSession.token_hash == token_hash)
        )
        session = result.scalar_one_or_none()

        if session:
            session.is_revoked = True
            await self.db.commit()

    async def get_current_user(self, token: str) -> UserResponse:
        """
        获取当前用户信息

        Args:
            token: 访问令牌

        Returns:
            UserResponse: 用户信息

        Raises:
            UnauthorizedError: 令牌无效或用户不存在
        """
        # 解码令牌
        try:
            payload = decode_token(token)
            token_data = TokenPayload(**payload)
        except Exception:
            raise UnauthorizedError("无效的访问令牌")

        # 验证Token类型
        if token_data.type != "access":
            raise UnauthorizedError("Token类型错误")

        # 验证会话是否有效
        token_hash = self._hash_token(token)
        result = await self.db.execute(
            select(UserSession).where(
                UserSession.token_hash == token_hash,
                UserSession.is_revoked == False,
                UserSession.expires_at > datetime.now(timezone.utc)
            )
        )
        session = result.scalar_one_or_none()

        if not session:
            raise UnauthorizedError("会话已过期或已撤销")

        # 查找用户
        result = await self.db.execute(select(User).where(User.id == int(token_data.sub)))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise UnauthorizedError("用户不存在或已被禁用")

        return UserResponse.model_validate(user)

    async def forgot_password(self, email: str) -> str | None:
        """
        忘记密码

        Args:
            email: 用户邮箱

        Returns:
            str | None: 重置令牌（用于发送邮件），如果用户不存在返回 None

        Note:
            实际项目中应该发送邮件，这里返回令牌用于测试
        """
        import asyncio
        import random

        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            # 为了安全，即使用户不存在也返回成功
            # 添加随机延迟以防止通过时间差枚举邮箱
            delay = random.uniform(0.1, 0.3)
            await asyncio.sleep(delay)
            return None

        # 创建密码重置令牌
        import secrets

        reset_token = secrets.token_urlsafe(32)
        token_hash = self._hash_token(reset_token)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

        password_reset = PasswordReset(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        self.db.add(password_reset)
        await self.db.commit()

        # 添加随机延迟以防止通过时间差枚举邮箱
        delay = random.uniform(0.1, 0.3)
        await asyncio.sleep(delay)

        # TODO: 发送邮件
        # send_password_reset_email(user.email, reset_token)

        # 返回原始令牌（用于邮件发送）
        return reset_token

    async def reset_password(self, token: str, new_password: str) -> None:
        """
        重置密码

        Args:
            token: 重置令牌
            new_password: 新密码

        Raises:
            BadRequestError: 令牌无效或已过期
        """
        # 计算令牌哈希
        token_hash = self._hash_token(token)

        result = await self.db.execute(
            select(PasswordReset).where(
                PasswordReset.token_hash == token_hash,
                PasswordReset.is_used == False,
                PasswordReset.expires_at > datetime.now(timezone.utc)
            )
        )
        password_reset = result.scalar_one_or_none()

        if not password_reset:
            raise BadRequestError("重置令牌无效或已过期")

        # 更新用户密码
        user_result = await self.db.execute(select(User).where(User.id == password_reset.user_id))
        user = user_result.scalar_one()

        user.password_hash = get_password_hash(new_password)

        # 标记令牌已使用
        password_reset.is_used = True
        password_reset.used_at = datetime.now(timezone.utc)

        # 撤销所有会话（使用 UPDATE 语句）
        from sqlalchemy import update
        await self.db.execute(
            update(UserSession)
            .where(UserSession.user_id == user.id)
            .values(is_revoked=True)
        )

        await self.db.commit()

    async def _create_session(
        self,
        user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuthResponse:
        """
        创建用户会话并生成Token

        Args:
            user: 用户对象
            ip_address: 客户端IP地址
            user_agent: 用户代理

        Returns:
            AuthResponse: 认证响应
        """
        # 生成Token
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        # 计算过期时间
        access_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        # 创建会话
        session = UserSession(
            user_id=user.id,
            token_hash=self._hash_token(access_token),
            refresh_token_hash=self._hash_token(refresh_token),
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=expires_at,
            is_revoked=False,
        )

        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(user)

        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=int(access_expires.total_seconds()),
            user=UserResponse.model_validate(user),
        )

    @staticmethod
    def _hash_token(token: str) -> str:
        """
        哈希Token

        Args:
            token: 原始Token

        Returns:
            str: 哈希后的Token
        """
        return sha256(token.encode()).hexdigest()
