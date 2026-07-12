"""
库存盘点服务层

@description 库存盘点单的业务逻辑

@services
- StockCountService: 盘点单服务
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.stock_count import (
    StockCount,
    StockCountItem,
    StockCountDifference,
    StockCountStatus,
    DifferenceStatus,
)
from app.models.inventory import Warehouse, Product, Inventory, InventoryTransaction, TransactionType
from app.schemas.stock_count import (
    StockCountCreate,
    StockCountApprove,
    StockCountComplete,
    DifferenceHandle,
)


class StockCountService:
    """
    盘点单服务类
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_stock_count(self, data: StockCountCreate, operator_id: int) -> StockCount:
        """
        创建盘点单

        Args:
            data: 盘点单创建数据
            operator_id: 操作人ID

        Returns:
            StockCount: 创建的盘点单

        Raises:
            NotFoundError: 仓库不存在
            BadRequestError: 产品不存在于指定仓库
        """
        # 验证仓库存在
        warehouse_result = await self.db.execute(
            select(Warehouse).where(Warehouse.id == data.warehouse_id)
        )
        if not warehouse_result.scalar_one_or_none():
            raise NotFoundError("仓库不存在")

        # 生成盘点单号
        count_no = f"SC-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # 创建盘点单
        now = datetime.now(timezone.utc)
        stock_count = StockCount(
            count_no=count_no,
            warehouse_id=data.warehouse_id,
            count_date=data.count_date,
            count_type=data.count_type or "full",
            operator_id=operator_id,
            reviewer_id=data.reviewer_id,
            notes=data.notes,
            status=StockCountStatus.DRAFT,
            created_at=now,
            updated_at=now,
        )
        self.db.add(stock_count)
        await self.db.flush()

        # 验证产品并创建明细
        total_items = 0
        total_quantity = Decimal(0)
        total_difference = Decimal(0)

        for item_data in data.items:
            # 验证产品存在于该仓库
            inventory_result = await self.db.execute(
                select(Inventory).where(
                    Inventory.warehouse_id == data.warehouse_id,
                    Inventory.product_id == item_data.product_id,
                )
            )
            inventory = inventory_result.scalar_one_or_none()

            system_quantity = inventory.quantity if inventory else Decimal(0)

            # 创建明细
            item = StockCountItem(
                count_id=stock_count.id,
                product_id=item_data.product_id,
                system_quantity=system_quantity,
                counted_quantity=item_data.counted_quantity,
                difference_quantity=item_data.counted_quantity - system_quantity,
                location=item_data.location,
                batch_no=item_data.batch_no,
                serial_number=item_data.serial_number,
                notes=item_data.notes,
            )
            self.db.add(item)

            total_items += 1
            total_quantity += system_quantity
            total_difference += item_data.counted_quantity - system_quantity

        # 更新盘点单汇总
        stock_count.total_items = total_items
        stock_count.total_quantity = total_quantity
        stock_count.counted_quantity = total_quantity + total_difference
        stock_count.difference_quantity = total_difference

        await self.db.commit()
        await self.db.refresh(stock_count)

        return stock_count

    async def get_stock_counts(
        self,
        warehouse_id: Optional[int] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[StockCount]:
        """
        获取盘点单列表

        Args:
            warehouse_id: 仓库筛选
            status: 状态筛选
            keyword: 关键词搜索
            skip: 跳过条数
            limit: 限制条数

        Returns:
            List[StockCount]: 盘点单列表
        """
        query = select(StockCount).where(StockCount.is_deleted == False)

        if warehouse_id:
            query = query.where(StockCount.warehouse_id == warehouse_id)

        if status:
            query = query.where(StockCount.status == status)

        if keyword:
            query = query.where(StockCount.count_no.like(f"%{keyword}%"))

        query = query.order_by(StockCount.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_stock_count(self, count_id: int) -> StockCount:
        """
        获取盘点单详情

        Args:
            count_id: 盘点单ID

        Returns:
            StockCount: 盘点单详情

        Raises:
            NotFoundError: 盘点单不存在
        """
        result = await self.db.execute(
            select(StockCount)
            .options(selectinload(StockCount.items))
            .where(
                StockCount.id == count_id,
                StockCount.is_deleted == False,
            )
        )
        stock_count = result.scalar_one_or_none()

        if not stock_count:
            raise NotFoundError("盘点单不存在")

        return stock_count

    async def approve_stock_count(
        self, count_id: int, data: StockCountApprove
    ) -> StockCount:
        """
        审核盘点单

        Args:
            count_id: 盘点单ID
            data: 审核数据

        Returns:
            StockCount: 审核后的盘点单

        Raises:
            NotFoundError: 盘点单不存在
            BadRequestError: 盘点单状态不允许审核
        """
        stock_count = await self.get_stock_count(count_id)

        if stock_count.status != StockCountStatus.PENDING:
            raise BadRequestError(f"盘点单状态为{stock_count.status}，无法审核")

        if data.approved:
            stock_count.status = StockCountStatus.APPROVED
        else:
            stock_count.status = StockCountStatus.CANCELLED

        stock_count.reviewed_at = datetime.now(timezone.utc)
        stock_count.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(stock_count)

        return stock_count

    async def complete_stock_count(
        self, count_id: int, data: StockCountComplete
    ) -> StockCount:
        """
        完成盘点单

        Args:
            count_id: 盘点单ID
            data: 完成数据

        Returns:
            StockCount: 完成后的盘点单

        Raises:
            NotFoundError: 盘点单不存在
            BadRequestError: 盘点单状态不允许完成
        """
        stock_count = await self.get_stock_count(count_id)

        if stock_count.status not in [StockCountStatus.APPROVED, StockCountStatus.IN_PROGRESS]:
            raise BadRequestError(f"盘点单状态为{stock_count.status}，无法完成")

        # 创建差异记录
        now = datetime.now(timezone.utc)
        for item in stock_count.items:
            if item.difference_quantity != 0:
                adjust_type = "profit" if item.difference_quantity > 0 else "loss"

                # 创建差异记录
                difference = StockCountDifference(
                    count_id=count_id,
                    item_id=item.id,
                    product_id=item.product_id,
                    difference_quantity=item.difference_quantity,
                    difference_amount=item.difference_amount,
                    adjust_type=adjust_type,
                    status=DifferenceStatus.PENDING,
                    notes=data.notes,
                )
                self.db.add(difference)

                # 自动调整库存
                if data.auto_adjust:
                    await self._adjust_inventory(
                        stock_count.warehouse_id,
                        item.product_id,
                        item.difference_quantity,
                        f"盘点单{stock_count.count_no}自动调整",
                    )
                    difference.status = DifferenceStatus.AUTO_ADJUSTED
                    difference.handled_at = now

        stock_count.status = StockCountStatus.COMPLETED
        stock_count.completed_at = now
        stock_count.updated_at = now

        await self.db.commit()
        await self.db.refresh(stock_count)

        return stock_count

    async def handle_difference(
        self, difference_id: int, data: DifferenceHandle, handler_id: int
    ) -> StockCountDifference:
        """
        处理盘点差异

        Args:
            difference_id: 差异ID
            data: 处理数据
            handler_id: 处理人ID

        Returns:
            StockCountDifference: 处理后的差异记录

        Raises:
            NotFoundError: 差异记录不存在
            BadRequestError: 差异状态不允许处理
        """
        result = await self.db.execute(
            select(StockCountDifference).where(
                StockCountDifference.id == difference_id
            )
        )
        difference = result.scalar_one_or_none()

        if not difference:
            raise NotFoundError("差异记录不存在")

        if difference.status != DifferenceStatus.PENDING:
            raise BadRequestError(f"差异状态为{difference.status}，无法处理")

        if data.approved:
            # 获取盘点单信息
            stock_count_result = await self.db.execute(
                select(StockCount).where(StockCount.id == difference.count_id)
            )
            stock_count = stock_count_result.scalar_one_or_none()

            if stock_count:
                # 调整库存
                await self._adjust_inventory(
                    stock_count.warehouse_id,
                    difference.product_id,
                    difference.difference_quantity,
                    f"盘点差异处理 - {data.notes or ''}",
                )

            difference.status = DifferenceStatus.APPROVED
        else:
            difference.status = DifferenceStatus.REJECTED

        difference.handled_by = handler_id
        difference.handled_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(difference)

        return difference

    async def _adjust_inventory(
        self, warehouse_id: int, product_id: int, quantity: Decimal, notes: str
    ) -> None:
        """
        调整库存

        Args:
            warehouse_id: 仓库ID
            product_id: 产品ID
            quantity: 调整数量（正数增加，负数减少）
            notes: 调整备注
        """
        # 获取当前库存
        result = await self.db.execute(
            select(Inventory).where(
                Inventory.warehouse_id == warehouse_id,
                Inventory.product_id == product_id,
            )
        )
        inventory = result.scalar_one_or_none()

        if inventory:
            before_quantity = inventory.quantity
            inventory.quantity += quantity
            inventory.available_quantity += quantity
            inventory.last_updated = datetime.now(timezone.utc)
            after_quantity = inventory.quantity
        else:
            # 创建新库存记录
            before_quantity = Decimal(0)
            after_quantity = quantity
            inventory = Inventory(
                warehouse_id=warehouse_id,
                product_id=product_id,
                quantity=quantity,
                available_quantity=quantity,
                last_updated=datetime.now(timezone.utc),
            )
            self.db.add(inventory)

        # 记录库存流水
        transaction_type = TransactionType.ADJUSTMENT_IN if quantity > 0 else TransactionType.ADJUSTMENT_OUT
        transaction = InventoryTransaction(
            warehouse_id=warehouse_id,
            product_id=product_id,
            transaction_type=transaction_type,
            quantity=quantity,
            before_quantity=before_quantity,
            after_quantity=after_quantity,
            reference_type="stock_count",
            notes=notes,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(transaction)

    async def get_summary(self) -> dict:
        """
        获取盘点汇总统计

        Returns:
            dict: 盘点汇总数据
        """
        # 统计各状态盘点单数量
        result = await self.db.execute(
            select(
                func.count(StockCount.id).label("total"),
                func.sum(
                    func.case(
                        (StockCount.status == StockCountStatus.IN_PROGRESS, 1),
                        else_=0,
                    )
                ).label("in_progress"),
                func.sum(
                    func.case(
                        (StockCount.status == StockCountStatus.COMPLETED, 1),
                        else_=0,
                    )
                ).label("completed"),
            ).where(StockCount.is_deleted == False)
        )
        stats = result.one()

        # 统计差异
        diff_result = await self.db.execute(
            select(
                func.sum(StockCount.difference_quantity).label("total_diff_qty"),
                func.sum(StockCount.difference_amount).label("total_diff_amt"),
            ).where(StockCount.is_deleted == False)
        )
        diff_stats = diff_result.one()

        # 待处理差异数
        pending_result = await self.db.execute(
            select(func.count(StockCountDifference.id)).where(
                StockCountDifference.status == DifferenceStatus.PENDING
            )
        )
        pending_count = pending_result.scalar() or 0

        return {
            "total_counts": stats.total or 0,
            "in_progress_counts": stats.in_progress or 0,
            "completed_counts": stats.completed or 0,
            "total_difference_quantity": diff_stats.total_diff_qty or Decimal(0),
            "total_difference_amount": diff_stats.total_diff_amt or Decimal(0),
            "pending_differences": pending_count,
        }
