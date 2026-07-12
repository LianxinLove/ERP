"""
发票管理服务层

@description 发票模块的业务逻辑

@services
- SalesInvoiceService: 销售发票服务
- PurchaseInvoiceService: 采购发票服务
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.invoice import (
    SalesInvoice,
    SalesInvoiceItem,
    PurchaseInvoice,
    PurchaseInvoiceItem,
    InvoiceType,
    InvoiceStatus,
)
from app.models.sales import SalesOrder, SalesOrderItem, DeliveryOrder
from app.models.purchase import PurchaseOrder, PurchaseOrderItem, ReceiptOrder
from app.schemas.invoice import (
    SalesInvoiceCreate,
    SalesInvoiceIssue,
    SalesInvoiceSend,
    PurchaseInvoiceCreate,
    PurchaseInvoiceReceive,
    PurchaseInvoiceVerify,
    InvoiceMatchRequest,
)


class SalesInvoiceService:
    """
    销售发票服务类
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_invoice(self, data: SalesInvoiceCreate) -> SalesInvoice:
        """
        创建销售发票

        Args:
            data: 销售发票创建数据

        Returns:
            SalesInvoice: 创建的销售发票

        Raises:
            NotFoundError: 客户不存在或销售订单不存在
        """
        # 验证客户存在（通过销售服务或直接查询）
        # TODO: 添加客户验证

        # 如果有关联的销售订单，验证其状态
        if data.order_id:
            order_result = await self.db.execute(
                select(SalesOrder).where(SalesOrder.id == data.order_id)
            )
            order = order_result.scalar_one_or_none()
            if not order:
                raise NotFoundError("销售订单不存在")

        # 计算总金额和税额
        total_amount = Decimal(0)
        total_tax = Decimal(0)

        for item_data in data.items:
            item_amount = (item_data.unit_price or 0) * item_data.quantity
            total_amount += item_amount
            if item_data.tax_rate:
                total_tax += item_amount * (item_data.tax_rate / 100)

        # 创建发票
        now = datetime.now(timezone.utc)
        invoice = SalesInvoice(
            invoice_no=f"SI-{now.strftime('%Y%m%d%H%M%S')}",
            invoice_code=data.invoice_code,
            invoice_type=data.invoice_type or InvoiceType.VAT_ELECTRONIC,
            order_id=data.order_id,
            customer_id=data.customer_id,
            invoice_date=data.invoice_date,
            total_amount=total_amount,
            tax_amount=total_tax,
            total_amount_with_tax=total_amount + total_tax,
            buyer_name=data.buyer_name,
            buyer_tax_no=data.buyer_tax_no,
            buyer_address_phone=data.buyer_address_phone,
            buyer_bank_account=data.buyer_bank_account,
            seller_name=data.seller_name,
            seller_tax_no=data.seller_tax_no,
            seller_address_phone=data.seller_address_phone,
            seller_bank_account=data.seller_bank_account,
            remarks=data.remarks,
            status=InvoiceStatus.DRAFT,
            created_at=now,
            updated_at=now,
        )
        self.db.add(invoice)
        await self.db.flush()

        # 创建明细
        for item_data in data.items:
            item = SalesInvoiceItem(
                invoice_id=invoice.id,
                **item_data.model_dump(),
            )
            self.db.add(item)

        await self.db.commit()
        await self.db.refresh(invoice)

        return invoice

    async def get_invoices(
        self,
        customer_id: Optional[int] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[SalesInvoice]:
        """
        获取销售发票列表

        Args:
            customer_id: 客户筛选
            status: 状态筛选
            keyword: 关键词搜索
            skip: 跳过条数
            limit: 限制条数

        Returns:
            List[SalesInvoice]: 销售发票列表
        """
        query = select(SalesInvoice).where(SalesInvoice.is_deleted == False)

        if customer_id:
            query = query.where(SalesInvoice.customer_id == customer_id)

        if status:
            query = query.where(SalesInvoice.status == status)

        if keyword:
            query = query.where(
                or_(
                    SalesInvoice.invoice_no.like(f"%{keyword}%"),
                    SalesInvoice.buyer_name.like(f"%{keyword}%"),
                )
            )

        query = query.order_by(SalesInvoice.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_invoice(self, invoice_id: int) -> SalesInvoice:
        """
        获取销售发票详情

        Args:
            invoice_id: 发票ID

        Returns:
            SalesInvoice: 销售发票详情

        Raises:
            NotFoundError: 发票不存在
        """
        result = await self.db.execute(
            select(SalesInvoice)
            .options(selectinload(SalesInvoice.items))
            .where(
                SalesInvoice.id == invoice_id,
                SalesInvoice.is_deleted == False,
            )
        )
        invoice = result.scalar_one_or_none()

        if not invoice:
            raise NotFoundError("销售发票不存在")

        return invoice

    async def issue_invoice(
        self, invoice_id: int, data: SalesInvoiceIssue
    ) -> SalesInvoice:
        """
        开具发票

        Args:
            invoice_id: 发票ID
            data: 开票数据

        Returns:
            SalesInvoice: 开票后的发票

        Raises:
            NotFoundError: 发票不存在
            BadRequestError: 发票状态不允许开票
        """
        invoice = await self.get_invoice(invoice_id)

        if invoice.status != InvoiceStatus.DRAFT:
            raise BadRequestError(f"发票状态为{invoice.status}，无法开票")

        invoice.invoice_no = data.invoice_no
        invoice.invoice_code = data.invoice_code
        invoice.pdf_url = data.pdf_url
        invoice.status = InvoiceStatus.ISSUED
        invoice.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(invoice)

        return invoice

    async def send_invoice(
        self, invoice_id: int, data: SalesInvoiceSend
    ) -> SalesInvoice:
        """
        发送发票

        Args:
            invoice_id: 发票ID
            data: 发送数据

        Returns:
            SalesInvoice: 发送后的发票

        Raises:
            NotFoundError: 发票不存在
            BadRequestError: 发票状态不允许发送
        """
        invoice = await self.get_invoice(invoice_id)

        if invoice.status != InvoiceStatus.ISSUED:
            raise BadRequestError(f"发票状态为{invoice.status}，无法发送")

        # TODO: 实现实际的发送逻辑
        # - email: 发送邮件
        # - paper: 生成打印任务

        invoice.status = InvoiceStatus.SENT
        invoice.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(invoice)

        return invoice

    async def cancel_invoice(self, invoice_id: int) -> SalesInvoice:
        """
        作废发票

        Args:
            invoice_id: 发票ID

        Returns:
            SalesInvoice: 作废后的发票

        Raises:
            NotFoundError: 发票不存在
            BadRequestError: 发票状态不允许作废
        """
        invoice = await self.get_invoice(invoice_id)

        if invoice.status in [InvoiceStatus.CANCELLED, InvoiceStatus.REVERSED]:
            raise BadRequestError(f"发票状态为{invoice.status}，无法作废")

        invoice.status = InvoiceStatus.CANCELLED
        invoice.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(invoice)

        return invoice


class PurchaseInvoiceService:
    """
    采购发票服务类
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_invoice(self, data: PurchaseInvoiceCreate) -> PurchaseInvoice:
        """
        创建采购发票

        Args:
            data: 采购发票创建数据

        Returns:
            PurchaseInvoice: 创建的采购发票

        Raises:
            NotFoundError: 供应商不存在或采购订单不存在
        """
        # 验证供应商存在
        # TODO: 添加供应商验证

        # 如果有关联的采购订单，验证其状态
        if data.order_id:
            order_result = await self.db.execute(
                select(PurchaseOrder).where(PurchaseOrder.id == data.order_id)
            )
            order = order_result.scalar_one_or_none()
            if not order:
                raise NotFoundError("采购订单不存在")

        # 计算总金额和税额
        total_amount = Decimal(0)
        total_tax = Decimal(0)

        for item_data in data.items:
            item_amount = (item_data.unit_price or 0) * item_data.quantity
            total_amount += item_amount
            if item_data.tax_rate:
                total_tax += item_amount * (item_data.tax_rate / 100)

        # 创建发票
        now = datetime.now(timezone.utc)
        invoice = PurchaseInvoice(
            invoice_no=f"PI-{now.strftime('%Y%m%d%H%M%S')}",
            invoice_code=data.invoice_code,
            invoice_type=data.invoice_type or InvoiceType.VAT_ELECTRONIC,
            order_id=data.order_id,
            supplier_id=data.supplier_id,
            invoice_date=data.invoice_date,
            total_amount=total_amount,
            tax_amount=total_tax,
            total_amount_with_tax=total_amount + total_tax,
            buyer_name=data.buyer_name,
            buyer_tax_no=data.buyer_tax_no,
            seller_name=data.seller_name,
            seller_tax_no=data.seller_tax_no,
            remarks=data.remarks,
            status=InvoiceStatus.DRAFT,
            created_at=now,
            updated_at=now,
        )
        self.db.add(invoice)
        await self.db.flush()

        # 创建明细
        for item_data in data.items:
            item = PurchaseInvoiceItem(
                invoice_id=invoice.id,
                **item_data.model_dump(),
            )
            self.db.add(item)

        await self.db.commit()
        await self.db.refresh(invoice)

        return invoice

    async def get_invoices(
        self,
        supplier_id: Optional[int] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[PurchaseInvoice]:
        """
        获取采购发票列表

        Args:
            supplier_id: 供应商筛选
            status: 状态筛选
            keyword: 关键词搜索
            skip: 跳过条数
            limit: 限制条数

        Returns:
            List[PurchaseInvoice]: 采购发票列表
        """
        query = select(PurchaseInvoice).where(PurchaseInvoice.is_deleted == False)

        if supplier_id:
            query = query.where(PurchaseInvoice.supplier_id == supplier_id)

        if status:
            query = query.where(PurchaseInvoice.status == status)

        if keyword:
            query = query.where(
                or_(
                    PurchaseInvoice.invoice_no.like(f"%{keyword}%"),
                    PurchaseInvoice.seller_name.like(f"%{keyword}%"),
                )
            )

        query = query.order_by(PurchaseInvoice.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_invoice(self, invoice_id: int) -> PurchaseInvoice:
        """
        获取采购发票详情

        Args:
            invoice_id: 发票ID

        Returns:
            PurchaseInvoice: 采购发票详情

        Raises:
            NotFoundError: 发票不存在
        """
        result = await self.db.execute(
            select(PurchaseInvoice)
            .options(selectinload(PurchaseInvoice.items))
            .where(
                PurchaseInvoice.id == invoice_id,
                PurchaseInvoice.is_deleted == False,
            )
        )
        invoice = result.scalar_one_or_none()

        if not invoice:
            raise NotFoundError("采购发票不存在")

        return invoice

    async def receive_invoice(
        self, invoice_id: int, data: PurchaseInvoiceReceive
    ) -> PurchaseInvoice:
        """
        接收采购发票

        Args:
            invoice_id: 发票ID
            data: 接收数据

        Returns:
            PurchaseInvoice: 接收后的发票

        Raises:
            NotFoundError: 发票不存在
            BadRequestError: 发票状态不允许接收
        """
        invoice = await self.get_invoice(invoice_id)

        if invoice.status != InvoiceStatus.DRAFT:
            raise BadRequestError(f"发票状态为{invoice.status}，无法接收")

        invoice.invoice_no = data.invoice_no
        invoice.invoice_code = data.invoice_code
        invoice.pdf_url = data.pdf_url
        invoice.status = InvoiceStatus.RECEIVED
        invoice.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(invoice)

        return invoice

    async def verify_invoice(
        self, invoice_id: int, data: PurchaseInvoiceVerify
    ) -> PurchaseInvoice:
        """
        认证采购发票

        Args:
            invoice_id: 发票ID
            data: 认证数据

        Returns:
            PurchaseInvoice: 认证后的发票

        Raises:
            NotFoundError: 发票不存在
            BadRequestError: 发票状态不允许认证
        """
        invoice = await self.get_invoice(invoice_id)

        if invoice.status != InvoiceStatus.RECEIVED:
            raise BadRequestError(f"发票状态为{invoice.status}，无法认证")

        # TODO: 调用税务API进行实际认证
        # result = await tax_api.verify_invoice(invoice.invoice_no, invoice.invoice_code)

        invoice.verification_status = data.verification_status
        invoice.verification_date = datetime.now(timezone.utc)
        invoice.status = InvoiceStatus.VERIFIED
        invoice.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(invoice)

        return invoice


class InvoiceMatchService:
    """
    发票勾稽服务类
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def match_sales_invoice(
        self, invoice_id: int, delivery_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        销售发票勾稽验证

        Args:
            invoice_id: 销售发票ID
            delivery_id: 发货单ID（可选）

        Returns:
            Dict: 匹配结果 {matched, differences, warnings}
        """
        # 获取发票
        invoice_result = await self.db.execute(
            select(SalesInvoice)
            .options(selectinload(SalesInvoice.items))
            .where(SalesInvoice.id == invoice_id)
        )
        invoice = invoice_result.scalar_one_or_none()
        if not invoice:
            raise NotFoundError("销售发票不存在")

        differences = []
        warnings = []

        # 如果指定了发货单，与发货单比对
        if delivery_id:
            delivery_result = await self.db.execute(
                select(DeliveryOrder)
                .options(selectinload(DeliveryOrder.items))
                .where(DeliveryOrder.id == delivery_id)
            )
            delivery = delivery_result.scalar_one_or_none()

            if delivery:
                # 比对金额
                if invoice.total_amount and delivery.total_amount:
                    if abs(invoice.total_amount - delivery.total_amount) > Decimal("0.01"):
                        differences.append({
                            "field": "total_amount",
                            "invoice": float(invoice.total_amount),
                            "delivery": float(delivery.total_amount),
                        })

                # 比对明细数量
                if len(invoice.items) != len(delivery.items):
                    warnings.append("明细数量不一致")

        # 如果关联了订单，与订单比对
        if invoice.order_id:
            order_result = await self.db.execute(
                select(SalesOrder)
                .options(selectinload(SalesOrder.items))
                .where(SalesOrder.id == invoice.order_id)
            )
            order = order_result.scalar_one_or_none()

            if order:
                # 比对金额
                if invoice.total_amount and order.total_amount:
                    if abs(invoice.total_amount - order.total_amount) > Decimal("0.01"):
                        differences.append({
                            "field": "order_amount",
                            "invoice": float(invoice.total_amount),
                            "order": float(order.total_amount),
                        })

        return {
            "matched": len(differences) == 0,
            "differences": differences,
            "warnings": warnings,
        }

    async def match_purchase_invoice(
        self, invoice_id: int, receipt_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        采购发票勾稽验证

        Args:
            invoice_id: 采购发票ID
            receipt_id: 收货单ID（可选）

        Returns:
            Dict: 匹配结果 {matched, differences, warnings}
        """
        # 获取发票
        invoice_result = await self.db.execute(
            select(PurchaseInvoice)
            .options(selectinload(PurchaseInvoice.items))
            .where(PurchaseInvoice.id == invoice_id)
        )
        invoice = invoice_result.scalar_one_or_none()
        if not invoice:
            raise NotFoundError("采购发票不存在")

        differences = []
        warnings = []

        # 如果指定了收货单，与收货单比对
        if receipt_id:
            receipt_result = await self.db.execute(
                select(ReceiptOrder)
                .options(selectinload(ReceiptOrder.items))
                .where(ReceiptOrder.id == receipt_id)
            )
            receipt = receipt_result.scalar_one_or_none()

            if receipt:
                # 比对金额
                if invoice.total_amount and receipt.total_amount:
                    if abs(invoice.total_amount - receipt.total_amount) > Decimal("0.01"):
                        differences.append({
                            "field": "total_amount",
                            "invoice": float(invoice.total_amount),
                            "receipt": float(receipt.total_amount),
                        })

                # 比对明细数量
                if len(invoice.items) != len(receipt.items):
                    warnings.append("明细数量不一致")

        # 如果关联了订单，与订单比对
        if invoice.order_id:
            order_result = await self.db.execute(
                select(PurchaseOrder)
                .options(selectinload(PurchaseOrder.items))
                .where(PurchaseOrder.id == invoice.order_id)
            )
            order = order_result.scalar_one_or_none()

            if order:
                # 比对金额
                if invoice.total_amount and order.total_amount:
                    if abs(invoice.total_amount - order.total_amount) > Decimal("0.01"):
                        differences.append({
                            "field": "order_amount",
                            "invoice": float(invoice.total_amount),
                            "order": float(order.total_amount),
                        })

        return {
            "matched": len(differences) == 0,
            "differences": differences,
            "warnings": warnings,
        }
