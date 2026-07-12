"""
认证模块测试
@description 测试用户注册、登录、令牌刷新等功能
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestRegister:
    """用户注册测试"""

    async def test_register_success(self, client: AsyncClient):
        """测试成功注册"""
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "NewPass123!",
                "full_name": "New User",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data
        assert data["user"]["username"] == "newuser"
        assert data["user"]["email"] == "newuser@example.com"
        assert "id" in data["user"]
        assert "password" not in data["user"]

    async def test_register_duplicate_username(self, client: AsyncClient, test_user):
        """测试重复用户名注册"""
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "email": "another@example.com",
                "password": "NewPass123!",
                "full_name": "Another User",
            },
        )
        assert response.status_code == 400

    async def test_register_weak_password(self, client: AsyncClient):
        """测试弱密码注册"""
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "newuser2",
                "email": "newuser2@example.com",
                "password": "123",
                "full_name": "New User",
            },
        )
        assert response.status_code == 422


@pytest.mark.asyncio
class TestLogin:
    """用户登录测试"""

    async def test_login_success(self, client: AsyncClient, test_user):
        """测试成功登录"""
        response = await client.post(
            "/api/auth/login",
            json={
                "username": "testuser",
                "password": "testpass123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_invalid_credentials(self, client: AsyncClient):
        """测试无效凭证登录"""
        response = await client.post(
            "/api/auth/login",
            json={
                "username": "nonexistent",
                "password": "wrongpass",
            },
        )
        assert response.status_code == 401

    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        """测试错误密码登录"""
        response = await client.post(
            "/api/auth/login",
            json={
                "username": "testuser",
                "password": "wrongpass",
            },
        )
        assert response.status_code == 401


@pytest.mark.asyncio
class TestGetCurrentUser:
    """获取当前用户测试"""

    async def test_get_current_user_success(self, client: AsyncClient, auth_headers):
        """测试成功获取当前用户"""
        response = await client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert "email" in data

    async def test_get_current_user_no_token(self, client: AsyncClient):
        """测试无令牌获取当前用户"""
        response = await client.get("/api/auth/me")
        assert response.status_code == 401

    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """测试无效令牌获取当前用户"""
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401


@pytest.mark.asyncio
class TestTokenRefresh:
    """令牌刷新测试"""

    async def test_refresh_token_success(self, client: AsyncClient, test_user):
        """测试成功刷新令牌"""
        # 先登录获取令牌
        login_response = await client.post(
            "/api/auth/login",
            json={
                "username": "testuser",
                "password": "testpass123",
            },
        )
        tokens = login_response.json()
        refresh_token = tokens["refresh_token"]

        # 刷新令牌
        response = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_refresh_token_invalid(self, client: AsyncClient):
        """测试无效刷新令牌"""
        response = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )
        assert response.status_code == 401


@pytest.mark.asyncio
class TestLogout:
    """登出测试"""

    async def test_logout_success(self, client: AsyncClient, auth_headers):
        """测试成功登出"""
        response = await client.post("/api/auth/logout", headers=auth_headers)
        assert response.status_code == 204

    async def test_logout_without_auth(self, client: AsyncClient):
        """测试未认证登出"""
        response = await client.post("/api/auth/logout")
        assert response.status_code == 401
