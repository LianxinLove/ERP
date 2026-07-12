"""
Redis 权限缓存模块

@description 使用 Redis 存储用户权限缓存，支持多进程/多服务器环境
"""

import json
import logging
from typing import Optional, Set

# Redis 是可选依赖，如果没有安装则使用内存缓存
try:
    from redis.asyncio import Redis, ConnectionPool
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    Redis = None  # type: ignore
    ConnectionPool = None  # type: ignore

from app.core.config import settings

logger = logging.getLogger(__name__)

# Redis 连接池
_redis_pool: Optional[ConnectionPool] = None
_redis_client: Optional[Redis] = None


def get_redis_client() -> Optional[Redis]:
    """
    获取 Redis 客户端

    Returns:
        Optional[Redis]: Redis 客户端实例，不可用时返回 None
    """
    global _redis_client, _redis_pool

    if not REDIS_AVAILABLE:
        logger.debug("Redis 模块未安装，权限缓存将使用内存缓存")
        return None

    if _redis_client is None:
        # 检查是否配置了 Redis
        redis_url = getattr(settings, 'REDIS_URL', None)
        if not redis_url:
            logger.warning("Redis 未配置，权限缓存将使用内存缓存")
            return None

        try:
            _redis_pool = ConnectionPool.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            _redis_client = Redis(connection_pool=_redis_pool)
            logger.info("Redis 连接成功")
        except Exception as e:
            logger.error(f"Redis 连接失败: {e}")
            _redis_client = None

    return _redis_client


async def close_redis():
    """关闭 Redis 连接"""
    global _redis_client, _redis_pool

    if not REDIS_AVAILABLE:
        return

    if _redis_client:
        await _redis_client.close()
        _redis_client = None

    if _redis_pool:
        await _redis_pool.disconnect()
        _redis_pool = None


class PermissionCache:
    """
    权限缓存类

    提供 Redis 缓存和内存缓存的统一接口
    """

    def __init__(self):
        self._memory_cache: dict[int, Set[str]] = {}
        self._use_redis = False

    async def _init_redis(self):
        """初始化 Redis 连接"""
        if not self._use_redis:
            client = get_redis_client()
            self._use_redis = client is not None

    async def get(self, user_id: int) -> Optional[Set[str]]:
        """
        获取用户权限缓存

        Args:
            user_id: 用户ID

        Returns:
            Set[str]: 权限编码集合，不存在时返回 None
        """
        await self._init_redis()

        if self._use_redis:
            try:
                client = get_redis_client()
                if client:
                    key = f"permissions:user:{user_id}"
                    value = await client.get(key)
                    if value:
                        return set(json.loads(value))
            except Exception as e:
                logger.error(f"Redis 获取缓存失败: {e}")
                # 降级到内存缓存
                return self._memory_cache.get(user_id)

        return self._memory_cache.get(user_id)

    async def set(self, user_id: int, permissions: Set[str], ttl: int = 3600) -> None:
        """
        设置用户权限缓存

        Args:
            user_id: 用户ID
            permissions: 权限编码集合
            ttl: 缓存过期时间（秒），默认1小时
        """
        await self._init_redis()

        # 同时设置内存缓存（降级使用）
        self._memory_cache[user_id] = permissions

        if self._use_redis:
            try:
                client = get_redis_client()
                if client:
                    key = f"permissions:user:{user_id}"
                    await client.setex(
                        key,
                        ttl,
                        json.dumps(list(permissions))
                    )
            except Exception as e:
                logger.error(f"Redis 设置缓存失败: {e}")

    async def delete(self, user_id: int) -> None:
        """
        删除用户权限缓存

        Args:
            user_id: 用户ID
        """
        await self._init_redis()

        # 删除内存缓存
        if user_id in self._memory_cache:
            del self._memory_cache[user_id]

        if self._use_redis:
            try:
                client = get_redis_client()
                if client:
                    key = f"permissions:user:{user_id}"
                    await client.delete(key)
            except Exception as e:
                logger.error(f"Redis 删除缓存失败: {e}")

    async def delete_by_pattern(self, pattern: str) -> int:
        """
        根据模式删除缓存

        Args:
            pattern: 匹配模式，如 "permissions:user:*"

        Returns:
            int: 删除的键数量
        """
        await self._init_redis()

        count = 0

        # 删除匹配的内存缓存
        if pattern == "permissions:user:*":
            # 清空所有内存缓存
            cleared = len(self._memory_cache)
            self._memory_cache.clear()
            count += cleared

        if self._use_redis:
            try:
                client = get_redis_client()
                if client:
                    keys = []
                    async for key in client.scan_iter(match=pattern):
                        keys.append(key)
                    if keys:
                        count += await client.delete(*keys)
            except Exception as e:
                logger.error(f"Redis 批量删除缓存失败: {e}")

        return count

    async def clear_all(self) -> None:
        """清空所有权限缓存"""
        await self._init_redis()

        # 清空内存缓存
        self._memory_cache.clear()

        if self._use_redis:
            try:
                client = get_redis_client()
                if client:
                    keys = []
                    async for key in client.scan_iter(match="permissions:*"):
                        keys.append(key)
                    if keys:
                        await client.delete(*keys)
            except Exception as e:
                logger.error(f"Redis 清空缓存失败: {e}")


# 全局缓存实例
permission_cache = PermissionCache()


async def get_cached_permissions(user_id: int) -> Optional[Set[str]]:
    """
    获取用户缓存的权限

    Args:
        user_id: 用户ID

    Returns:
        Set[str]: 权限编码集合
    """
    return await permission_cache.get(user_id)


async def set_cached_permissions(user_id: int, permissions: Set[str], ttl: int = 3600) -> None:
    """
    设置用户权限缓存

    Args:
        user_id: 用户ID
        permissions: 权限编码集合
        ttl: 缓存过期时间（秒）
    """
    await permission_cache.set(user_id, permissions, ttl)


async def clear_permission_cache(user_id: int) -> None:
    """
    清除用户权限缓存

    Args:
        user_id: 用户ID
    """
    await permission_cache.delete(user_id)


async def clear_all_permission_cache() -> None:
    """清空所有权限缓存"""
    await permission_cache.clear_all()


async def clear_permission_cache_by_role(role_id: int) -> int:
    """
    根据角色清除权限缓存

    当角色权限变更时，清除所有拥有该角色的用户的缓存

    Args:
        role_id: 角色ID

    Returns:
        int: 清除的缓存数量
    """
    # 由于 Redis 无法直接根据 role_id 查找用户
    # 这里简化处理：清空所有缓存
    # 在实际应用中，可以维护一个 role -> users 的映射
    await permission_cache.clear_all()
    return -1  # 返回 -1 表示全部清除
