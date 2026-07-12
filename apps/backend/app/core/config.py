"""
应用配置模块

@description 使用 pydantic-settings 管理应用配置

@features
- 环境变量自动加载
- 类型验证
- 默认值设置
"""

import secrets
from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    应用配置类

    从环境变量加载配置，提供类型安全的配置访问
    """

    # API配置
    PROJECT_NAME: str = Field(default="ERP System", description="项目名称")
    API_HOST: str = Field(default="0.0.0.0", description="API服务地址")
    API_PORT: int = Field(default=8000, description="API服务端口")
    DEBUG: bool = Field(default=False, description="调试模式")

    # 数据库配置 (SQLite)
    DB_PATH: str = Field(default="./erp_system.db", description="SQLite数据库文件路径")

    # JWT配置
    # 注意: 生产环境必须设置强随机密钥，建议使用 openssl rand -hex 32 生成
    JWT_SECRET_KEY: str = Field(
        default="",
        description="JWT密钥（生产环境必须通过环境变量设置，默认值仅用于开发）"
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT算法")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15, description="访问令牌过期时间（分钟）")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="刷新令牌过期时间（天）")

    # CORS配置
    # 生产环境必须通过环境变量显式配置允许的域名
    # 使用字符串类型以支持逗号分隔的配置
    CORS_ORIGINS: str = Field(
        default="",  # 默认为空字符串
        description="允许的跨域来源（生产环境必须通过环境变量设置，用逗号分隔多个域名）"
    )

    # 文件存储配置
    UPLOAD_DIR: str = Field(default="./uploads", description="文件上传目录")
    MAX_UPLOAD_SIZE: int = Field(default=10 * 1024 * 1024, description="最大上传大小（字节）")

    # 分页配置
    DEFAULT_PAGE_SIZE: int = Field(default=10, description="默认分页大小")
    MAX_PAGE_SIZE: int = Field(default=100, description="最大分页大小")

    # Redis配置
    REDIS_URL: str = Field(default="", description="Redis连接URL（如 redis://localhost:6379/0）")
    REDIS_CACHE_TTL: int = Field(default=3600, description="Redis缓存过期时间（秒），默认1小时")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator('JWT_SECRET_KEY')
    @classmethod
    def validate_jwt_secret_key(cls, v):
        """
        验证 JWT 密钥

        在生产环境中必须设置强随机密钥
        """
        if not v or v == "":
            raise ValueError(
                "JWT_SECRET_KEY cannot be empty. "
                "请在 .env 文件中设置 JWT_SECRET_KEY 环境变量，"
                "或使用以下命令生成: openssl rand -hex 32"
            )
        if len(v) < 32:
            raise ValueError(
                f"JWT_SECRET_KEY 长度不足 (当前: {len(v)} 字符)。 "
                "建议使用至少 32 字符的强随机密钥。"
            )
        return v

    @field_validator('CORS_ORIGINS', mode='after')
    @classmethod
    def validate_cors_origins(cls, v: str) -> str:
        """
        验证 CORS 配置

        接受逗号分隔的字符串，验证格式后返回
        """
        if not v or not v.strip():
            return v

        # 验证格式：应该是逗号分隔的 URL
        origins = [o.strip() for o in v.split(',') if o.strip()]
        for origin in origins:
            if not origin.startswith(('http://', 'https://')):
                raise ValueError(
                    f'CORS origin must start with http:// or https://, got: {origin}'
                )
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        """
        获取 CORS 配置为列表格式
        """
        if not self.CORS_ORIGINS or not self.CORS_ORIGINS.strip():
            return []
        return [o.strip() for o in self.CORS_ORIGINS.split(',') if o.strip()]

    @property
    def database_url(self) -> str:
        """获取数据库连接URL (SQLite)"""
        return f"sqlite+aiosqlite:///{self.DB_PATH}"


@lru_cache()
def get_settings() -> Settings:
    """
    获取配置单例

    Returns:
        Settings: 配置实例
    """
    return Settings()


# 导出配置实例
settings = get_settings()
