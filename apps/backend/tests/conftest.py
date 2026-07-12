"""
测试配置和共享fixtures

@description 提供测试所需的数据库、客户端和用户fixtures
"""

import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
import bcrypt
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models.user import User, UserSession
from app.models.rbac import Role, Permission, RolePermission, UserRole
from app.models.data_permission import DataPermission
from app.core.database import Base


# 测试数据库配置 - 使用内存SQLite数据库
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="session")
async def engine():
    """
    创建测试数据库引擎

    Yields:
        异步数据库引擎
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
    )

    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # 清理
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """
    创建数据库会话

    每个测试函数使用独立的会话，测试完成后自动回滚

    Args:
        engine: 数据库引擎

    Yields:
        异步数据库会话
    """
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with async_session() as session:
        # 确保数据库是干净的
        await session.execute(User.__table__.delete())
        await session.execute(UserSession.__table__.delete())
        await session.commit()

        yield session


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    创建测试客户端

    Args:
        db_session: 数据库会话

    Yields:
        异步HTTP客户端
    """
    from app.main import create_app

    app = create_app()

    # 重写数据库依赖
    async def override_get_db():
        yield db_session

    from app.api.deps import get_db
    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


def hash_password(password: str) -> str:
    """哈希密码"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session: AsyncSession) -> User:
    """
    创建测试用户

    Args:
        db_session: 数据库会话

    Returns:
        创建的测试用户
    """
    user = User(
        username="testuser",
        email="testuser@example.com",
        password_hash=hash_password("testpass123"),
        full_name="Test User",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def auth_headers(client: AsyncClient, test_user: User) -> dict:
    """
    获取认证头

    Args:
        client: 测试客户端
        test_user: 测试用户

    Returns:
        包含Authorization头的字典
    """
    response = await client.post(
        "/api/auth/login",
        json={
            "username": "testuser",
            "password": "testpass123",
        },
    )
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest_asyncio.fixture(scope="function")
async def admin_user(db_session: AsyncSession) -> User:
    """
    创建管理员测试用户

    Args:
        db_session: 数据库会话

    Returns:
        创建的管理员用户
    """
    user = User(
        username="admin",
        email="admin@example.com",
        password_hash=hash_password("admin123"),
        full_name="Admin User",
        is_active=True,
        is_superuser=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def admin_headers(client: AsyncClient, admin_user: User) -> dict:
    """
    获取管理员认证头

    Args:
        client: 测试客户端
        admin_user: 管理员用户

    Returns:
        包含管理员Authorization头的字典
    """
    response = await client.post(
        "/api/auth/login",
        json={
            "username": "admin",
            "password": "admin123",
        },
    )
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}
