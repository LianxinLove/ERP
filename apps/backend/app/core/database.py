"""
数据库配置模块

@description SQLAlchemy数据库连接和会话管理

@features
- 异步数据库连接
- 会话管理
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import settings

# 创建异步引擎 (SQLite)
# 注意: SQLite 不支持连接池配置，使用简单模式
engine = create_async_engine(
    settings.database_url,
    echo=settings.DEBUG,
)

# 创建会话工厂
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# 创建基类
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    获取数据库会话

    Yields:
        AsyncSession: 数据库会话实例

    Note:
        使用依赖注入方式在API路由中使用
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """
    初始化数据库

    创建所有表结构（仅用于开发环境）

    Warning:
        生产环境应使用 Alembic 迁移
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
