"""
用户相关的 Pydantic 模型

@description 用户认证和信息的请求/响应模型
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.password import validate_password_strength
from app.core.sanitization import sanitize_string


# ============ 请求模型 ============

class RegisterRequest(BaseModel):
    """
    用户注册请求模型
    """
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=8, max_length=50, description="密码（至少8字符，包含大小写字母、数字和特殊字符）")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")

    @field_validator('username')
    @classmethod
    def sanitize_username(cls, v: str) -> str:
        """清理用户名，防止XSS"""
        return sanitize_string(v)

    @field_validator('full_name')
    @classmethod
    def sanitize_full_name(cls, v: Optional[str]) -> Optional[str]:
        """清理全名，防止XSS"""
        return sanitize_string(v) if v else v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """验证密码强度"""
        is_valid, errors = validate_password_strength(v)
        if not is_valid:
            raise ValueError('; '.join(errors))
        return v


class LoginRequest(BaseModel):
    """
    用户登录请求模型
    """
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")


class RefreshTokenRequest(BaseModel):
    """
    刷新Token请求模型
    """
    refresh_token: str = Field(..., description="刷新令牌")


class ChangePasswordRequest(BaseModel):
    """
    修改密码请求模型
    """
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=8, max_length=50, description="新密码（至少8字符，包含大小写字母、数字和特殊字符）")

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """验证新密码强度"""
        is_valid, errors = validate_password_strength(v)
        if not is_valid:
            raise ValueError('; '.join(errors))
        return v


class ForgotPasswordRequest(BaseModel):
    """
    忘记密码请求模型
    """
    email: EmailStr = Field(..., description="邮箱")


class ResetPasswordRequest(BaseModel):
    """
    重置密码请求模型
    """
    token: str = Field(..., description="重置令牌")
    new_password: str = Field(..., min_length=8, max_length=50, description="新密码（至少8字符，包含大小写字母、数字和特殊字符）")

    @field_validator('new_password')
    @classmethod
    def validate_reset_password(cls, v: str) -> str:
        """验证重置密码强度"""
        is_valid, errors = validate_password_strength(v)
        if not is_valid:
            raise ValueError('; '.join(errors))
        return v


# ============ 响应模型 ============

class UserBase(BaseModel):
    """
    用户基础信息模型
    """
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    is_superuser: bool
    last_login_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserResponse(UserBase):
    """
    用户信息响应模型
    """
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    """
    认证响应模型
    """
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")
    user: UserResponse = Field(..., description="用户信息")


# ============ 内部使用模型 ============

class UserCreate(BaseModel):
    """
    创建用户模型（内部使用）
    """
    username: str
    email: EmailStr
    password_hash: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False


class UserUpdate(BaseModel):
    """
    更新用户模型（内部使用）
    """
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None
    password_hash: Optional[str] = None

    @field_validator('full_name')
    @classmethod
    def sanitize_full_name(cls, v: Optional[str]) -> Optional[str]:
        """清理全名，防止XSS"""
        return sanitize_string(v) if v else v


class TokenPayload(BaseModel):
    """
    Token载荷模型
    """
    sub: str = Field(..., description="用户ID")
    exp: int = Field(..., description="过期时间")
    type: str = Field(..., description="Token类型")
