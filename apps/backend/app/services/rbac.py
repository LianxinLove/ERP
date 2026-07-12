"""
RBAC 服务

@description 角色权限控制的业务逻辑

@features
- 角色管理
- 权限管理
- 权限检查
- 角色分配
"""

from functools import lru_cache
from typing import List, Optional, Set

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.rbac import Role, Permission, RolePermission, UserRole
from app.models.user import User
from app.schemas.rbac import (
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    RoleListResponse,
    PermissionCreate,
    PermissionUpdate,
    PermissionResponse,
    AssignRoleRequest,
)


class PermissionService:
    """
    权限服务类
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_permission(self, data: PermissionCreate) -> PermissionResponse:
        """
        创建权限

        Args:
            data: 权限创建数据

        Returns:
            PermissionResponse: 创建的权限信息

        Raises:
            BadRequestError: 权限编码已存在
        """
        # 检查权限编码是否已存在
        result = await self.db.execute(select(Permission).where(Permission.code == data.code))
        if result.scalar_one_or_none():
            raise BadRequestError("权限编码已存在")

        permission = Permission(**data.model_dump())
        self.db.add(permission)
        await self.db.commit()
        await self.db.refresh(permission)

        return PermissionResponse.model_validate(permission)

    async def get_permissions(self, module: Optional[str] = None) -> List[PermissionResponse]:
        """
        获取权限列表

        Args:
            module: 模块名称（可选）

        Returns:
            List[PermissionResponse]: 权限列表
        """
        query = select(Permission).where(Permission.is_deleted == False)

        if module:
            query = query.where(Permission.module == module)

        query = query.order_by(Permission.module, Permission.code)

        result = await self.db.execute(query)
        permissions = result.scalars().all()

        return [PermissionResponse.model_validate(p) for p in permissions]

    async def get_permission(self, permission_id: int) -> PermissionResponse:
        """
        获取权限详情

        Args:
            permission_id: 权限ID

        Returns:
            PermissionResponse: 权限详情

        Raises:
            NotFoundError: 权限不存在
        """
        result = await self.db.execute(
            select(Permission).where(Permission.id == permission_id, Permission.is_deleted == False)
        )
        permission = result.scalar_one_or_none()

        if not permission:
            raise NotFoundError("权限不存在")

        return PermissionResponse.model_validate(permission)

    async def update_permission(self, permission_id: int, data: PermissionUpdate) -> PermissionResponse:
        """
        更新权限

        Args:
            permission_id: 权限ID
            data: 更新数据

        Returns:
            PermissionResponse: 更新后的权限信息

        Raises:
            NotFoundError: 权限不存在
        """
        result = await self.db.execute(
            select(Permission).where(Permission.id == permission_id, Permission.is_deleted == False)
        )
        permission = result.scalar_one_or_none()

        if not permission:
            raise NotFoundError("权限不存在")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(permission, field, value)

        await self.db.commit()
        await self.db.refresh(permission)

        return PermissionResponse.model_validate(permission)

    async def delete_permission(self, permission_id: int) -> None:
        """
        删除权限（软删除）

        Args:
            permission_id: 权限ID

        Raises:
            NotFoundError: 权限不存在
        """
        result = await self.db.execute(
            select(Permission).where(Permission.id == permission_id, Permission.is_deleted == False)
        )
        permission = result.scalar_one_or_none()

        if not permission:
            raise NotFoundError("权限不存在")

        permission.is_deleted = True
        permission.deleted_at = func.now()

        await self.db.commit()

    async def import_permissions(self, permissions_data: List[dict], overwrite: bool = False) -> dict:
        """
        导入权限

        Args:
            permissions_data: 权限数据列表
            overwrite: 是否覆盖已存在的权限

        Returns:
            dict: 导入结果统计
        """
        created_count = 0
        updated_count = 0
        skipped_count = 0
        errors = []

        for perm_data in permissions_data:
            try:
                # 检查权限是否已存在
                result = await self.db.execute(
                    select(Permission).where(
                        Permission.code == perm_data.get("code"),
                        Permission.is_deleted == False
                    )
                )
                existing = result.scalar_one_or_none()

                if existing:
                    if overwrite:
                        # 更新现有权限
                        for field, value in perm_data.items():
                            if field != "code" and value is not None:
                                setattr(existing, field, value)
                        updated_count += 1
                    else:
                        skipped_count += 1
                else:
                    # 创建新权限
                    permission = Permission(**perm_data)
                    self.db.add(permission)
                    created_count += 1

            except Exception as e:
                errors.append({
                    "code": perm_data.get("code", "unknown"),
                    "error": str(e)
                })

        await self.db.commit()

        return {
            "created": created_count,
            "updated": updated_count,
            "skipped": skipped_count,
            "errors": errors
        }


class RoleService:
    """
    角色服务类
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_role(self, data: RoleCreate) -> RoleResponse:
        """
        创建角色

        Args:
            data: 角色创建数据

        Returns:
            RoleResponse: 创建的角色信息

        Raises:
            BadRequestError: 角色编码已存在
        """
        # 检查角色编码是否已存在
        result = await self.db.execute(select(Role).where(Role.code == data.code))
        if result.scalar_one_or_none():
            raise BadRequestError("角色编码已存在")

        role = Role(
            name=data.name,
            code=data.code,
            description=data.description,
        )
        self.db.add(role)
        await self.db.flush()

        # 分配权限
        if data.permission_ids:
            await self._assign_permissions(role.id, data.permission_ids)

        await self.db.commit()

        # 重新加载角色及其权限
        result = await self.db.execute(
            select(Role)
            .options(selectinload(Role.permissions).selectinload(RolePermission.permission))
            .where(Role.id == role.id)
        )
        role = result.scalar_one_or_none()

        permissions = [
            PermissionResponse.model_validate(rp.permission) for rp in role.permissions
        ]

        return RoleResponse(
            id=role.id,
            name=role.name,
            code=role.code,
            description=role.description,
            is_system=role.is_system,
            created_at=role.created_at,
            updated_at=role.updated_at,
            permissions=permissions,
        )

    async def get_roles(self) -> List[RoleListResponse]:
        """
        获取角色列表

        Returns:
            List[RoleListResponse]: 角色列表
        """
        result = await self.db.execute(
            select(Role)
            .where(Role.is_deleted == False)
            .options(selectinload(Role.permissions))
        )
        roles = result.scalars().all()

        # 对于列表响应，只计算权限数量，不需要加载 permission 关系
        return [
            RoleListResponse(
                id=r.id,
                name=r.name,
                code=r.code,
                description=r.description,
                is_system=r.is_system,
                permission_count=len(r.permissions),
            )
            for r in roles
        ]

        return [
            RoleListResponse(
                id=r.id,
                name=r.name,
                code=r.code,
                description=r.description,
                is_system=r.is_system,
                permission_count=len(r.permissions),
            )
            for r in roles
        ]

    async def get_role(self, role_id: int) -> RoleResponse:
        """
        获取角色详情

        Args:
            role_id: 角色ID

        Returns:
            RoleResponse: 角色详情

        Raises:
            NotFoundError: 角色不存在
        """
        result = await self.db.execute(
            select(Role)
            .options(selectinload(Role.permissions).selectinload(RolePermission.permission))
            .where(Role.id == role_id, Role.is_deleted == False)
        )
        role = result.scalar_one_or_none()

        if not role:
            raise NotFoundError("角色不存在")

        permissions = [
            PermissionResponse.model_validate(rp.permission) for rp in role.permissions
        ]

        return RoleResponse(
            id=role.id,
            name=role.name,
            code=role.code,
            description=role.description,
            is_system=role.is_system,
            created_at=role.created_at,
            updated_at=role.updated_at,
            permissions=permissions,
        )

    async def update_role(self, role_id: int, data: RoleUpdate) -> RoleResponse:
        """
        更新角色

        Args:
            role_id: 角色ID
            data: 更新数据

        Returns:
            RoleResponse: 更新后的角色信息

        Raises:
            NotFoundError: 角色不存在
            BadRequestError: 系统角色不可修改
        """
        result = await self.db.execute(
            select(Role).where(Role.id == role_id, Role.is_deleted == False)
        )
        role = result.scalar_one_or_none()

        if not role:
            raise NotFoundError("角色不存在")

        if role.is_system:
            raise BadRequestError("系统角色不可修改")

        # 更新基本信息
        for field, value in data.model_dump(exclude_unset=True, exclude={"permission_ids"}).items():
            setattr(role, field, value)

        # 更新权限
        if data.permission_ids is not None:
            await self._assign_permissions(role_id, data.permission_ids)

        await self.db.commit()
        await self.db.refresh(role)

        return await self.get_role(role_id)

    async def delete_role(self, role_id: int) -> None:
        """
        删除角色（软删除）

        Args:
            role_id: 角色ID

        Raises:
            NotFoundError: 角色不存在
            BadRequestError: 系统角色不可删除
        """
        result = await self.db.execute(
            select(Role).where(Role.id == role_id, Role.is_deleted == False)
        )
        role = result.scalar_one_or_none()

        if not role:
            raise NotFoundError("角色不存在")

        if role.is_system:
            raise BadRequestError("系统角色不可删除")

        role.is_deleted = True
        role.deleted_at = func.now()

        await self.db.commit()

    async def assign_permissions(self, role_id: int, permission_ids: List[int]) -> None:
        """
        为角色分配权限

        Args:
            role_id: 角色ID
            permission_ids: 权限ID列表

        Raises:
            NotFoundError: 角色不存在
        """
        # 检查角色是否存在
        result = await self.db.execute(
            select(Role).where(Role.id == role_id, Role.is_deleted == False)
        )
        role = result.scalar_one_or_none()

        if not role:
            raise NotFoundError("角色不存在")

        await self._assign_permissions(role_id, permission_ids)
        await self.db.commit()

    async def batch_assign_permissions(self, role_ids: List[int], permission_ids: List[int]) -> int:
        """
        批量为角色分配相同的权限

        Args:
            role_ids: 角色ID列表
            permission_ids: 权限ID列表

        Returns:
            int: 成功分配的角色数量

        Raises:
            NotFoundError: 部分角色或权限不存在
        """
        # 检查角色是否存在
        result = await self.db.execute(
            select(Role).where(Role.id.in_(role_ids), Role.is_deleted == False)
        )
        roles = result.scalars().all()
        existing_role_ids = {r.id for r in roles}

        if len(existing_role_ids) != len(role_ids):
            missing = set(role_ids) - existing_role_ids
            raise NotFoundError(f"角色不存在: {missing}")

        # 检查权限是否存在
        result = await self.db.execute(
            select(Permission).where(Permission.id.in_(permission_ids), Permission.is_deleted == False)
        )
        permissions = result.scalars().all()
        existing_permission_ids = {p.id for p in permissions}

        if len(existing_permission_ids) != len(permission_ids):
            missing = set(permission_ids) - existing_permission_ids
            raise NotFoundError(f"权限不存在: {missing}")

        # 为每个角色分配权限
        for role_id in role_ids:
            await self._assign_permissions(role_id, permission_ids)

        await self.db.commit()
        return len(role_ids)

    async def _assign_permissions(self, role_id: int, permission_ids: List[int]) -> None:
        """
        内部方法：分配权限

        Args:
            role_id: 角色ID
            permission_ids: 权限ID列表
        """
        # 删除现有权限关联
        await self.db.execute(delete(RolePermission).where(RolePermission.role_id == role_id))

        # 创建新的权限关联
        for permission_id in permission_ids:
            rp = RolePermission(role_id=role_id, permission_id=permission_id)
            self.db.add(rp)


