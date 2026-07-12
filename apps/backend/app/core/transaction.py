"""
事务处理工具模块

@description 提供数据库事务处理的装饰器和上下文管理器

@features
- 自动事务回滚
- 统一错误处理
- 事务上下文管理
"""

import functools
from typing import Callable, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import APIException


T = TypeVar('T')


def with_transaction(func: Callable[..., T]) -> Callable[..., T]:
    """
    事务处理装饰器

    自动处理数据库事务的提交和回滚

    Args:
        func: 需要事务处理的函数

    Returns:
        包装后的函数

    Example:
        class MyService:
            def __init__(self, db: AsyncSession):
                self.db = db

            @with_transaction
            async def create_something(self, data: DataCreate) -> DataResponse:
                # 这里抛出异常会自动回滚
                obj = Something(**data.dict())
                self.db.add(obj)
                await self.db.commit()
                await self.db.refresh(obj)
                return DataResponse.model_validate(obj)
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> T:
        # 假设第一个参数是 self，它包含 db 属性
        self = args[0]
        db: AsyncSession = self.db

        try:
            result = await func(*args, **kwargs)
            return result
        except APIException:
            # 业务异常直接抛出，让上层处理
            await db.rollback()
            raise
        except Exception as e:
            # 系统异常回滚并记录日志
            await db.rollback()
            import logging
            logging.getLogger(__name__).error(
                f"Transaction error in {func.__name__}: {str(e)}",
                exc_info=True
            )
            raise

    return wrapper


class Transactional:
    """
    事务处理基类

    为服务类提供事务处理能力

    Example:
        class MyService(Transactional):
            def __init__(self, db: AsyncSession):
                super().__init__(db)
                # 其他初始化...

            async def create_something(self, data: DataCreate):
                return await self._transactional(
                    self._create_something_impl, data
                )

            async def _create_something_impl(self, data: DataCreate):
                # 实际业务逻辑
                obj = Something(**data.dict())
                self.db.add(obj)
                await self.db.commit()
                await self.db.refresh(obj)
                return DataResponse.model_validate(obj)
    """

    def __init__(self, db: AsyncSession):
        """
        初始化事务处理器

        Args:
            db: 数据库会话
        """
        self.db = db
        self._in_transaction = False

    async def _transactional(self, func: Callable[..., T], *args, **kwargs) -> T:
        """
        在事务中执行函数

        Args:
            func: 要执行的函数
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            函数执行结果

        Raises:
            Exception: 函数执行中的任何异常
        """
        try:
            result = await func(*args, **kwargs)
            return result
        except APIException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            import logging
            logging.getLogger(__name__).error(
                f"Transaction error in {func.__name__}: {str(e)}",
                exc_info=True
            )
            raise
