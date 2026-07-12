"""
数据权限服务

@description 数据权限的业务逻辑
"""

from typing import List, Optional

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.data_permission import DataPermission, DataScopeEnum
from app.models.rbac import Role
from app.models.user import User
from app.schemas.data_permission import (
    DataPermissionCreate,
    DataPermissionUpdate,
    DataPermissionResponse,
)


class DataPermissionService:
    """
    数据权限服务类
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_permission(self, data: DataPermissionCreate) -> DataPermissionResponse:
        """
        创建数据权限

        Args:
            data: 数据权限创建数据

        Returns:
            DataPermissionResponse: 创建的数据权限信息

        Raises:
            BadRequestError: 权限配置已存在
        """
        # 检查是否已存在相同配置
        conditions = [
            DataPermission.resource_type == data.resource_type,
        ]

        if data.user_id:
            conditions.append(DataPermission.user_id == data.user_id)
        else:
            conditions.append(DataPermission.user_id.is_(None))

        if data.role_id:
            conditions.append(DataPermission.role_id == data.role_id)
        else:
            conditions.append(DataPermission.role_id.is_(None))

        result = await self.db.execute(
            select(DataPermission).where(and_(*conditions))
        )
        if result.scalar_one_or_none():
            raise BadRequestError("该数据权限配置已存在")

        # 验证用户是否存在
        if data.user_id:
            result = await self.db.execute(select(User).where(User.id == data.user_id))
            if not result.scalar_one_or_none():
                raise NotFoundError("用户不存在")

        # 验证角色是否存在
        if data.role_id:
            result = await self.db.execute(
                select(Role).where(Role.id == data.role_id, Role.is_deleted == False)
            )
            if not result.scalar_one_or_none():
                raise NotFoundError("角色不存在")

        permission = DataPermission(**data.model_dump())
        self.db.add(permission)
        await self.db.commit()
        await self.db.refresh(permission)

        return DataPermissionResponse.model_validate(permission)

    async def get_permissions(
        self,
        resource_type: Optional[str] = None,
        user_id: Optional[int] = None,
        role_id: Optional[int] = None,
    ) -> List[DataPermissionResponse]:
        """
        获取数据权限列表

        Args:
            resource_type: 资源类型筛选
            user_id: 用户ID筛选
            role_id: 角色ID筛选

        Returns:
            List[DataPermissionResponse]: 数据权限列表
        """
        conditions = [DataPermission.is_active == True]

        if resource_type:
            conditions.append(DataPermission.resource_type == resource_type)
        if user_id:
            conditions.append(DataPermission.user_id == user_id)
        if role_id:
            conditions.append(DataPermission.role_id == role_id)

        result = await self.db.execute(
            select(DataPermission).where(and_(*conditions))
        )
        permissions = result.scalars().all()

        return [DataPermissionResponse.model_validate(p) for p in permissions]

    async def get_permission(self, permission_id: int) -> DataPermissionResponse:
        """
        获取数据权限详情

        Args:
            permission_id: 权限ID

        Returns:
            DataPermissionResponse: 数据权限详情

        Raises:
            NotFoundError: 权限不存在
        """
        result = await self.db.execute(
            select(DataPermission).where(DataPermission.id == permission_id)
        )
        permission = result.scalar_one_or_none()

        if not permission:
            raise NotFoundError("数据权限不存在")

        return DataPermissionResponse.model_validate(permission)

    async def update_permission(
        self, permission_id: int, data: DataPermissionUpdate
    ) -> DataPermissionResponse:
        """
        更新数据权限

        Args:
            permission_id: 权限ID
            data: 更新数据

        Returns:
            DataPermissionResponse: 更新后的数据权限信息

        Raises:
            NotFoundError: 权限不存在
        """
        result = await self.db.execute(
            select(DataPermission).where(DataPermission.id == permission_id)
        )
        permission = result.scalar_one_or_none()

        if not permission:
            raise NotFoundError("数据权限不存在")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(permission, field, value)

        await self.db.commit()
        await self.db.refresh(permission)

        return DataPermissionResponse.model_validate(permission)

    async def delete_permission(self, permission_id: int) -> None:
        """
        删除数据权限

        Args:
            permission_id: 权限ID

        Raises:
            NotFoundError: 权限不存在
        """
        result = await self.db.execute(
            select(DataPermission).where(DataPermission.id == permission_id)
        )
        permission = result.scalar_one_or_none()

        if not permission:
            raise NotFoundError("数据权限不存在")

        await self.db.delete(permission)
        await self.db.commit()

    async def get_user_effective_scope(
        self, user_id: int, resource_type: str
    ) -> str:
        """
        获取用户对指定资源的有效数据范围

        Args:
            user_id: 用户ID
            resource_type: 资源类型

        Returns:
            str: 数据范围
        """
        from app.schemas.user import UserResponse
        from app.services.auth import AuthService

        # 获取用户信息
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            return DataScopeEnum.SELF

        if user.is_superuser:
            return DataScopeEnum.ALL

        # 查询用户专属权限
        result = await self.db.execute(
            select(DataPermission).where(
                and_(
                    DataPermission.user_id == user_id,
                    DataPermission.resource_type == resource_type,
                    DataPermission.is_active == True,
                )
            )
        )
        user_permission = result.scalar_one_or_none()

        if user_permission:
            return user_permission.scope

        # 查询角色权限
        # 先获取用户的角色
        from app.models.rbac import UserRole

        result = await self.db.execute(
            select(UserRole).where(UserRole.user_id == user_id)
        )
        user_roles = result.scalars().all()

        if user_roles:
            role_ids = [ur.role_id for ur in user_roles]
            result = await self.db.execute(
                select(DataPermission).where(
                    and_(
                        DataPermission.role_id.in_(role_ids),
                        DataPermission.resource_type == resource_type,
                        DataPermission.is_active == True,
                    )
                )
            )
            role_permission = result.scalar_one_or_none()

            if role_permission:
                return role_permission.scope

        # 默认只能访问自己创建的数据
        return DataScopeEnum.SELF
