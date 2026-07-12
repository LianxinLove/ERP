"""
批号管理服务层

@description 批号追踪和有效期管理的业务逻辑

@services
- BatchService: 批号管理服务
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.batch import (
    InventoryBatch,
    BatchTransaction,
    BatchStatus,
)
from app.models.inventory import Product, Warehouse
from app.schemas.batch import (
    InventoryBatchCreate,
    InventoryBatchUpdate,
    BatchAdjustment,
    BatchTransfer,
)


class BatchService:
    """
    批号管理服务类
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_batch(self, data: InventoryBatchCreate) -> InventoryBatch:
        """
        创建批号

        Args:
            data: 批号创建数据

        Returns:
            InventoryBatch: 创建的批号

        Raises:
            BadRequestError: 批号已存在
            NotFoundError: 产品或仓库不存在
        """
        # 检查批号是否已存在
        result = await self.db.execute(
            select(InventoryBatch).where(
                InventoryBatch.batch_no == data.batch_no,
                InventoryBatch.is_deleted == False,
            )
        )
        if result.scalar_one_or_none():
            raise BadRequestError("批号已存在")

        # 验证产品和仓库存在
        product_result = await self.db.execute(
            select(Product).where(Product.id == data.product_id)
        )
        if not product_result.scalar_one_or_none():
            raise NotFoundError("产品不存在")

        warehouse_result = await self.db.execute(
            select(Warehouse).where(Warehouse.id == data.warehouse_id)
        )
        if not warehouse_result.scalar_one_or_none():
            raise NotFoundError("仓库不存在")

        # 检查是否过期
        status = BatchStatus.ACTIVE
        if data.expiry_date and data.expiry_date < datetime.now(timezone.utc):
            status = BatchStatus.EXPIRED

        # 创建批号
        now = datetime.now(timezone.utc)
        batch = InventoryBatch(
            **data.model_dump(),
            available_quantity=data.quantity,
            status=status,
            created_at=now,
            updated_at=now,
        )
        self.db.add(batch)

        # 记录初始流水
        await self.db.flush()
        transaction = BatchTransaction(
            batch_id=batch.id,
            transaction_type="initial",
            quantity=data.quantity,
            before_quantity=Decimal(0),
            after_quantity=data.quantity,
            reference_type="batch_create",
            notes="初始入库",
            created_at=now,
        )
        self.db.add(transaction)

        await self.db.commit()
        await self.db.refresh(batch)

        return batch

    async def get_batches(
        self,
        product_id: Optional[int] = None,
        warehouse_id: Optional[int] = None,
        status: Optional[str] = None,
        include_expired: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> List[InventoryBatch]:
        """
        获取批号列表

        Args:
            product_id: 产品筛选
            warehouse_id: 仓库筛选
            status: 状态筛选
            include_expired: 是否包含已过期
            skip: 跳过条数
            limit: 限制条数

        Returns:
            List[InventoryBatch]: 批号列表
        """
        query = select(InventoryBatch).where(InventoryBatch.is_deleted == False)

        if product_id:
            query = query.where(InventoryBatch.product_id == product_id)

        if warehouse_id:
            query = query.where(InventoryBatch.warehouse_id == warehouse_id)

        if status:
            query = query.where(InventoryBatch.status == status)

        if not include_expired:
            query = query.where(
                or_(
                    InventoryBatch.expiry_date == None,
                    InventoryBatch.expiry_date > datetime.now(timezone.utc),
                )
            )

        query = query.order_by(InventoryBatch.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_batch(self, batch_id: int) -> InventoryBatch:
        """
        获取批号详情

        Args:
            batch_id: 批号ID

        Returns:
            InventoryBatch: 批号详情

        Raises:
            NotFoundError: 批号不存在
        """
        result = await self.db.execute(
            select(InventoryBatch).where(
                InventoryBatch.id == batch_id,
                InventoryBatch.is_deleted == False,
            )
        )
        batch = result.scalar_one_or_none()

        if not batch:
            raise NotFoundError("批号不存在")

        return batch

    async def adjust_batch(self, batch_id: int, data: BatchAdjustment) -> InventoryBatch:
        """
        调整批号数量

        Args:
            batch_id: 批号ID
            data: 调整数据

        Returns:
            InventoryBatch: 调整后的批号

        Raises:
            NotFoundError: 批号不存在
            BadRequestError: 调整数量不合法
        """
        batch = await self.get_batch(batch_id)

        adjust_quantity = data.adjust_quantity
        new_quantity = batch.quantity + adjust_quantity

        if new_quantity < 0:
            raise BadRequestError("调整后数量不能为负数")
        if new_quantity < batch.available_quantity:
            raise BadRequestError("调整后数量不能小于已分配数量")

        before_quantity = batch.quantity
        batch.quantity = new_quantity
        batch.available_quantity = batch.available_quantity + adjust_quantity
        batch.updated_at = datetime.now(timezone.utc)

        # 记录流水
        transaction = BatchTransaction(
            batch_id=batch.id,
            transaction_type="adjustment",
            quantity=adjust_quantity,
            before_quantity=before_quantity,
            after_quantity=new_quantity,
            reference_type="batch_adjustment",
            notes=data.notes or "批号调整",
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(transaction)

        await self.db.commit()
        await self.db.refresh(batch)

        return batch

    async def transfer_batch(self, batch_id: int, data: BatchTransfer) -> InventoryBatch:
        """
        批号调拨

        Args:
            batch_id: 源批号ID
            data: 调拨数据

        Returns:
            InventoryBatch: 新创建的目标批号

        Raises:
            NotFoundError: 批号或目标仓库不存在
            BadRequestError: 调拨数量不合法
        """
        source_batch = await self.get_batch(batch_id)

        if data.quantity > source_batch.available_quantity:
            raise BadRequestError("调拨数量不能超过可用数量")

        # 验证目标仓库
        target_warehouse_result = await self.db.execute(
            select(Warehouse).where(Warehouse.id == data.to_warehouse_id)
        )
        if not target_warehouse_result.scalar_one_or_none():
            raise NotFoundError("目标仓库不存在")

        # 生成新批号
        new_batch_no = data.new_batch_no or f"{source_batch.batch_no}-T"
        now = datetime.now(timezone.utc)

        # 创建目标批号
        target_batch = InventoryBatch(
            batch_no=new_batch_no,
            product_id=source_batch.product_id,
            warehouse_id=data.to_warehouse_id,
            quantity=data.quantity,
            available_quantity=data.quantity,
            production_date=source_batch.production_date,
            expiry_date=source_batch.expiry_date,
            supplier_id=source_batch.supplier_id,
            cost_price=source_batch.cost_price,
            status=source_batch.status,
            notes=data.notes or f"从仓库{source_batch.warehouse_id}调拨",
            created_at=now,
            updated_at=now,
        )
        self.db.add(target_batch)
        await self.db.flush()

        # 更新源批号
        source_batch.available_quantity -= data.quantity
        source_batch.updated_at = now

        # 记录源批号流水
        source_transaction = BatchTransaction(
            batch_id=source_batch.id,
            transaction_type="transfer_out",
            quantity=-data.quantity,
            before_quantity=source_batch.quantity,
            after_quantity=source_batch.quantity,
            reference_type="batch_transfer",
            reference_id=target_batch.id,
            notes=f"调拨到仓库{data.to_warehouse_id}",
            created_at=now,
        )
        self.db.add(source_transaction)

        # 记录目标批号流水
        target_transaction = BatchTransaction(
            batch_id=target_batch.id,
            transaction_type="transfer_in",
            quantity=data.quantity,
            before_quantity=Decimal(0),
            after_quantity=data.quantity,
            reference_type="batch_transfer",
            reference_id=source_batch.id,
            notes=f"从仓库{source_batch.warehouse_id}调拨",
            created_at=now,
        )
        self.db.add(target_transaction)

        await self.db.commit()
        await self.db.refresh(target_batch)

        return target_batch

    async def get_expiry_alerts(
        self,
        days_threshold: int = 30,
        skip: int = 0,
        limit: int = 100,
    ) -> List[dict]:
        """
        获取即将过期的批号列表

        Args:
            days_threshold: 天数阈值（默认30天）
            skip: 跳过条数
            limit: 限制条数

        Returns:
            List[dict]: 即将过期的批号列表
        """
        threshold_date = datetime.now(timezone.utc) + timedelta(days=days_threshold)

        query = select(InventoryBatch).where(
            and_(
                InventoryBatch.is_deleted == False,
                InventoryBatch.status == BatchStatus.ACTIVE,
                InventoryBatch.expiry_date != None,
                InventoryBatch.expiry_date <= threshold_date,
            )
        )

        query = query.order_by(InventoryBatch.expiry_date.asc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        batches = result.scalars().all()

        alerts = []
        for batch in batches:
            days_to_expiry = (batch.expiry_date - datetime.now(timezone.utc)).days
            alerts.append({
                "batch_id": batch.id,
                "batch_no": batch.batch_no,
                "product_id": batch.product_id,
                "warehouse_id": batch.warehouse_id,
                "expiry_date": batch.expiry_date,
                "days_to_expiry": days_to_expiry,
                "quantity": batch.quantity,
                "is_expired": days_to_expiry < 0,
            })

        return alerts

    async def update_expired_batches(self) -> int:
        """
        更新过期批号状态

        Returns:
            int: 更新的批号数量
        """
        now = datetime.now(timezone.utc)

        result = await self.db.execute(
            select(InventoryBatch).where(
                and_(
                    InventoryBatch.is_deleted == False,
                    InventoryBatch.status == BatchStatus.ACTIVE,
                    InventoryBatch.expiry_date != None,
                    InventoryBatch.expiry_date < now,
                )
            )
        )
        expired_batches = result.scalars().all()

        count = 0
        for batch in expired_batches:
            batch.status = BatchStatus.EXPIRED
            batch.updated_at = now
            count += 1

        await self.db.commit()
        return count

    async def get_batch_transactions(
        self,
        batch_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[BatchTransaction]:
        """
        获取批号流水列表

        Args:
            batch_id: 批号ID
            skip: 跳过条数
            limit: 限制条数

        Returns:
            List[BatchTransaction]: 批号流水列表
        """
        query = select(BatchTransaction).where(
            BatchTransaction.batch_id == batch_id
        )

        query = query.order_by(BatchTransaction.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()
