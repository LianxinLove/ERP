"""
销售管理服务层

@description 销售模块的业务逻辑

@services
- CustomerService: 客户服务
- SalesOrderService: 销售订单服务
- SalesReturnService: 销售退货服务
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.sales import (
    Customer,
    CustomerStatus,
    SalesOrder,
    SalesOrderStatus,
    SalesOrderItem,
    SalesReturn,
    SalesReturnStatus,
    SalesReturnItem,
    DeliveryOrder,
    DeliveryOrderStatus,
    DeliveryOrderItem,
)
from app.schemas.sales import (
    CustomerCreate,
    CustomerUpdate,
    SalesOrderCreate,
    SalesOrderUpdate,
    SalesReturnCreate,
    SalesReturnUpdate,
)


class CustomerService:
    """
    客户服务类
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_customer(self, data: CustomerCreate) -> Customer:
        """创建客户"""
        # 检查编码是否已存在
        result = await self.db.execute(
            select(Customer).where(
                Customer.code == data.code,
                Customer.is_deleted == False,
            )
        )
        if result.scalar_one_or_none():
            raise BadRequestError("客户编码已存在")

        now = datetime.now(timezone.utc)
        customer = Customer(
            **data.model_dump(),
            created_at=now,
            updated_at=now,
        )
        self.db.add(customer)
        await self.db.commit()
        await self.db.refresh(customer)

        return customer

    async def get_customers(
        self,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Customer]:
        """获取客户列表"""
        query = select(Customer).where(Customer.is_deleted == False)

        if status:
            query = query.where(Customer.status == status)

        if keyword:
            query = query.where(
                or_(
                    Customer.code.like(f"%{keyword}%"),
                    Customer.name.like(f"%{keyword}%"),
                    Customer.contact.like(f"%{keyword}%"),
                )
            )

        query = query.order_by(Customer.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_customer(self, customer_id: int) -> Customer:
        """获取客户详情"""
        result = await self.db.execute(
            select(Customer).where(
                Customer.id == customer_id,
                Customer.is_deleted == False,
            )
        )
        customer = result.scalar_one_or_none()

        if not customer:
            raise NotFoundError("客户不存在")

        return customer

    async def update_customer(self, customer_id: int, data: CustomerUpdate) -> Customer:
        """更新客户"""
        customer = await self.get_customer(customer_id)

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(customer, field, value)

        customer.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(customer)

        return customer

    async def delete_customer(self, customer_id: int) -> None:
        """删除客户（软删除）"""
        customer = await self.get_customer(customer_id)

        # 检查是否有关联的销售订单
        result = await self.db.execute(
            select(func.count(SalesOrder.id)).where(
                SalesOrder.customer_id == customer_id,
                SalesOrder.is_deleted == False,
            )
        )
        count = result.scalar()

        if count > 0:
            raise BadRequestError("该客户存在关联的销售订单，无法删除")

        customer.is_deleted = True
        customer.updated_at = datetime.now(timezone.utc)
        await self.db.commit()


class SalesOrderService:
    """
    销售订单服务类
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_order(self, data: SalesOrderCreate) -> SalesOrder:
        """创建销售订单"""
        # 验证客户
        customer_service = CustomerService(self.db)
        await customer_service.get_customer(data.customer_id)

        # 生成订单号
        order_no = f"SO-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # 计算总金额和税额
        total_amount = Decimal(0)
        tax_amount = Decimal(0)

        for item_data in data.items:
            # 计算明细金额（考虑折扣）
            item_amount = (item_data.unit_price or 0) * item_data.quantity
            if item_data.discount_rate:
                item_amount = item_amount * (1 - item_data.discount_rate / 100)
            total_amount += item_amount

            # 计算税额
            if data.tax_inclusive and item_data.tax_rate:
                tax_amount += item_amount - (item_amount / (1 + item_data.tax_rate / 100))
            elif item_data.tax_rate:
                tax_amount += item_amount * (item_data.tax_rate / 100)

        # 扣除折扣金额
        if data.discount_amount:
            total_amount -= data.discount_amount

        # 创建销售订单
        now = datetime.now(timezone.utc)
        order = SalesOrder(
            order_no=order_no,
            customer_id=data.customer_id,
            order_date=data.order_date,
            delivery_date=data.delivery_date,
            total_amount=total_amount,
            tax_amount=tax_amount,
            tax_inclusive=data.tax_inclusive or False,
            discount_amount=data.discount_amount,
            payment_terms=data.payment_terms,
            delivery_address=data.delivery_address,
            contact=data.contact,
            contact_phone=data.contact_phone,
            salesperson_id=data.salesperson_id,
            notes=data.notes,
            status=SalesOrderStatus.DRAFT,
            created_at=now,
            updated_at=now,
        )
        self.db.add(order)
        await self.db.flush()

        # 创建明细
        for item_data in data.items:
            item = SalesOrderItem(
                order_id=order.id,
                **item_data.model_dump(),
            )
            self.db.add(item)

        await self.db.commit()
        await self.db.refresh(order)

        return order

    async def get_orders(
        self,
        customer_id: Optional[int] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[SalesOrder]:
        """获取销售订单列表"""
        query = select(SalesOrder).where(SalesOrder.is_deleted == False)

        if customer_id:
            query = query.where(SalesOrder.customer_id == customer_id)

        if status:
            query = query.where(SalesOrder.status == status)

        if keyword:
            query = query.where(SalesOrder.order_no.like(f"%{keyword}%"))

        query = query.order_by(SalesOrder.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_order(self, order_id: int) -> SalesOrder:
        """获取销售订单详情"""
        result = await self.db.execute(
            select(SalesOrder)
            .options(
                selectinload(SalesOrder.items),
                selectinload(SalesOrder.customer),
            )
            .where(
                SalesOrder.id == order_id,
                SalesOrder.is_deleted == False,
            )
        )
        order = result.scalar_one_or_none()

        if not order:
            raise NotFoundError("销售订单不存在")

        return order

    async def update_order(self, order_id: int, data: SalesOrderUpdate) -> SalesOrder:
        """更新销售订单"""
        order = await self.get_order(order_id)

        if order.status != SalesOrderStatus.DRAFT:
            raise BadRequestError(f"订单状态为{order.status}，无法修改")

        # 更新基本信息
        update_data = data.model_dump(exclude_unset=True, exclude={"items"})
        for field, value in update_data.items():
            setattr(order, field, value)

        # 更新明细
        if data.items is not None:
            # 删除旧明细
            for old_item in order.items:
                await self.db.delete(old_item)

            try:
                # 添加新明细
                total_amount = Decimal(0)
                tax_amount = Decimal(0)

                for item_data in data.items:
                    item = SalesOrderItem(
                        order_id=order.id,
                        **item_data.model_dump(),
                    )
                    self.db.add(item)

                    # 计算金额
                    item_amount = (item_data.unit_price or 0) * item_data.quantity
                    if item_data.discount_rate:
                        item_amount = item_amount * (1 - item_data.discount_rate / 100)
                    total_amount += item_amount

                    # 计算税额
                    if data.tax_inclusive and item_data.tax_rate:
                        tax_amount += item_amount - (item_amount / (1 + item_data.tax_rate / 100))
                    elif item_data.tax_rate:
                        tax_amount += item_amount * (item_data.tax_rate / 100)

                # 扣除折扣金额
                if data.discount_amount:
                    total_amount -= data.discount_amount

                order.total_amount = total_amount
                order.tax_amount = tax_amount

                order.updated_at = datetime.now(timezone.utc)
                await self.db.commit()
                await self.db.refresh(order)
            except Exception:
                # 回滚事务，避免数据不一致
                await self.db.rollback()
                raise

        return order

    async def confirm_order(self, order_id: int) -> SalesOrder:
        """确认销售订单"""
        order = await self.get_order(order_id)

        if order.status != SalesOrderStatus.DRAFT:
            raise BadRequestError(f"订单状态为{order.status}，无法确认")

        order.status = SalesOrderStatus.CONFIRMED
        order.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(order)

        return order

    async def cancel_order(self, order_id: int) -> SalesOrder:
        """取消销售订单"""
        order = await self.get_order(order_id)

        if order.status in [SalesOrderStatus.SHIPPED, SalesOrderStatus.PAID, SalesOrderStatus.CLOSED]:
            raise BadRequestError(f"订单状态为{order.status}，无法取消")

        order.status = SalesOrderStatus.CANCELLED
        order.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(order)

        return order

    async def delete_order(self, order_id: int) -> None:
        """删除销售订单（软删除）"""
        order = await self.get_order(order_id)

        if order.status != SalesOrderStatus.DRAFT:
            raise BadRequestError(f"订单状态为{order.status}，无法删除")

        order.is_deleted = True
        order.updated_at = datetime.now(timezone.utc)
        await self.db.commit()


class SalesReturnService:
    """
    销售退货服务类
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_return(self, data: SalesReturnCreate) -> SalesReturn:
        """创建销售退货"""
        # 验证客户
        customer_service = CustomerService(self.db)
        await customer_service.get_customer(data.customer_id)

        # 验证原销售订单
        if data.order_id:
            order_service = SalesOrderService(self.db)
            order = await order_service.get_order(data.order_id)

            if order.customer_id != data.customer_id:
                raise BadRequestError("退货客户与原订单客户不一致")

        # 生成退货单号
        return_no = f"SR-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # 计算总金额
        total_amount = sum(
            (item.unit_price or 0) * item.quantity
            for item in data.items
        )

        # 创建销售退货
        now = datetime.now(timezone.utc)
        sales_return = SalesReturn(
            return_no=return_no,
            customer_id=data.customer_id,
            order_id=data.order_id,
            return_date=data.return_date,
            reason=data.reason,
            total_amount=total_amount,
            refund_amount=total_amount,
            notes=data.notes,
            status=SalesReturnStatus.DRAFT,
            created_at=now,
            updated_at=now,
        )
        self.db.add(sales_return)
        await self.db.flush()

        # 创建明细
        for item_data in data.items:
            item = SalesReturnItem(
                return_id=sales_return.id,
                **item_data.model_dump(),
            )
            self.db.add(item)

        await self.db.commit()
        await self.db.refresh(sales_return)

        return sales_return

    async def get_returns(
        self,
        customer_id: Optional[int] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[SalesReturn]:
        """获取销售退货列表"""
        query = select(SalesReturn).where(SalesReturn.is_deleted == False)

        if customer_id:
            query = query.where(SalesReturn.customer_id == customer_id)

        if status:
            query = query.where(SalesReturn.status == status)

        if keyword:
            query = query.where(SalesReturn.return_no.like(f"%{keyword}%"))

        query = query.order_by(SalesReturn.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_return(self, return_id: int) -> SalesReturn:
        """获取销售退货详情"""
        result = await self.db.execute(
            select(SalesReturn)
            .options(
                selectinload(SalesReturn.items),
                selectinload(SalesReturn.customer),
            )
            .where(
                SalesReturn.id == return_id,
                SalesReturn.is_deleted == False,
            )
        )
        sales_return = result.scalar_one_or_none()

        if not sales_return:
            raise NotFoundError("销售退货不存在")

        return sales_return

    async def delete_return(self, return_id: int) -> None:
        """删除销售退货（软删除）"""
        sales_return = await self.get_return(return_id)

        if sales_return.status not in [SalesReturnStatus.DRAFT, SalesReturnStatus.REJECTED]:
            raise BadRequestError(f"退货状态为{sales_return.status}，无法删除")

        sales_return.is_deleted = True
        sales_return.updated_at = datetime.now(timezone.utc)
        await self.db.commit()


class DeliveryOrderService:
    """
    发货单服务类
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_delivery(self, data: "DeliveryOrderCreate") -> DeliveryOrder:
        """创建发货单"""
        from app.schemas.sales import DeliveryOrderCreate

        # 验证客户
        customer_service = CustomerService(self.db)
        await customer_service.get_customer(data.customer_id)

        # 验证销售订单（如果有）
        order = None
        if data.order_id:
            order_service = SalesOrderService(self.db)
            order = await order_service.get_order(data.order_id)

            if order.customer_id != data.customer_id:
                raise BadRequestError("发货客户与订单客户不一致")

            if order.status not in [
                SalesOrderStatus.CONFIRMED,
                SalesOrderStatus.PARTIAL_SHIPPED,
            ]:
                raise BadRequestError(f"订单状态为{order.status}，无法发货")

        # 生成发货单号
        delivery_no = f"DO-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # 计算总数量和总金额
        total_quantity = sum(item.quantity for item in data.items)
        total_amount = sum(
            (item.unit_price or 0) * item.quantity for item in data.items
        )

        # 创建发货单
        now = datetime.now(timezone.utc)
        delivery = DeliveryOrder(
            delivery_no=delivery_no,
            order_id=data.order_id,
            customer_id=data.customer_id,
            delivery_date=data.delivery_date,
            warehouse_id=data.warehouse_id,
            total_amount=total_amount,
            total_quantity=total_quantity,
            delivery_address=data.delivery_address,
            contact=data.contact,
            contact_phone=data.contact_phone,
            logistics_company=data.logistics_company,
            logistics_no=data.logistics_no,
            logistics_fee=data.logistics_fee,
            notes=data.notes,
            status=DeliveryOrderStatus.PENDING,
            created_at=now,
            updated_at=now,
        )
        self.db.add(delivery)
        await self.db.flush()

        # 创建明细
        for item_data in data.items:
            # 验证订单明细数量（如果有关联订单）
            if order:
                order_item = next(
                    (oi for oi in order.items if oi.id == item_data.order_item_id),
                    None,
                )
                if order_item:
                    # 检查发货数量是否超过订单数量
                    already_shipped = await self._get_shipped_quantity(order_item.id)
                    if already_shipped + item_data.quantity > order_item.quantity:
                        raise BadRequestError(
                            f"产品{item_data.product_name}发货数量超过订单数量"
                        )

            item = DeliveryOrderItem(
                delivery_id=delivery.id,
                **item_data.model_dump(),
            )
            self.db.add(item)

        await self.db.commit()
        await self.db.refresh(delivery)

        return delivery

    async def _get_shipped_quantity(self, order_item_id: int) -> Decimal:
        """获取订单明细的已发货数量"""
        from sqlalchemy import sum as sql_sum

        result = await self.db.execute(
            select(sql_sum(DeliveryOrderItem.quantity)).where(
                DeliveryOrderItem.order_item_id == order_item_id
            )
        )
        shipped = result.scalar() or 0
        return shipped

    async def get_deliveries(
        self,
        customer_id: Optional[int] = None,
        order_id: Optional[int] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[DeliveryOrder]:
        """获取发货单列表"""
        query = select(DeliveryOrder).where(DeliveryOrder.is_deleted == False)

        if customer_id:
            query = query.where(DeliveryOrder.customer_id == customer_id)

        if order_id:
            query = query.where(DeliveryOrder.order_id == order_id)

        if status:
            query = query.where(DeliveryOrder.status == status)

        if keyword:
            query = query.where(DeliveryOrder.delivery_no.like(f"%{keyword}%"))

        query = query.order_by(DeliveryOrder.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_delivery(self, delivery_id: int) -> DeliveryOrder:
        """获取发货单详情"""
        result = await self.db.execute(
            select(DeliveryOrder)
            .options(
                selectinload(DeliveryOrder.items),
                selectinload(DeliveryOrder.customer),
                selectinload(DeliveryOrder.sales_order),
            )
            .where(
                DeliveryOrder.id == delivery_id,
                DeliveryOrder.is_deleted == False,
            )
        )
        delivery = result.scalar_one_or_none()

        if not delivery:
            raise NotFoundError("发货单不存在")

        return delivery

    async def ship_delivery(
        self, delivery_id: int, data: "DeliveryOrderShip"
    ) -> DeliveryOrder:
        """确认发货"""
        from app.schemas.sales import DeliveryOrderShip

        delivery = await self.get_delivery(delivery_id)

        if delivery.status != DeliveryOrderStatus.PENDING:
            raise BadRequestError(f"发货单状态为{delivery.status}，无法发货")

        # 更新物流信息
        if data.logistics_company:
            delivery.logistics_company = data.logistics_company
        if data.logistics_no:
            delivery.logistics_no = data.logistics_no
        if data.notes:
            delivery.notes = data.notes

        delivery.status = DeliveryOrderStatus.SHIPPED
        delivery.shipped_at = datetime.now(timezone.utc)
        delivery.updated_at = datetime.now(timezone.utc)

        # 更新关联订单状态
        if delivery.order_id and delivery.sales_order:
            order = delivery.sales_order
            # 检查订单是否全部发货
            is_fully_shipped = await self._check_order_fully_shipped(delivery.order_id)
            if is_fully_shipped:
                order.status = SalesOrderStatus.SHIPPED
            else:
                order.status = SalesOrderStatus.PARTIAL_SHIPPED
            order.updated_at = datetime.now(timezone.utc)

        # 更新订单明细的已发货数量
        for delivery_item in delivery.items:
            if delivery_item.order_item_id:
                result = await self.db.execute(
                    select(SalesOrderItem).where(
                        SalesOrderItem.id == delivery_item.order_item_id
                    )
                )
                order_item = result.scalar_one_or_none()
                if order_item:
                    order_item.shipped_quantity += delivery_item.quantity

        await self.db.commit()
        await self.db.refresh(delivery)

        return delivery

    async def _check_order_fully_shipped(self, order_id: int) -> bool:
        """检查订单是否全部发货"""
        # 获取订单的所有明细
        result = await self.db.execute(
            select(SalesOrderItem).where(SalesOrderItem.order_id == order_id)
        )
        order_items = result.scalars().all()

        for order_item in order_items:
            if order_item.shipped_quantity < order_item.quantity:
                return False

        return True

    async def receive_delivery(
        self, delivery_id: int, data: "DeliveryOrderReceive"
    ) -> DeliveryOrder:
        """确认签收"""
        from app.schemas.sales import DeliveryOrderReceive

        delivery = await self.get_delivery(delivery_id)

        if delivery.status != DeliveryOrderStatus.SHIPPED:
            raise BadRequestError(f"发货单状态为{delivery.status}，无法签收")

        delivery.status = DeliveryOrderStatus.RECEIVED
        delivery.received_at = datetime.now(timezone.utc)
        delivery.received_by = data.received_by
        delivery.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(delivery)

        return delivery

    async def cancel_delivery(self, delivery_id: int) -> DeliveryOrder:
        """取消发货单"""
        delivery = await self.get_delivery(delivery_id)

        if delivery.status not in [
            DeliveryOrderStatus.DRAFT,
            DeliveryOrderStatus.PENDING,
        ]:
            raise BadRequestError(f"发货单状态为{delivery.status}，无法取消")

        delivery.status = DeliveryOrderStatus.CANCELLED
        delivery.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(delivery)

        return delivery