class UserRoleService:
    """
    用户角色服务类
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def assign_user_roles(self, user_id: int, data: AssignRoleRequest) -> None:
        """
        为用户分配角色

        Args:
            user_id: 用户ID
            data: 角色ID列表

        Raises:
            NotFoundError: 用户或角色不存在
        """
        # 检查用户是否存在
        result = await self.db.execute(select(User).where(User.id == user_id))
        if not result.scalar_one_or_none():
            raise NotFoundError("用户不存在")

        # 检查角色是否存在
        result = await self.db.execute(
            select(Role).where(Role.id.in_(data.role_ids), Role.is_deleted == False)
        )
        roles = result.scalars().all()

        if len(roles) != len(data.role_ids):
            raise NotFoundError("部分角色不存在")

        # 删除现有角色关联
        await self.db.execute(delete(UserRole).where(UserRole.user_id == user_id))

        # 创建新的角色关联
        for role_id in data.role_ids:
            ur = UserRole(user_id=user_id, role_id=role_id)
            self.db.add(ur)

        await self.db.commit()

    async def get_user_roles(self, user_id: int) -> List[RoleResponse]:
        """
        获取用户的角色列表

        Args:
            user_id: 用户ID

        Returns:
            List[RoleResponse]: 角色列表
        """
        result = await self.db.execute(
            select(Role)
            .options(selectinload(Role.permissions).selectinload(RolePermission.permission))
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id, Role.is_deleted == False)
        )
        roles = result.scalars().all()

        # 使用完整的 RoleResponse
        result_list = []
        for r in roles:
            permissions = [
                PermissionResponse.model_validate(rp.permission) for rp in r.permissions
            ]
            result_list.append(RoleResponse(
                id=r.id,
                name=r.name,
                code=r.code,
                description=r.description,
                is_system=r.is_system,
                created_at=r.created_at,
                updated_at=r.updated_at,
                permissions=permissions,
            ))
        return result_list

    async def get_user_permissions(self, user_id: int) -> Set[str]:
        """
        获取用户的所有权限编码

        Args:
            user_id: 用户ID

        Returns:
            Set[str]: 权限编码集合
        """
        # 超级管理员拥有所有权限
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user and user.is_superuser:
            all_permissions = await self.db.execute(
                select(Permission.code).where(Permission.is_deleted == False)
            )
            return set(p[0] for p in all_permissions.all())

        # 获取用户角色的权限
        result = await self.db.execute(
            select(Permission.code)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(UserRole, UserRole.role_id == RolePermission.role_id)
            .where(UserRole.user_id == user_id, Permission.is_deleted == False)
        )

        return set(p[0] for p in result.all())

    async def batch_assign_roles(self, user_ids: List[int], role_ids: List[int]) -> int:
        """
        批量为用户分配相同的角色

        Args:
            user_ids: 用户ID列表
            role_ids: 角色ID列表

        Returns:
            int: 成功分配的用户数量

        Raises:
            NotFoundError: 部分用户或角色不存在
        """
        # 检查用户是否存在
        result = await self.db.execute(select(User).where(User.id.in_(user_ids)))
        users = result.scalars().all()
        existing_user_ids = {u.id for u in users}

        if len(existing_user_ids) != len(user_ids):
            missing = set(user_ids) - existing_user_ids
            raise NotFoundError(f"用户不存在: {missing}")

        # 检查角色是否存在
        result = await self.db.execute(
            select(Role).where(Role.id.in_(role_ids), Role.is_deleted == False)
        )
        roles = result.scalars().all()

        if len(roles) != len(role_ids):
            missing = set(role_ids) - {r.id for r in roles}
            raise NotFoundError(f"角色不存在: {missing}")

        # 为每个用户分配角色
        for user_id in user_ids:
            # 删除现有角色关联
            await self.db.execute(delete(UserRole).where(UserRole.user_id == user_id))

            # 创建新的角色关联
            for role_id in role_ids:
                ur = UserRole(user_id=user_id, role_id=role_id)
                self.db.add(ur)

        await self.db.commit()
        return len(user_ids)

    async def batch_assign_different_roles(self, assignments: List[dict]) -> int:
        """
        批量为用户分配不同的角色

        Args:
            assignments: 分配列表，每项包含 user_id 和 role_ids

        Returns:
            int: 成功分配的用户数量

        Raises:
            NotFoundError: 部分用户或角色不存在
        """
        user_ids = [a["user_id"] for a in assignments]

        # 检查用户是否存在
        result = await self.db.execute(select(User).where(User.id.in_(user_ids)))
        users = result.scalars().all()
        existing_user_ids = {u.id for u in users}

        if len(existing_user_ids) != len(user_ids):
            missing = set(user_ids) - existing_user_ids
            raise NotFoundError(f"用户不存在: {missing}")

        # 收集所有角色ID进行检查
        all_role_ids = set()
        for a in assignments:
            all_role_ids.update(a["role_ids"])

        # 检查角色是否存在
        result = await self.db.execute(
            select(Role).where(Role.id.in_(all_role_ids), Role.is_deleted == False)
        )
        roles = result.scalars().all()
        existing_role_ids = {r.id for r in roles}

        if len(existing_role_ids) != len(all_role_ids):
            missing = all_role_ids - existing_role_ids
            raise NotFoundError(f"角色不存在: {missing}")

        # 为每个用户分配角色
        for assignment in assignments:
            user_id = assignment["user_id"]
            role_ids = assignment["role_ids"]

            # 删除现有角色关联
            await self.db.execute(delete(UserRole).where(UserRole.user_id == user_id))

            # 创建新的角色关联
            for role_id in role_ids:
                ur = UserRole(user_id=user_id, role_id=role_id)
                self.db.add(ur)

        await self.db.commit()
        return len(assignments)
