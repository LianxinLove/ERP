"""
序列号管理服务层

@description 产品序列号管理的业务逻辑

@services
- SerialNumberService: 序列号管理服务
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.serial_number import (
    ProductSerialNumber,
    SerialNumberTransaction,
    SerialNumberStatus,
)
from app.models.inventory import Product, Warehouse
from app.schemas.serial_number import (
    ProductSerialNumberCreate,
    SerialNumberSale,
    SerialNumberReturn,
    SerialNumberWarranty,
)


class SerialNumberService:
    """
    序列号管理服务类
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_serial_number(self, data: ProductSerialNumberCreate) -> ProductSerialNumber:
        """
        创建序列号

        Args:
            data: 序列号创建数据

        Returns:
            ProductSerialNumber: 创建的序列号

        Raises:
            BadRequestError: 序列号已存在
            NotFoundError: 产品或仓库不存在
        """
        # 检查序列号是否已存在
        result = await self.db.execute(
            select(ProductSerialNumber).where(
                ProductSerialNumber.serial_number == data.serial_number,
                ProductSerialNumber.is_deleted == False,
            )
        )
        if result.scalar_one_or_none():
            raise BadRequestError("序列号已存在")

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

        # 创建序列号
        now = datetime.now(timezone.utc)
        serial = ProductSerialNumber(
            **data.model_dump(),
            status=SerialNumberStatus.IN_STOCK,
            created_at=now,
            updated_at=now,
        )
        self.db.add(serial)

        # 记录初始流水
        await self.db.flush()
        transaction = SerialNumberTransaction(
            serial_number_id=serial.id,
            transaction_type="initial",
            from_status=None,
            to_status=SerialNumberStatus.IN_STOCK,
            reference_type="serial_create",
            notes="序列号创建",
            created_at=now,
        )
        self.db.add(transaction)

        await self.db.commit()
        await self.db.refresh(serial)

        return serial

    async def get_serial_numbers(
        self,
        product_id: Optional[int] = None,
        warehouse_id: Optional[int] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ProductSerialNumber]:
        """
        获取序列号列表

        Args:
            product_id: 产品筛选
            warehouse_id: 仓库筛选
            status: 状态筛选
            keyword: 关键词搜索
            skip: 跳过条数
            limit: 限制条数

        Returns:
            List[ProductSerialNumber]: 序列号列表
        """
        query = select(ProductSerialNumber).where(ProductSerialNumber.is_deleted == False)

        if product_id:
            query = query.where(ProductSerialNumber.product_id == product_id)

        if warehouse_id:
            query = query.where(ProductSerialNumber.warehouse_id == warehouse_id)

        if status:
            query = query.where(ProductSerialNumber.status == status)

        if keyword:
            query = query.where(ProductSerialNumber.serial_number.like(f"%{keyword}%"))

        query = query.order_by(ProductSerialNumber.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_serial_number(self, serial_id: int) -> ProductSerialNumber:
        """
        获取序列号详情

        Args:
            serial_id: 序列号ID

        Returns:
            ProductSerialNumber: 序列号详情

        Raises:
            NotFoundError: 序列号不存在
        """
        result = await self.db.execute(
            select(ProductSerialNumber).where(
                ProductSerialNumber.id == serial_id,
                ProductSerialNumber.is_deleted == False,
            )
        )
        serial = result.scalar_one_or_none()

        if not serial:
            raise NotFoundError("序列号不存在")

        return serial

    async def sale_serial_numbers(self, data: SerialNumberSale) -> List[ProductSerialNumber]:
        """
        销售序列号

        Args:
            data: 销售数据

        Returns:
            List[ProductSerialNumber]: 销售后的序列号列表

        Raises:
            BadRequestError: 序列号状态不允许销售
        """
        sold_serials = []
        now = datetime.now(timezone.utc)

        for serial_id in data.serial_numbers:
            serial = await self.get_serial_number(serial_id)

            if serial.status != SerialNumberStatus.IN_STOCK:
                raise BadRequestError(f"序列号 {serial.serial_number} 状态为{serial.status}，无法销售")

            from_status = serial.status
            serial.status = SerialNumberStatus.SOLD
            serial.customer_id = data.customer_id
            serial.sale_date = data.sale_date
            serial.updated_at = now

            # 记录流水
            transaction = SerialNumberTransaction(
                serial_number_id=serial.id,
                transaction_type="sale",
                from_status=from_status,
                to_status=SerialNumberStatus.SOLD,
                reference_type="sale",
                reference_id=data.order_id,
                customer_id=data.customer_id,
                notes=data.notes or "销售",
                created_at=now,
            )
            self.db.add(transaction)

            sold_serials.append(serial)

        await self.db.commit()
        for serial in sold_serials:
            await self.db.refresh(serial)

        return sold_serials

    async def return_serial_number(self, serial_id: int, data: SerialNumberReturn) -> ProductSerialNumber:
        """
        序列号退货

        Args:
            serial_id: 序列号ID
            data: 退货数据

        Returns:
            ProductSerialNumber: 退货后的序列号

        Raises:
            NotFoundError: 序列号不存在
            BadRequestError: 序列号状态不允许退货
        """
        serial = await self.get_serial_number(serial_id)

        if serial.status != SerialNumberStatus.SOLD:
            raise BadRequestError(f"序列号状态为{serial.status}，无法退货")

        from_status = serial.status
        serial.status = SerialNumberStatus.RETURNED
        serial.updated_at = datetime.now(timezone.utc)

        # 记录流水
        transaction = SerialNumberTransaction(
            serial_number_id=serial.id,
            transaction_type="return",
            from_status=from_status,
            to_status=SerialNumberStatus.RETURNED,
            reference_type="return",
            notes=data.reason or data.notes or "退货",
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(transaction)

        await self.db.commit()
        await self.db.refresh(serial)

        return serial

    async def update_warranty(self, serial_id: int, data: SerialNumberWarranty) -> ProductSerialNumber:
        """
        更新序列号保修信息

        Args:
            serial_id: 序列号ID
            data: 保修数据

        Returns:
            ProductSerialNumber: 更新后的序列号

        Raises:
            NotFoundError: 序列号不存在
        """
        serial = await self.get_serial_number(serial_id)

        serial.warranty_expiry = data.warranty_expiry
        serial.warranty_notes = data.warranty_notes
        if data.notes:
            serial.notes = data.notes
        serial.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(serial)

        return serial

    async def get_warranty_alerts(
        self,
        days_threshold: int = 30,
        skip: int = 0,
        limit: int = 100,
    ) -> List[dict]:
        """
        获取即将过保的序列号列表

        Args:
            days_threshold: 天数阈值（默认30天）
            skip: 跳过条数
            limit: 限制条数

        Returns:
            List[dict]: 即将过保的序列号列表
        """
        threshold_date = datetime.now(timezone.utc) + timedelta(days=days_threshold)

        query = select(ProductSerialNumber).where(
            and_(
                ProductSerialNumber.is_deleted == False,
                ProductSerialNumber.status.in_([
                    SerialNumberStatus.SOLD,
                    SerialNumberStatus.WARRANTY,
                ]),
                ProductSerialNumber.warranty_expiry != None,
                ProductSerialNumber.warranty_expiry <= threshold_date,
            )
        )

        query = query.order_by(ProductSerialNumber.warranty_expiry.asc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        serials = result.scalars().all()

        alerts = []
        for serial in serials:
            days_to_expiry = (serial.warranty_expiry - datetime.now(timezone.utc)).days
            alerts.append({
                "serial_number_id": serial.id,
                "serial_number": serial.serial_number,
                "product_id": serial.product_id,
                "customer_id": serial.customer_id,
                "warranty_expiry": serial.warranty_expiry,
                "days_to_expiry": days_to_expiry,
                "is_expired": days_to_expiry < 0,
                "status": serial.status,
            })

        return alerts

    async def get_serial_number_transactions(
        self,
        serial_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[SerialNumberTransaction]:
        """
        获取序列号流水列表

        Args:
            serial_id: 序列号ID
            skip: 跳过条数
            limit: 限制条数

        Returns:
            List[SerialNumberTransaction]: 序列号流水列表
        """
        query = select(SerialNumberTransaction).where(
            SerialNumberTransaction.serial_number_id == serial_id
        )

        query = query.order_by(SerialNumberTransaction.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def trace_serial_number(self, serial_id: int) -> dict:
        """
        追溯序列号完整历史

        Args:
            serial_id: 序列号ID

        Returns:
            dict: 序列号完整追溯信息
        """
        serial = await self.get_serial_number(serial_id)

        # 获取所有流水记录
        transactions_result = await self.db.execute(
            select(SerialNumberTransaction)
            .where(SerialNumberTransaction.serial_number_id == serial_id)
            .order_by(SerialNumberTransaction.created_at.asc())
        )
        transactions = transactions_result.scalars().all()

        return {
            "serial_number": {
                "id": serial.id,
                "serial_number": serial.serial_number,
                "product_id": serial.product_id,
                "warehouse_id": serial.warehouse_id,
                "batch_id": serial.batch_id,
                "production_date": serial.production_date,
                "cost_price": serial.cost_price,
                "supplier_id": serial.supplier_id,
                "receipt_id": serial.receipt_id,
                "status": serial.status,
                "customer_id": serial.customer_id,
                "sale_date": serial.sale_date,
                "warranty_expiry": serial.warranty_expiry,
                "created_at": serial.created_at,
            },
            "transactions": [
                {
                    "id": t.id,
                    "transaction_type": t.transaction_type,
                    "from_status": t.from_status,
                    "to_status": t.to_status,
                    "reference_type": t.reference_type,
                    "reference_id": t.reference_id,
                    "reference_no": t.reference_no,
                    "customer_id": t.customer_id,
                    "notes": t.notes,
                    "created_at": t.created_at,
                }
                for t in transactions
            ],
        }
