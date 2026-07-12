"""
RBAC 初始化脚本

@description 初始化默认权限和角色数据

@features
- 创建默认权限
- 创建默认角色
- 分配权限给角色
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rbac import Permission, Role, RolePermission
from app.schemas.rbac import PermissionCreate, RoleCreate


# ============ 默认权限定义 ============

DEFAULT_PERMISSIONS = [
    # 用户模块权限
    {"name": "查看用户", "code": "user.read", "module": "user"},
    {"name": "创建用户", "code": "user.create", "module": "user"},
    {"name": "更新用户", "code": "user.update", "module": "user"},
    {"name": "删除用户", "code": "user.delete", "module": "user"},
    {"name": "分配用户角色", "code": "user.assign_role", "module": "user"},

    # 角色权限模块
    {"name": "查看角色", "code": "role.read", "module": "role"},
    {"name": "创建角色", "code": "role.create", "module": "role"},
    {"name": "更新角色", "code": "role.update", "module": "role"},
    {"name": "删除角色", "code": "role.delete", "module": "role"},
    {"name": "分配角色权限", "code": "role.assign_permission", "module": "role"},

    # 权限模块
    {"name": "查看权限", "code": "permission.read", "module": "permission"},
    {"name": "创建权限", "code": "permission.create", "module": "permission"},
    {"name": "更新权限", "code": "permission.update", "module": "permission"},
    {"name": "删除权限", "code": "permission.delete", "module": "permission"},
    {"name": "导入导出权限", "code": "permission.import_export", "module": "permission"},

    # 财务模块权限
    {"name": "查看财务科目", "code": "finance.account.read", "module": "finance"},
    {"name": "管理财务科目", "code": "finance.account.manage", "module": "finance"},
    {"name": "查看应收账款", "code": "finance.receivable.read", "module": "finance"},
    {"name": "管理应收账款", "code": "finance.receivable.manage", "module": "finance"},
    {"name": "查看应付账款", "code": "finance.payable.read", "module": "finance"},
    {"name": "管理应付账款", "code": "finance.payable.manage", "module": "finance"},
    {"name": "查看收付款", "code": "finance.payment.read", "module": "finance"},
    {"name": "创建收付款", "code": "finance.payment.create", "module": "finance"},
    {"name": "完成收付款", "code": "finance.payment.complete", "module": "finance"},
    {"name": "取消收付款", "code": "finance.payment.cancel", "module": "finance"},
    {"name": "查看财务报表", "code": "finance.report.read", "module": "finance"},

    # 库存模块权限
    {"name": "查看仓库", "code": "inventory.warehouse.read", "module": "inventory"},
    {"name": "管理仓库", "code": "inventory.warehouse.manage", "module": "inventory"},
    {"name": "查看产品", "code": "inventory.product.read", "module": "inventory"},
    {"name": "管理产品", "code": "inventory.product.manage", "module": "inventory"},
    {"name": "查看库存", "code": "inventory.stock.read", "module": "inventory"},
    {"name": "调整库存", "code": "inventory.stock.adjust", "module": "inventory"},
    {"name": "查看库存流水", "code": "inventory.transaction.read", "module": "inventory"},
    {"name": "查看库存调拨", "code": "inventory.transfer.read", "module": "inventory"},
    {"name": "创建库存调拨", "code": "inventory.transfer.create", "module": "inventory"},
    {"name": "执行库存调拨", "code": "inventory.transfer.execute", "module": "inventory"},

    # 销售模块权限
    {"name": "查看客户", "code": "sales.customer.read", "module": "sales"},
    {"name": "管理客户", "code": "sales.customer.manage", "module": "sales"},
    {"name": "查看销售订单", "code": "sales.order.read", "module": "sales"},
    {"name": "创建销售订单", "code": "sales.order.create", "module": "sales"},
    {"name": "更新销售订单", "code": "sales.order.update", "module": "sales"},
    {"name": "删除销售订单", "code": "sales.order.delete", "module": "sales"},
    {"name": "确认销售订单", "code": "sales.order.confirm", "module": "sales"},
    {"name": "取消销售订单", "code": "sales.order.cancel", "module": "sales"},
    {"name": "查看销售报表", "code": "sales.report.read", "module": "sales"},

    # 采购模块权限
    {"name": "查看供应商", "code": "purchase.supplier.read", "module": "purchase"},
    {"name": "管理供应商", "code": "purchase.supplier.manage", "module": "purchase"},
    {"name": "查看采购订单", "code": "purchase.order.read", "module": "purchase"},
    {"name": "创建采购订单", "code": "purchase.order.create", "module": "purchase"},
    {"name": "更新采购订单", "code": "purchase.order.update", "module": "purchase"},
    {"name": "删除采购订单", "code": "purchase.order.delete", "module": "purchase"},
    {"name": "确认采购订单", "code": "purchase.order.confirm", "module": "purchase"},
    {"name": "取消采购订单", "code": "purchase.order.cancel", "module": "purchase"},

    # 工作流模块权限
    {"name": "查看流程定义", "code": "workflow.definition.read", "module": "workflow"},
    {"name": "管理流程定义", "code": "workflow.definition.manage", "module": "workflow"},
    {"name": "查看流程实例", "code": "workflow.instance.read", "module": "workflow"},
    {"name": "启动流程", "code": "workflow.instance.start", "module": "workflow"},
    {"name": "处理待办任务", "code": "workflow.task.process", "module": "workflow"},
    {"name": "查看我的待办", "code": "workflow.task.my", "module": "workflow"},

    # 组织模块权限
    {"name": "查看部门", "code": "organization.department.read", "module": "organization"},
    {"name": "管理部门", "code": "organization.department.manage", "module": "organization"},
    {"name": "查看员工", "code": "organization.employee.read", "module": "organization"},
    {"name": "管理员工", "code": "organization.employee.manage", "module": "organization"},
]


# ============ 默认角色定义 ============

DEFAULT_ROLES = [
    {
        "name": "超级管理员",
        "code": "superadmin",
        "description": "拥有系统所有权限",
        "is_system": True,
        "permissions": "all",  # 特殊标记，表示所有权限
    },
    {
        "name": "财务管理员",
        "code": "finance_manager",
        "description": "负责财务相关操作",
        "is_system": True,
        "permissions": [
            "finance.*",  # 所有财务权限
            "sales.order.read",  # 可查看销售订单
            "purchase.order.read",  # 可查看采购订单
        ],
    },
    {
        "name": "库存管理员",
        "code": "inventory_manager",
        "description": "负责库存管理",
        "is_system": True,
        "permissions": [
            "inventory.*",  # 所有库存权限
        ],
    },
    {
        "name": "销售员",
        "code": "sales",
        "description": "负责销售业务",
        "is_system": True,
        "permissions": [
            "sales.customer.read",
            "sales.customer.manage",
            "sales.order.*",  # 所有销售订单权限
            "sales.report.read",
            "inventory.product.read",  # 可查看产品
            "inventory.stock.read",  # 可查看库存
        ],
    },
    {
        "name": "采购员",
        "code": "purchaser",
        "description": "负责采购业务",
        "is_system": True,
        "permissions": [
            "purchase.supplier.read",
            "purchase.supplier.manage",
            "purchase.order.*",  # 所有采购订单权限
            "inventory.product.read",  # 可查看产品
            "inventory.stock.read",  # 可查看库存
        ],
    },
    {
        "name": "普通用户",
        "code": "user",
        "description": "普通用户，拥有基础权限",
        "is_system": True,
        "permissions": [
            "workflow.task.my",  # 可查看自己的待办
            "workflow.task.process",  # 可处理待办
            "sales.order.read",  # 只读
            "purchase.order.read",  # 只读
            "inventory.product.read",  # 只读
            "inventory.stock.read",  # 只读
        ],
    },
]


async def init_permissions(db: AsyncSession) -> dict:
    """
    初始化默认权限

    Args:
        db: 数据库会话

    Returns:
        dict: 创建统计
    """
    from sqlalchemy import select

    created_count = 0
    skipped_count = 0

    for perm_data in DEFAULT_PERMISSIONS:
        # 检查权限是否已存在
        result = await db.execute(
            select(Permission).where(Permission.code == perm_data["code"])
        )
        existing = result.scalar_one_or_none()

        if existing:
            skipped_count += 1
        else:
            permission = Permission(**perm_data)
            db.add(permission)
            created_count += 1

    await db.commit()

    return {
        "created": created_count,
        "skipped": skipped_count,
        "total": len(DEFAULT_PERMISSIONS)
    }


async def init_roles(db: AsyncSession) -> dict:
    """
    初始化默认角色

    Args:
        db: 数据库会话

    Returns:
        dict: 创建统计
    """
    from sqlalchemy import select

    # 先获取所有权限
    result = await db.execute(select(Permission))
    all_permissions = result.scalars().all()
    permission_map = {p.code: p for p in all_permissions}

    created_count = 0
    skipped_count = 0

    for role_data in DEFAULT_ROLES:
        # 检查角色是否已存在
        result = await db.execute(
            select(Role).where(Role.code == role_data["code"])
        )
        existing = result.scalar_one_or_none()

        if existing:
            skipped_count += 1
            continue

        # 创建角色
        role = Role(
            name=role_data["name"],
            code=role_data["code"],
            description=role_data["description"],
            is_system=role_data["is_system"],
        )
        db.add(role)
        await db.flush()  # 获取角色ID

        # 分配权限
        permissions_config = role_data["permissions"]
        perm_codes = []

        if permissions_config == "all":
            # 超级管理员拥有所有权限
            perm_codes = list(permission_map.keys())
        else:
            # 解析权限列表（支持通配符）
            for perm_pattern in permissions_config:
                if perm_pattern.endswith(".*"):
                    # 通配符匹配
                    prefix = perm_pattern[:-2]
                    perm_codes.extend([k for k in permission_map.keys() if k.startswith(prefix + ".") or k == prefix])
                else:
                    perm_codes.append(perm_pattern)

        # 去重
        perm_codes = list(set(perm_codes))

        # 创建权限关联
        for code in perm_codes:
            if code in permission_map:
                rp = RolePermission(role_id=role.id, permission_id=permission_map[code].id)
                db.add(rp)

        created_count += 1

    await db.commit()

    return {
        "created": created_count,
        "skipped": skipped_count,
        "total": len(DEFAULT_ROLES)
    }


async def init_rbac(db: AsyncSession) -> dict:
    """
    初始化 RBAC 数据（权限和角色）

    Args:
        db: 数据库会话

    Returns:
        dict: 初始化结果
    """
    print("初始化 RBAC 数据...")

    # 初始化权限
    perm_result = await init_permissions(db)
    print(f"权限初始化完成: 创建 {perm_result['created']} 个，跳过 {perm_result['skipped']} 个")

    # 初始化角色
    role_result = await init_roles(db)
    print(f"角色初始化完成: 创建 {role_result['created']} 个，跳过 {role_result['skipped']} 个")

    return {
        "permissions": perm_result,
        "roles": role_result
    }
