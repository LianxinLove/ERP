"""
数据库初始化脚本
@description 创建所有数据库表和初始数据
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.core.config import settings
from app.core.init_rbac import init_rbac

# 必须导入所有模型以确保它们被注册到 Base.metadata
from app.models import (
    User,
    UserSession,
    PasswordReset,
    Role,
    Permission,
    RolePermission,
    UserRole,
    Department,
    Position,
    EmployeeProfile,
    WorkflowDefinition,
    WorkflowNode,
    WorkflowEdge,
    WorkflowInstance,
    WorkflowTask,
    WorkflowApproval,
    Supplier,
    PurchaseRequest,
    PurchaseRequestItem,
    PurchaseOrder,
    PurchaseOrderItem,
    Customer,
    SalesOrder,
    SalesOrderItem,
    SalesReturn,
    SalesReturnItem,
    Warehouse,
    Product,
    Inventory,
    InventoryTransaction,
    InventoryTransfer,
    InventoryTransferItem,
    Account,
    PaymentMethod,
    Receivable,
    Payable,
    Payment,
)


async def init_database():
    """初始化数据库"""
    print("正在初始化数据库...")

    # 创建引擎
    engine = create_async_engine(
        settings.database_url,
        echo=settings.DEBUG,
    )

    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("数据库表创建成功！")

    # 创建会话并初始化 RBAC 数据
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        # 初始化权限和角色
        await init_rbac(session)
        print("RBAC 数据初始化成功！")

    await engine.dispose()


def main():
    """主函数"""
    asyncio.run(init_database())


if __name__ == "__main__":
    main()
