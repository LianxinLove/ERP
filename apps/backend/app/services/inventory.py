"""
库存管理服务层

@description 库存模块的业务逻辑

@services
- WarehouseService: 仓库服务
- ProductService: 产品服务
- InventoryService: 库存服务
- InventoryTransferService: 库存调拨服务
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.inventory import (
    Warehouse,
    Product,
    ProductStatus,
    Inventory,
    TransactionType,
    InventoryTransaction,
    InventoryTransfer,
    InventoryTransferItem,
    TransferStatus,
)
from app.schemas.inventory import (
    WarehouseCreate,
    WarehouseUpdate,
    ProductCreate,
    ProductUpdate,
    InventoryTransferCreate,
    InventoryTransferUpdate,
)


class WarehouseService:
    """仓库服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_warehouse(self, data: WarehouseCreate) -> Warehouse:
        """创建仓库"""
        # 检查编码是否已存在
        result = await self.db.execute(
            select(Warehouse).where(
                Warehouse.code == data.code,
                Warehouse.is_deleted == False,
            )
        )
        if result.scalar_one_or_none():
            raise BadRequestError("仓库编码已存在")

        warehouse = Warehouse(**data.model_dump())
        self.db.add(warehouse)
        await self.db.commit()
        await self.db.refresh(warehouse)

        return warehouse

    async def get_warehouses(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Warehouse]:
        """获取仓库列表"""
        query = select(Warehouse).where(Warehouse.is_deleted == False)
        query = query.order_by(Warehouse.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_warehouse(self, warehouse_id: int) -> Warehouse:
        """获取仓库详情"""
        result = await self.db.execute(
            select(Warehouse).where(
                Warehouse.id == warehouse_id,
                Warehouse.is_deleted == False,
            )
        )
        warehouse = result.scalar_one_or_none()

        if not warehouse:
            raise NotFoundError("仓库不存在")

        return warehouse

    async def update_warehouse(self, warehouse_id: int, data: WarehouseUpdate) -> Warehouse:
        """更新仓库"""
        warehouse = await self.get_warehouse(warehouse_id)

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(warehouse, field, value)

        warehouse.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(warehouse)

        return warehouse

    async def delete_warehouse(self, warehouse_id: int) -> None:
        """删除仓库（软删除）"""
        warehouse = await self.get_warehouse(warehouse_id)

        # 检查是否有库存记录
        result = await self.db.execute(
            select(func.count(Inventory.id)).where(
                Inventory.warehouse_id == warehouse_id
            )
        )
        count = result.scalar()

        if count > 0:
            raise BadRequestError("该仓库存在库存记录，无法删除")

        warehouse.is_deleted = True
        warehouse.updated_at = datetime.now(timezone.utc)
        await self.db.commit()


class ProductService:
    """产品服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_product(self, data: ProductCreate) -> Product:
        """创建产品"""
        # 检查编码是否已存在
        result = await self.db.execute(
            select(Product).where(
                Product.code == data.code,
                Product.is_deleted == False,
            )
        )
        if result.scalar_one_or_none():
            raise BadRequestError("产品编码已存在")

        product = Product(**data.model_dump())
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)

        return product

    async def get_products(
        self,
        category: Optional[str] = None,
        keyword: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Product]:
        """获取产品列表"""
        query = select(Product).where(Product.is_deleted == False)

        if category:
            query = query.where(Product.category == category)

        if status:
            query = query.where(Product.status == status)

        if keyword:
            query = query.where(
                or_(
                    Product.code.like(f"%{keyword}%"),
                    Product.name.like(f"%{keyword}%"),
                    Product.barcode.like(f"%{keyword}%"),
                )
            )

        query = query.order_by(Product.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_product(self, product_id: int) -> Product:
        """获取产品详情"""
        result = await self.db.execute(
            select(Product).where(
                Product.id == product_id,
                Product.is_deleted == False,
            )
        )
        product = result.scalar_one_or_none()

        if not product:
            raise NotFoundError("产品不存在")

        return product

    async def update_product(self, product_id: int, data: ProductUpdate) -> Product:
        """更新产品"""
        product = await self.get_product(product_id)

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(product, field, value)

        product.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(product)

        return product

    async def delete_product(self, product_id: int) -> None:
        """删除产品（软删除）"""
        product = await self.get_product(product_id)

        # 检查是否有库存记录
        result = await self.db.execute(
            select(func.count(Inventory.id)).where(
                Inventory.product_id == product_id
            )
        )
        count = result.scalar()

        if count > 0:
            raise BadRequestError("该产品存在库存记录，无法删除")

        product.is_deleted = True
        product.updated_at = datetime.now(timezone.utc)
        await self.db.commit()


class InventoryService:
    """库存服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_inventories(
        self,
        warehouse_id: Optional[int] = None,
        product_id: Optional[int] = None,
        low_stock_only: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> List[dict]:
        """获取库存列表"""
        query = select(
            Inventory.id,
            Inventory.warehouse_id,
            Warehouse.name.label("warehouse_name"),
            Inventory.product_id,
            Product.code.label("product_code"),
            Product.name.label("product_name"),
            Product.min_stock,
            Inventory.quantity,
            Inventory.allocated_quantity,
            Inventory.available_quantity,
            Inventory.last_updated,
        ).join(
            Warehouse, Inventory.warehouse_id == Warehouse.id
        ).join(
            Product, Inventory.product_id == Product.id
        )

        if warehouse_id:
            query = query.where(Inventory.warehouse_id == warehouse_id)

        if product_id:
            query = query.where(Inventory.product_id == product_id)

        if low_stock_only:
            query = query.where(
                and_(
                    Product.min_stock.isnot(None),
                    Inventory.available_quantity < Product.min_stock
                )
            )

        query = query.order_by(Inventory.last_updated.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)

        inventories = []
        for row in result.all():
            inventories.append({
                "id": row.id,
                "warehouse_id": row.warehouse_id,
                "warehouse_name": row.warehouse_name,
                "product_id": row.product_id,
                "product_code": row.product_code,
                "product_name": row.product_name,
                "min_stock": row.min_stock,
                "quantity": row.quantity,
                "allocated_quantity": row.allocated_quantity,
                "available_quantity": row.available_quantity,
                "last_updated": row.last_updated,
            })

        return inventories

    async def adjust_inventory(
        self,
        warehouse_id: int,
        product_id: int,
        quantity: Decimal,
        transaction_type: TransactionType,
        reference_type: Optional[str] = None,
        reference_id: Optional[int] = None,
        reference_no: Optional[str] = None,
        notes: Optional[str] = None,
        created_by: Optional[int] = None,
    ) -> Inventory:
        """
        调整库存

        Args:
            warehouse_id: 仓库ID
            product_id: 产品ID
            quantity: 调整数量（正数为入库，负数为出库）
            transaction_type: 流水类型
            reference_type: 关联单据类型
            reference_id: 关联单据ID
            reference_no: 关联单据号
            notes: 备注
            created_by: 创建人ID

        Returns:
            Inventory: 更新后的库存记录
        """
        # 获取或创建库存记录
        result = await self.db.execute(
            select(Inventory).where(
                Inventory.warehouse_id == warehouse_id,
                Inventory.product_id == product_id,
            )
        )
        inventory = result.scalar_one_or_none()

        before_quantity = inventory.quantity if inventory else Decimal(0)

        if inventory:
            # 更新现有库存
            new_quantity = before_quantity + quantity

            if new_quantity < 0:
                raise BadRequestError("库存不足，无法扣减")

            inventory.quantity = new_quantity
            inventory.available_quantity = new_quantity - inventory.allocated_quantity
            inventory.last_updated = datetime.now(timezone.utc)
        else:
            # 创建新库存记录
            if quantity < 0:
                raise BadRequestError("库存不足，无法扣减")

            inventory = Inventory(
                warehouse_id=warehouse_id,
                product_id=product_id,
                quantity=quantity,
                allocated_quantity=Decimal(0),
                available_quantity=quantity,
                last_updated=datetime.now(timezone.utc),
            )
            self.db.add(inventory)
            await self.db.flush()

        after_quantity = inventory.quantity

        # 记录库存流水
        transaction = InventoryTransaction(
            warehouse_id=warehouse_id,
            product_id=product_id,
            transaction_type=transaction_type,
            quantity=quantity,
            before_quantity=before_quantity,
            after_quantity=after_quantity,
            reference_type=reference_type,
            reference_id=reference_id,
            reference_no=reference_no,
            notes=notes,
            created_by=created_by,
        )
        self.db.add(transaction)

        await self.db.commit()
        await self.db.refresh(inventory)

        return inventory

    async def get_transactions(
        self,
        warehouse_id: Optional[int] = None,
        product_id: Optional[int] = None,
        transaction_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[InventoryTransaction]:
        """获取库存流水列表"""
        query = select(InventoryTransaction)

        if warehouse_id:
            query = query.where(InventoryTransaction.warehouse_id == warehouse_id)

        if product_id:
            query = query.where(InventoryTransaction.product_id == product_id)

        if transaction_type:
            query = query.where(InventoryTransaction.transaction_type == transaction_type)

        query = query.order_by(InventoryTransaction.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()


class InventoryTransferService:
    """库存调拨服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_transfer(self, data: InventoryTransferCreate) -> InventoryTransfer:
        """创建库存调拨"""
        # 验证仓库
        warehouse_service = WarehouseService(self.db)
        from_warehouse = await warehouse_service.get_warehouse(data.from_warehouse_id)
        to_warehouse = await warehouse_service.get_warehouse(data.to_warehouse_id)

        if from_warehouse.id == to_warehouse.id:
            raise BadRequestError("调出和调入仓库不能相同")

        # 生成调拨单号
        transfer_no = f"TF-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # 创建调拨单
        transfer = InventoryTransfer(
            transfer_no=transfer_no,
            from_warehouse_id=data.from_warehouse_id,
            to_warehouse_id=data.to_warehouse_id,
            transfer_date=data.transfer_date,
            notes=data.notes,
            status=TransferStatus.DRAFT,
        )
        self.db.add(transfer)
        await self.db.flush()

        # 创建明细
        for item_data in data.items:
            item = InventoryTransferItem(
                transfer_id=transfer.id,
                **item_data.model_dump(),
            )
            self.db.add(item)

        await self.db.commit()
        await self.db.refresh(transfer)

        return transfer

    async def get_transfers(
        self,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[InventoryTransfer]:
        """获取库存调拨列表"""
        query = select(InventoryTransfer).where(InventoryTransfer.is_deleted == False)

        if status:
            query = query.where(InventoryTransfer.status == status)

        query = query.order_by(InventoryTransfer.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_transfer(self, transfer_id: int) -> InventoryTransfer:
        """获取库存调拨详情"""
        result = await self.db.execute(
            select(InventoryTransfer)
            .options(selectinload(InventoryTransfer.items))
            .where(
                InventoryTransfer.id == transfer_id,
                InventoryTransfer.is_deleted == False,
            )
        )
        transfer = result.scalar_one_or_none()

        if not transfer:
            raise NotFoundError("库存调拨不存在")

        return transfer

    async def execute_transfer(self, transfer_id: int) -> InventoryTransfer:
        """执行库存调拨"""
        transfer = await self.get_transfer(transfer_id)

        if transfer.status != TransferStatus.APPROVED:
            raise BadRequestError(f"调拨状态为{transfer.status}，无法执行")

        inventory_service = InventoryService(self.db)

        # 创建明细并执行调拨
        for item in transfer.items:
            # 调出仓库扣减库存
            await inventory_service.adjust_inventory(
                warehouse_id=transfer.from_warehouse_id,
                product_id=item.product_id,
                quantity=-item.quantity,
                transaction_type=TransactionType.TRANSFER_OUT,
                reference_type="InventoryTransfer",
                reference_id=transfer.id,
                reference_no=transfer.transfer_no,
            )

            # 调入仓库增加库存
            await inventory_service.adjust_inventory(
                warehouse_id=transfer.to_warehouse_id,
                product_id=item.product_id,
                quantity=item.quantity,
                transaction_type=TransactionType.TRANSFER_IN,
                reference_type="InventoryTransfer",
                reference_id=transfer.id,
                reference_no=transfer.transfer_no,
            )

        # 更新状态
        transfer.status = TransferStatus.COMPLETED
        transfer.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(transfer)

        return transfer

    async def delete_transfer(self, transfer_id: int) -> None:
        """删除库存调拨（软删除）"""
        transfer = await self.get_transfer(transfer_id)

        if transfer.status not in [TransferStatus.DRAFT, TransferStatus.REJECTED]:
            raise BadRequestError(f"调拨状态为{transfer.status}，无法删除")

        transfer.is_deleted = True
        transfer.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
