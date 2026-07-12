"""
采购管理服务层

@description 采购模块的业务逻辑

@services
- SupplierService: 供应商服务
- PurchaseRequestService: 采购申请服务
- PurchaseOrderService: 采购订单服务
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.purchase import (
    Supplier,
    SupplierStatus,
    PurchaseRequest,
    PurchaseRequestStatus,
    PurchaseRequestItem,
    PurchaseOrder,
    PurchaseOrderStatus,
    PurchaseOrderItem,
    ReceiptOrder,
    ReceiptOrderStatus,
    ReceiptOrderItem,
)
from app.schemas.purchase import (
    SupplierCreate,
    SupplierUpdate,
    PurchaseRequestCreate,
    PurchaseRequestUpdate,
    PurchaseOrderCreate,
    PurchaseOrderUpdate,
    ReceiptOrderCreate,
    ReceiptOrderReceive,
    ReceiptOrderInspect,
    ReceiptOrderStock,
)


class SupplierService:
    """
    供应商服务类
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_supplier(self, data: SupplierCreate) -> Supplier:
        """
        创建供应商

        Args:
            data: 供应商创建数据

        Returns:
            Supplier: 创建的供应商

        Raises:
            BadRequestError: 供应商编码已存在
        """
        # 检查编码是否已存在
        result = await self.db.execute(
            select(Supplier).where(
                Supplier.code == data.code,
                Supplier.is_deleted == False,
            )
        )
        if result.scalar_one_or_none():
            raise BadRequestError("供应商编码已存在")

        # 创建供应商
        now = datetime.now(timezone.utc)
        supplier = Supplier(
            **data.model_dump(),
            created_at=now,
            updated_at=now,
        )
        self.db.add(supplier)
        await self.db.commit()
        await self.db.refresh(supplier)

        return supplier

    async def get_suppliers(
        self,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Supplier]:
        """
        获取供应商列表

        Args:
            status: 状态筛选
            keyword: 关键词搜索（编码、名称、联系人）
            skip: 跳过条数
            limit: 限制条数

        Returns:
            List[Supplier]: 供应商列表
        """
        query = select(Supplier).where(Supplier.is_deleted == False)

        if status:
            query = query.where(Supplier.status == status)

        if keyword:
            query = query.where(
                or_(
                    Supplier.code.like(f"%{keyword}%"),
                    Supplier.name.like(f"%{keyword}%"),
                    Supplier.contact.like(f"%{keyword}%"),
                )
            )

        query = query.order_by(Supplier.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_supplier(self, supplier_id: int) -> Supplier:
        """
        获取供应商详情

        Args:
            supplier_id: 供应商ID

        Returns:
            Supplier: 供应商详情

        Raises:
            NotFoundError: 供应商不存在
        """
        result = await self.db.execute(
            select(Supplier).where(
                Supplier.id == supplier_id,
                Supplier.is_deleted == False,
            )
        )
        supplier = result.scalar_one_or_none()

        if not supplier:
            raise NotFoundError("供应商不存在")

        return supplier

    async def update_supplier(self, supplier_id: int, data: SupplierUpdate) -> Supplier:
        """
        更新供应商

        Args:
            supplier_id: 供应商ID
            data: 更新数据

        Returns:
            Supplier: 更新后的供应商

        Raises:
            NotFoundError: 供应商不存在
        """
        supplier = await self.get_supplier(supplier_id)

        # 更新字段
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(supplier, field, value)

        supplier.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(supplier)

        return supplier

    async def delete_supplier(self, supplier_id: int) -> None:
        """
        删除供应商（软删除）

        Args:
            supplier_id: 供应商ID

        Raises:
            NotFoundError: 供应商不存在
            BadRequestError: 供应商有关联的采购订单
        """
        supplier = await self.get_supplier(supplier_id)

        # 检查是否有关联的采购订单
        result = await self.db.execute(
            select(func.count(PurchaseOrder.id)).where(
                PurchaseOrder.supplier_id == supplier_id,
                PurchaseOrder.is_deleted == False,
            )
        )
        count = result.scalar()

        if count > 0:
            raise BadRequestError("该供应商存在关联的采购订单，无法删除")

        # 软删除
        supplier.is_deleted = True
        supplier.updated_at = datetime.now(timezone.utc)
        await self.db.commit()


class PurchaseRequestService:
    """
    采购申请服务类
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_request(self, data: PurchaseRequestCreate, applicant_id: int) -> PurchaseRequest:
        """
        创建采购申请

        Args:
            data: 采购申请数据
            applicant_id: 申请人ID

        Returns:
            PurchaseRequest: 创建的采购申请
        """
        # 生成申请单号
        request_no = f"PR-{datetime.now().strftime('%Y%m%d%H%M%S')}-{applicant_id}"

        # 计算总金额
        total_amount = sum(
            (item.estimated_price or 0) * item.quantity
            for item in data.items
        )

        # 创建采购申请
        now = datetime.now(timezone.utc)
        request = PurchaseRequest(
            request_no=request_no,
            title=data.title,
            request_date=data.request_date,
            applicant_id=applicant_id,
            department_id=data.department_id,
            reason=data.reason,
            total_amount=total_amount,
            status=PurchaseRequestStatus.DRAFT,
            created_at=now,
            updated_at=now,
        )
        self.db.add(request)
        await self.db.flush()

        # 创建明细
        for item_data in data.items:
            item = PurchaseRequestItem(
                request_id=request.id,
                **item_data.model_dump(),
            )
            self.db.add(item)

        await self.db.commit()
        await self.db.refresh(request)

        return request

    async def get_requests(
        self,
        applicant_id: Optional[int] = None,
        status: Optional[str] = None,
        department_id: Optional[int] = None,
        keyword: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[PurchaseRequest]:
        """
        获取采购申请列表

        Args:
            applicant_id: 申请人筛选
            status: 状态筛选
            department_id: 部门筛选
            keyword: 关键词搜索
            skip: 跳过条数
            limit: 限制条数

        Returns:
            List[PurchaseRequest]: 采购申请列表
        """
        query = select(PurchaseRequest).where(PurchaseRequest.is_deleted == False)

        if applicant_id:
            query = query.where(PurchaseRequest.applicant_id == applicant_id)

        if status:
            query = query.where(PurchaseRequest.status == status)

        if department_id:
            query = query.where(PurchaseRequest.department_id == department_id)

        if keyword:
            query = query.where(
                or_(
                    PurchaseRequest.request_no.like(f"%{keyword}%"),
                    PurchaseRequest.title.like(f"%{keyword}%"),
                )
            )

        query = query.order_by(PurchaseRequest.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_request(self, request_id: int) -> PurchaseRequest:
        """
        获取采购申请详情

        Args:
            request_id: 申请ID

        Returns:
            PurchaseRequest: 采购申请详情

        Raises:
            NotFoundError: 采购申请不存在
        """
        result = await self.db.execute(
            select(PurchaseRequest)
            .options(selectinload(PurchaseRequest.items))
            .where(
                PurchaseRequest.id == request_id,
                PurchaseRequest.is_deleted == False,
            )
        )
        request = result.scalar_one_or_none()

        if not request:
            raise NotFoundError("采购申请不存在")

        return request

    async def update_request(self, request_id: int, data: PurchaseRequestUpdate) -> PurchaseRequest:
        """
        更新采购申请

        Args:
            request_id: 申请ID
            data: 更新数据

        Returns:
            PurchaseRequest: 更新后的采购申请

        Raises:
            NotFoundError: 采购申请不存在
            BadRequestError: 申请状态不允许修改
        """
        request = await self.get_request(request_id)

        # 只有草稿状态可以修改
        if request.status != PurchaseRequestStatus.DRAFT:
            raise BadRequestError(f"申请状态为{request.status}，无法修改")

        # 更新基本信息
        update_data = data.model_dump(exclude_unset=True, exclude={"items"})
        for field, value in update_data.items():
            setattr(request, field, value)

        # 更新明细
        if data.items is not None:
            # 删除旧明细
            for old_item in request.items:
                await self.db.delete(old_item)

            # 添加新明细
            total_amount = Decimal(0)
            for item_data in data.items:
                item = PurchaseRequestItem(
                    request_id=request.id,
                    **item_data.model_dump(),
                )
                self.db.add(item)
                total_amount += (item_data.estimated_price or 0) * item_data.quantity

            request.total_amount = total_amount

        request.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(request)

        return request

    async def submit_request(self, request_id: int) -> PurchaseRequest:
        """
        提交采购申请（启动审批流程）

        Args:
            request_id: 申请ID

        Returns:
            PurchaseRequest: 提交后的采购申请

        Raises:
            NotFoundError: 采购申请不存在
            BadRequestError: 申请状态不允许提交
        """
        request = await self.get_request(request_id)

        if request.status != PurchaseRequestStatus.DRAFT:
            raise BadRequestError(f"申请状态为{request.status}，无法提交")

        # TODO: 启动审批流程
        # workflow_service.start_workflow(workflow_id, {...}, request.applicant_id)

        request.status = PurchaseRequestStatus.PENDING
        request.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(request)

        return request

    async def delete_request(self, request_id: int) -> None:
        """
        删除采购申请（软删除）

        Args:
            request_id: 申请ID

        Raises:
            NotFoundError: 采购申请不存在
            BadRequestError: 申请状态不允许删除
        """
        request = await self.get_request(request_id)

        if request.status not in [PurchaseRequestStatus.DRAFT, PurchaseRequestStatus.REJECTED]:
            raise BadRequestError(f"申请状态为{request.status}，无法删除")

        request.is_deleted = True
        request.updated_at = datetime.now(timezone.utc)
        await self.db.commit()


class PurchaseOrderService:
    """
    采购订单服务类
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_order(self, data: PurchaseOrderCreate) -> PurchaseOrder:
        """
        创建采购订单

        Args:
            data: 采购订单数据

        Returns:
            PurchaseOrder: 创建的采购订单

        Raises:
            NotFoundError: 供应商不存在或采购申请不存在
            BadRequestError: 采购申请状态不允许转订单
        """
        # 验证供应商
        supplier_service = SupplierService(self.db)
        supplier = await supplier_service.get_supplier(data.supplier_id)

        # 如果有关联的采购申请，验证其状态
        if data.request_id:
            request_service = PurchaseRequestService(self.db)
            request = await request_service.get_request(data.request_id)

            if request.status != PurchaseRequestStatus.APPROVED:
                raise BadRequestError("采购申请未审批通过，无法创建订单")

        # 生成订单号
        order_no = f"PO-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # 计算总金额和税额
        total_amount = Decimal(0)
        tax_amount = Decimal(0)

        for item_data in data.items:
            item_amount = (item_data.unit_price or 0) * item_data.quantity
            total_amount += item_amount

            if data.tax_inclusive and item_data.tax_rate:
                # 含税，计算不含税金额
                tax_amount += item_amount - (item_amount / (1 + item_data.tax_rate / 100))
            elif item_data.tax_rate:
                # 不含税，计算税额
                tax_amount += item_amount * (item_data.tax_rate / 100)

        # 创建采购订单
        now = datetime.now(timezone.utc)
        order = PurchaseOrder(
            order_no=order_no,
            supplier_id=data.supplier_id,
            order_date=data.order_date,
            expected_date=data.expected_date,
            request_id=data.request_id,
            total_amount=total_amount,
            tax_amount=tax_amount,
            tax_inclusive=data.tax_inclusive or False,
            payment_terms=data.payment_terms,
            delivery_address=data.delivery_address,
            contact=data.contact,
            contact_phone=data.contact_phone,
            notes=data.notes,
            status=PurchaseOrderStatus.DRAFT,
            created_at=now,
            updated_at=now,
        )
        self.db.add(order)
        await self.db.flush()

        # 创建明细
        for item_data in data.items:
            item = PurchaseOrderItem(
                order_id=order.id,
                **item_data.model_dump(),
            )
            self.db.add(item)

        # 更新采购申请状态
        if data.request_id:
            request_result = await self.db.execute(
                select(PurchaseRequest).where(PurchaseRequest.id == data.request_id)
            )
            request = request_result.scalar_one_or_none()
            if request:
                request.status = PurchaseRequestStatus.CONVERTED
                request.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(order)

        return order

    async def get_orders(
        self,
        supplier_id: Optional[int] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[PurchaseOrder]:
        """
        获取采购订单列表

        Args:
            supplier_id: 供应商筛选
            status: 状态筛选
            keyword: 关键词搜索
            skip: 跳过条数
            limit: 限制条数

        Returns:
            List[PurchaseOrder]: 采购订单列表
        """
        query = select(PurchaseOrder).where(PurchaseOrder.is_deleted == False)

        if supplier_id:
            query = query.where(PurchaseOrder.supplier_id == supplier_id)

        if status:
            query = query.where(PurchaseOrder.status == status)

        if keyword:
            query = query.where(PurchaseOrder.order_no.like(f"%{keyword}%"))

        query = query.order_by(PurchaseOrder.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_order(self, order_id: int) -> PurchaseOrder:
        """
        获取采购订单详情

        Args:
            order_id: 订单ID

        Returns:
            PurchaseOrder: 采购订单详情

        Raises:
            NotFoundError: 采购订单不存在
        """
        result = await self.db.execute(
            select(PurchaseOrder)
            .options(
                selectinload(PurchaseOrder.items),
                selectinload(PurchaseOrder.supplier),
            )
            .where(
                PurchaseOrder.id == order_id,
                PurchaseOrder.is_deleted == False,
            )
        )
        order = result.scalar_one_or_none()

        if not order:
            raise NotFoundError("采购订单不存在")

        return order

    async def update_order(self, order_id: int, data: PurchaseOrderUpdate) -> PurchaseOrder:
        """
        更新采购订单

        Args:
            order_id: 订单ID
            data: 更新数据

        Returns:
            PurchaseOrder: 更新后的采购订单

        Raises:
            NotFoundError: 采购订单不存在
            BadRequestError: 订单状态不允许修改
        """
        order = await self.get_order(order_id)

        # 只有草稿状态可以修改
        if order.status != PurchaseOrderStatus.DRAFT:
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

            # 添加新明细
            total_amount = Decimal(0)
            tax_amount = Decimal(0)

            for item_data in data.items:
                item = PurchaseOrderItem(
                    order_id=order.id,
                    **item_data.model_dump(),
                )
                self.db.add(item)

                item_amount = (item_data.unit_price or 0) * item_data.quantity
                total_amount += item_amount

                if data.tax_inclusive and item_data.tax_rate:
                    tax_amount += item_amount - (item_amount / (1 + item_data.tax_rate / 100))
                elif item_data.tax_rate:
                    tax_amount += item_amount * (item_data.tax_rate / 100)

            order.total_amount = total_amount
            order.tax_amount = tax_amount

        order.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(order)

        return order

    async def confirm_order(self, order_id: int) -> PurchaseOrder:
        """
        确认采购订单

        Args:
            order_id: 订单ID

        Returns:
            PurchaseOrder: 确认后的采购订单

        Raises:
            NotFoundError: 采购订单不存在
            BadRequestError: 订单状态不允许确认
        """
        order = await self.get_order(order_id)

        if order.status != PurchaseOrderStatus.DRAFT:
            raise BadRequestError(f"订单状态为{order.status}，无法确认")

        order.status = PurchaseOrderStatus.CONFIRMED
        order.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(order)

        return order

    async def cancel_order(self, order_id: int) -> PurchaseOrder:
        """
        取消采购订单

        Args:
            order_id: 订单ID

        Returns:
            PurchaseOrder: 取消后的采购订单

        Raises:
            NotFoundError: 采购订单不存在
            BadRequestError: 订单状态不允许取消
        """
        order = await self.get_order(order_id)

        if order.status in [PurchaseOrderStatus.RECEIVED, PurchaseOrderStatus.CLOSED]:
            raise BadRequestError(f"订单状态为{order.status}，无法取消")

        order.status = PurchaseOrderStatus.CANCELLED
        order.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(order)

        return order

    async def delete_order(self, order_id: int) -> None:
        """
        删除采购订单（软删除）

        Args:
            order_id: 订单ID

        Raises:
            NotFoundError: 采购订单不存在
            BadRequestError: 订单状态不允许删除
        """
        order = await self.get_order(order_id)

        if order.status != PurchaseOrderStatus.DRAFT:
            raise BadRequestError(f"订单状态为{order.status}，无法删除")

        order.is_deleted = True
        order.updated_at = datetime.now(timezone.utc)
        await self.db.commit()


class ReceiptOrderService:
    """
    收货单服务类
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_receipt(self, data: ReceiptOrderCreate) -> ReceiptOrder:
        """
        创建收货单

        Args:
            data: 收货单创建数据

        Returns:
            ReceiptOrder: 创建的收货单

        Raises:
            NotFoundError: 供应商不存在或采购订单不存在
            BadRequestError: 采购订单状态不允许收货
        """
        # 验证供应商
        supplier_service = SupplierService(self.db)
        supplier = await supplier_service.get_supplier(data.supplier_id)

        # 如果有关联的采购订单，验证其状态
        if data.order_id:
            order_service = PurchaseOrderService(self.db)
            order = await order_service.get_order(data.order_id)

            if order.status not in [PurchaseOrderStatus.CONFIRMED, PurchaseOrderStatus.PARTIAL_RECEIVED]:
                raise BadRequestError("采购订单状态不允许收货")

        # 生成收货单号
        receipt_no = f"RC-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # 计算总金额和总数量
        total_amount = Decimal(0)
        total_quantity = Decimal(0)

        for item_data in data.items:
            item_amount = (item_data.unit_price or 0) * item_data.quantity
            total_amount += item_amount
            total_quantity += item_data.quantity

        # 创建收货单
        now = datetime.now(timezone.utc)
        receipt = ReceiptOrder(
            receipt_no=receipt_no,
            order_id=data.order_id,
            supplier_id=data.supplier_id,
            receipt_date=data.receipt_date,
            warehouse_id=data.warehouse_id,
            total_amount=total_amount,
            total_quantity=total_quantity,
            inspection_status="pending",
            status=ReceiptOrderStatus.DRAFT,
            created_at=now,
            updated_at=now,
        )
        self.db.add(receipt)
        await self.db.flush()

        # 创建明细
        for item_data in data.items:
            item = ReceiptOrderItem(
                receipt_id=receipt.id,
                **item_data.model_dump(),
            )
            self.db.add(item)

        await self.db.commit()
        await self.db.refresh(receipt)

        return receipt

    async def get_receipts(
        self,
        supplier_id: Optional[int] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ReceiptOrder]:
        """
        获取收货单列表

        Args:
            supplier_id: 供应商筛选
            status: 状态筛选
            keyword: 关键词搜索
            skip: 跳过条数
            limit: 限制条数

        Returns:
            List[ReceiptOrder]: 收货单列表
        """
        query = select(ReceiptOrder).where(ReceiptOrder.is_deleted == False)

        if supplier_id:
            query = query.where(ReceiptOrder.supplier_id == supplier_id)

        if status:
            query = query.where(ReceiptOrder.status == status)

        if keyword:
            query = query.where(ReceiptOrder.receipt_no.like(f"%{keyword}%"))

        query = query.order_by(ReceiptOrder.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_receipt(self, receipt_id: int) -> ReceiptOrder:
        """
        获取收货单详情

        Args:
            receipt_id: 收货单ID

        Returns:
            ReceiptOrder: 收货单详情

        Raises:
            NotFoundError: 收货单不存在
        """
        result = await self.db.execute(
            select(ReceiptOrder)
            .options(
                selectinload(ReceiptOrder.items),
                selectinload(ReceiptOrder.supplier),
            )
            .where(
                ReceiptOrder.id == receipt_id,
                ReceiptOrder.is_deleted == False,
            )
        )
        receipt = result.scalar_one_or_none()

        if not receipt:
            raise NotFoundError("收货单不存在")

        return receipt

    async def receive_receipt(
        self, receipt_id: int, data: ReceiptOrderReceive
    ) -> ReceiptOrder:
        """
        收货确认

        Args:
            receipt_id: 收货单ID
            data: 收货确认数据

        Returns:
            ReceiptOrder: 收货确认后的收货单

        Raises:
            NotFoundError: 收货单不存在
            BadRequestError: 收货单状态不允许收货确认
        """
        receipt = await self.get_receipt(receipt_id)

        if receipt.status != ReceiptOrderStatus.DRAFT:
            raise BadRequestError(f"收货单状态为{receipt.status}，无法收货确认")

        receipt.status = ReceiptOrderStatus.RECEIVED
        receipt.warehouse_id = data.warehouse_id
        receipt.received_at = datetime.now(timezone.utc)
        if data.notes:
            receipt.notes = data.notes
        receipt.updated_at = datetime.now(timezone.utc)

        # 更新关联的采购订单状态
        if receipt.order_id:
            order_result = await self.db.execute(
                select(PurchaseOrder).where(PurchaseOrder.id == receipt.order_id)
            )
            order = order_result.scalar_one_or_none()
            if order and order.status == PurchaseOrderStatus.CONFIRMED:
                order.status = PurchaseOrderStatus.PARTIAL_RECEIVED
                order.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(receipt)

        return receipt

    async def inspect_receipt(
        self, receipt_id: int, data: ReceiptOrderInspect
    ) -> ReceiptOrder:
        """
        质检处理

        Args:
            receipt_id: 收货单ID
            data: 质检处理数据

        Returns:
            ReceiptOrder: 质检处理后的收货单

        Raises:
            NotFoundError: 收货单不存在
            BadRequestError: 收货单状态不允许质检
        """
        receipt = await self.get_receipt(receipt_id)

        if receipt.status != ReceiptOrderStatus.RECEIVED:
            raise BadRequestError(f"收货单状态为{receipt.status}，无法质检")

        # 更新明细的质检数据
        total_qualified = Decimal(0)
        total_rejected = Decimal(0)

        for item_data in data.items:
            item_result = await self.db.execute(
                select(ReceiptOrderItem).where(
                    ReceiptOrderItem.id == item_data.get("item_id"),
                    ReceiptOrderItem.receipt_id == receipt_id,
                )
            )
            item = item_result.scalar_one_or_none()

            if item:
                qualified = Decimal(str(item_data.get("qualified_quantity", 0)))
                rejected = Decimal(str(item_data.get("rejected_quantity", 0)))
                item.qualified_quantity = qualified
                item.rejected_quantity = rejected
                total_qualified += qualified
                total_rejected += rejected

        # 更新收货单质检状态
        receipt.inspection_result = data.inspection_result
        receipt.qualified_quantity = total_qualified
        receipt.rejected_quantity = total_rejected
        receipt.inspection_status = "complete"
        receipt.inspected_at = datetime.now(timezone.utc)

        # 根据质检结果更新状态
        if total_rejected == 0:
            receipt.status = ReceiptOrderStatus.INSPECTED
        elif total_qualified == 0:
            receipt.status = ReceiptOrderStatus.RETURNED
        else:
            receipt.status = ReceiptOrderStatus.PARTIAL_INSPECTED

        receipt.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(receipt)

        return receipt

    async def stock_receipt(
        self, receipt_id: int, data: ReceiptOrderStock
    ) -> ReceiptOrder:
        """
        入库确认

        Args:
            receipt_id: 收货单ID
            data: 入库确认数据

        Returns:
            ReceiptOrder: 入库确认后的收货单

        Raises:
            NotFoundError: 收货单不存在
            BadRequestError: 收货单状态不允许入库
        """
        receipt = await self.get_receipt(receipt_id)

        if receipt.status not in [
            ReceiptOrderStatus.INSPECTED,
            ReceiptOrderStatus.PARTIAL_INSPECTED,
        ]:
            raise BadRequestError(f"收货单状态为{receipt.status}，无法入库")

        # TODO: 创建库存入库流水
        # inventory_service.add_stock(...)

        # 更新采购订单的已收货数量
        if receipt.order_id:
            for receipt_item in receipt.items:
                order_item_result = await self.db.execute(
                    select(PurchaseOrderItem).where(
                        PurchaseOrderItem.id == receipt_item.order_item_id
                    )
                )
                order_item = order_item_result.scalar_one_or_none()
                if order_item:
                    order_item.received_quantity += receipt_item.qualified_quantity

            # 检查订单是否全部收货
            order_result = await self.db.execute(
                select(PurchaseOrder)
                .options(selectinload(PurchaseOrder.items))
                .where(PurchaseOrder.id == receipt.order_id)
            )
            order = order_result.scalar_one_or_none()
            if order:
                all_received = all(
                    item.received_quantity >= item.quantity for item in order.items
                )
                if all_received:
                    order.status = PurchaseOrderStatus.RECEIVED
                else:
                    order.status = PurchaseOrderStatus.PARTIAL_RECEIVED
                order.updated_at = datetime.now(timezone.utc)

        receipt.status = ReceiptOrderStatus.STOCKED
        receipt.stocked_at = datetime.now(timezone.utc)
        if data.notes:
            receipt.notes = data.notes
        receipt.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(receipt)

        return receipt

    async def cancel_receipt(self, receipt_id: int) -> ReceiptOrder:
        """
        取消收货单

        Args:
            receipt_id: 收货单ID

        Returns:
            ReceiptOrder: 取消后的收货单

        Raises:
            NotFoundError: 收货单不存在
            BadRequestError: 收货单状态不允许取消
        """
        receipt = await self.get_receipt(receipt_id)

        if receipt.status in [ReceiptOrderStatus.STOCKED, ReceiptOrderStatus.RETURNED]:
            raise BadRequestError(f"收货单状态为{receipt.status}，无法取消")

        receipt.status = ReceiptOrderStatus.CANCELLED
        receipt.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(receipt)

        return receipt
