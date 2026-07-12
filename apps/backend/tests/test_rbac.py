"""
RBAC 模块单元测试

@description 测试角色权限管理的各项功能
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rbac import Role, Permission, RolePermission
from app.models.user import User


class TestPermissionService:
    """权限服务测试"""

    @pytest.mark.asyncio
    async def test_create_permission(self, db_session: AsyncSession):
        """创建权限"""
        from app.services.rbac import PermissionService
        from app.schemas.rbac import PermissionCreate

        service = PermissionService(db_session)
        data = PermissionCreate(
            name="测试权限",
            code="test.permission",
            module="test",
            description="测试权限描述"
        )

        result = await service.create_permission(data)

        assert result.code == "test.permission"
        assert result.name == "测试权限"
        assert result.module == "test"

    @pytest.mark.asyncio
    async def test_create_duplicate_permission(self, db_session: AsyncSession):
        """创建重复权限应失败"""
        from app.services.rbac import PermissionService
        from app.schemas.rbac import PermissionCreate
        from app.core.exceptions import BadRequestError

        service = PermissionService(db_session)
        data = PermissionCreate(
            name="测试权限",
            code="test.duplicate",
            module="test"
        )

        await service.create_permission(data)

        with pytest.raises(BadRequestError, match="权限编码已存在"):
            await service.create_permission(data)

    @pytest.mark.asyncio
    async def test_get_permissions(self, db_session: AsyncSession):
        """获取权限列表"""
        from app.services.rbac import PermissionService
        from app.schemas.rbac import PermissionCreate

        service = PermissionService(db_session)

        # 创建测试权限
        await service.create_permission(PermissionCreate(
            name="权限1", code="test.1", module="test"
        ))
        await service.create_permission(PermissionCreate(
            name="权限2", code="test.2", module="test"
        ))

        result = await service.get_permissions()

        assert len(result) >= 2

    @pytest.mark.asyncio
    async def test_delete_permission(self, db_session: AsyncSession):
        """删除权限（软删除）"""
        from app.services.rbac import PermissionService
        from app.schemas.rbac import PermissionCreate

        service = PermissionService(db_session)

        permission = await service.create_permission(PermissionCreate(
            name="删除测试", code="test.delete", module="test"
        ))

        await service.delete_permission(permission.id)

        # 验证软删除
        from sqlalchemy import select
        result = await db_session.execute(
            select(Permission).where(Permission.id == permission.id)
        )
        deleted = result.scalar_one_or_none()

        assert deleted.is_deleted is True
        assert deleted.deleted_at is not None


class TestRoleService:
    """角色服务测试"""

    @pytest.mark.asyncio
    async def test_create_role(self, db_session: AsyncSession):
        """创建角色"""
        from app.services.rbac import RoleService
        from app.schemas.rbac import RoleCreate

        service = RoleService(db_session)
        data = RoleCreate(
            name="测试角色",
            code="test_role_001",
            description="测试角色描述"
        )

        result = await service.create_role(data)

        assert result.code == "test_role_001"
        assert result.name == "测试角色"

    @pytest.mark.asyncio
    async def test_create_role_with_permissions(self, db_session: AsyncSession):
        """创建角色并分配权限"""
        from app.services.rbac import RoleService, PermissionService
        from app.schemas.rbac import RoleCreate, PermissionCreate

        perm_service = PermissionService(db_session)
        role_service = RoleService(db_session)

        # 创建权限
        perm1 = await perm_service.create_permission(PermissionCreate(
            name="角色权限1", code="role_test.1", module="role_test"
        ))
        perm2 = await perm_service.create_permission(PermissionCreate(
            name="角色权限2", code="role_test.2", module="role_test"
        ))

        # 创建角色并分配权限
        role = await role_service.create_role(RoleCreate(
            name="测试角色",
            code="test_role_with_perm_001",
            permission_ids=[perm1.id, perm2.id]
        ))

        assert len(role.permissions) == 2

    @pytest.mark.asyncio
    async def test_assign_permissions(self, db_session: AsyncSession):
        """为角色分配权限"""
        from app.services.rbac import RoleService, PermissionService
        from app.schemas.rbac import RoleCreate, PermissionCreate

        perm_service = PermissionService(db_session)
        role_service = RoleService(db_session)

        # 创建权限
        perm = await perm_service.create_permission(PermissionCreate(
            name="分配权限", code="assign_test.1", module="assign_test"
        ))

        # 创建角色
        role = await role_service.create_role(RoleCreate(
            name="测试角色",
            code="test_role_assign_001"
        ))

        # 分配权限
        await role_service.assign_permissions(role.id, [perm.id])

        # 验证
        updated_role = await role_service.get_role(role.id)
        assert len(updated_role.permissions) == 1
        assert updated_role.permissions[0].code == "assign_test.1"


class TestUserRoleService:
    """用户角色服务测试"""

    @pytest.mark.asyncio
    async def test_assign_user_roles(self, db_session: AsyncSession, test_user: User):
        """为用户分配角色"""
        from app.services.rbac import UserRoleService, RoleService
        from app.schemas.rbac import RoleCreate, AssignRoleRequest

        role_service = RoleService(db_session)
        user_role_service = UserRoleService(db_session)

        # 创建角色
        role = await role_service.create_role(RoleCreate(
            name="测试角色",
            code="test_user_role"
        ))

        # 分配角色给用户
        await user_role_service.assign_user_roles(
            test_user.id,
            AssignRoleRequest(role_ids=[role.id])
        )

        # 验证
        user_roles = await user_role_service.get_user_roles(test_user.id)
        assert len(user_roles) == 1
        assert user_roles[0].code == "test_user_role"

    @pytest.mark.asyncio
    async def test_get_user_permissions(self, db_session: AsyncSession, test_user: User):
        """获取用户的所有权限"""
        from app.services.rbac import UserRoleService, RoleService, PermissionService
        from app.schemas.rbac import RoleCreate, PermissionCreate, AssignRoleRequest

        perm_service = PermissionService(db_session)
        role_service = RoleService(db_session)
        user_role_service = UserRoleService(db_session)

        # 创建权限
        perm = await perm_service.create_permission(PermissionCreate(
            name="用户测试权限", code="user_test.001", module="user_test"
        ))

        # 创建角色并分配权限
        role = await role_service.create_role(RoleCreate(
            name="用户测试角色",
            code="user_test_role_001",
            permission_ids=[perm.id]
        ))

        # 分配角色给用户
        await user_role_service.assign_user_roles(
            test_user.id,
            AssignRoleRequest(role_ids=[role.id])
        )

        # 获取用户权限
        permissions = await user_role_service.get_user_permissions(test_user.id)

        assert "user_test.001" in permissions


class TestBatchOperations:
    """批量操作测试"""

    @pytest.mark.asyncio
    async def test_batch_assign_roles(self, db_session: AsyncSession):
        """批量分配角色给用户"""
        from app.services.rbac import UserRoleService, RoleService
        from app.models.user import User
        from app.schemas.rbac import RoleCreate
        from app.core.security import get_password_hash

        role_service = RoleService(db_session)
        user_role_service = UserRoleService(db_session)

        # 创建角色
        role = await role_service.create_role(RoleCreate(
            name="批量测试角色",
            code="batch_test_role_001"
        ))

        # 创建多个用户
        user1 = User(
            username="user1",
            email="user1@test.com",
            password_hash=get_password_hash("pass123"),
            full_name="User 1"
        )
        user2 = User(
            username="user2",
            email="user2@test.com",
            password_hash=get_password_hash("pass123"),
            full_name="User 2"
        )
        db_session.add(user1)
        db_session.add(user2)
        await db_session.commit()

        # 批量分配角色
        count = await user_role_service.batch_assign_roles(
            [user1.id, user2.id],
            [role.id]
        )

        assert count == 2

    @pytest.mark.asyncio
    async def test_batch_assign_permissions(self, db_session: AsyncSession):
        """批量分配权限给角色"""
        from app.services.rbac import PermissionService, RoleService
        from app.schemas.rbac import PermissionCreate, RoleCreate

        perm_service = PermissionService(db_session)
        role_service = RoleService(db_session)

        # 创建权限
        perm1 = await perm_service.create_permission(PermissionCreate(
            name="批量权限1", code="batch_perm.1", module="batch_perm"
        ))
        perm2 = await perm_service.create_permission(PermissionCreate(
            name="批量权限2", code="batch_perm.2", module="batch_perm"
        ))

        # 创建角色
        role1 = await role_service.create_role(RoleCreate(
            name="批量角色1", code="batch_role_001"
        ))
        role2 = await role_service.create_role(RoleCreate(
            name="批量角色2", code="batch_role_002"
        ))

        # 批量分配权限
        count = await role_service.batch_assign_permissions(
            [role1.id, role2.id],
            [perm1.id, perm2.id]
        )

        assert count == 2


class TestPermissionImportExport:
    """权限导入导出测试"""

    @pytest.mark.asyncio
    async def test_export_permissions(self, db_session: AsyncSession):
        """导出权限"""
        from app.services.rbac import PermissionService
        from app.schemas.rbac import PermissionCreate

        service = PermissionService(db_session)

        # 创建测试权限
        await service.create_permission(PermissionCreate(
            name="导出测试", code="export.test", module="export"
        ))

        permissions = await service.get_permissions()

        assert len(permissions) >= 1
        assert any(p.code == "export.test" for p in permissions)

    @pytest.mark.asyncio
    async def test_import_permissions(self, db_session: AsyncSession):
        """导入权限"""
        from app.services.rbac import PermissionService

        service = PermissionService(db_session)

        permissions_data = [
            {
                "name": "导入权限1",
                "code": "import.1",
                "module": "import",
                "description": "导入测试"
            },
            {
                "name": "导入权限2",
                "code": "import.2",
                "module": "import"
            }
        ]

        result = await service.import_permissions(permissions_data, overwrite=False)

        assert result["created"] == 2
        assert result["skipped"] == 0
        assert len(result["errors"]) == 0

    @pytest.mark.asyncio
    async def test_import_overwrite_permissions(self, db_session: AsyncSession):
        """导入权限并覆盖"""
        from app.services.rbac import PermissionService
        from app.schemas.rbac import PermissionCreate

        service = PermissionService(db_session)

        # 先创建一个权限
        await service.create_permission(PermissionCreate(
            name="原始名称",
            code="overwrite.test",
            module="overwrite"
        ))

        # 导入并覆盖
        permissions_data = [
            {
                "name": "更新后的名称",
                "code": "overwrite.test",
                "module": "overwrite",
                "description": "更新后的描述"
            }
        ]

        result = await service.import_permissions(permissions_data, overwrite=True)

        assert result["created"] == 0
        assert result["updated"] == 1

        # 验证更新
        permissions = await service.get_permissions()
        perm = next(p for p in permissions if p.code == "overwrite.test")
        assert perm.name == "更新后的名称"
        assert perm.description == "更新后的描述"


class TestDataPermission:
    """数据权限测试"""

    @pytest.mark.asyncio
    async def test_get_user_data_scope(self, db_session: AsyncSession, test_user: User):
        """获取用户数据范围"""
        from app.services.data_permission import DataPermissionService

        service = DataPermissionService(db_session)

        # 默认范围应该是 self
        scope = await service.get_user_effective_scope(test_user.id, "sales_order")

        assert scope == "self"

    @pytest.mark.asyncio
    async def test_create_data_permission(self, db_session: AsyncSession, test_user: User):
        """创建数据权限"""
        from app.services.data_permission import DataPermissionService
        from app.schemas.data_permission import DataPermissionCreate

        service = DataPermissionService(db_session)

        permission = await service.create_permission(DataPermissionCreate(
            user_id=test_user.id,
            resource_type="sales_order",
            scope="department"
        ))

        assert permission.resource_type == "sales_order"
        assert permission.scope == "department"
