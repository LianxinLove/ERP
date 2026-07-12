"""
财务管理服务层

@description 财务模块的业务逻辑

@services
- AccountService: 科目服务
- PaymentMethodService: 付款方式服务
- ReceivableService: 应收账款服务
- PayableService: 应付账款服务
- PaymentService: 收付款记录服务
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import select, and_, or_, func, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.finance import (
    Account,
    PaymentMethod,
    Receivable,
    ReceivableStatus,
    Payable,
    PayableStatus,
    Payment,
    PaymentType,
    PaymentStatus,
)
from app.models.sales import Customer
from app.models.purchase import Supplier
from app.schemas.finance import (
    AccountCreate,
    AccountUpdate,
    PaymentMethodCreate,
    PaymentMethodUpdate,
    ReceivableCreate,
    ReceivableUpdate,
    PayableCreate,
    PayableUpdate,
    PaymentCreate,
    PaymentUpdate,
)


class AccountService:
    """科目服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_account(self, data: AccountCreate) -> Account:
        """创建科目"""
        # 检查编码是否已存在
        result = await self.db.execute(
            select(Account).where(Account.code == data.code)
        )
        if result.scalar_one_or_none():
            raise BadRequestError("科目编码已存在")

        # 如果有父科目，验证并计算级别
        level = data.level
        if data.parent_id:
            parent = await self.get_account(data.parent_id)
            level = parent.level + 1

        account = Account(
            **data.model_dump(exclude={'parent_id'}),
            parent_id=data.parent_id,
            level=level,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.db.add(account)
        await self.db.commit()
        await self.db.refresh(account)

        return account

    async def get_accounts(
        self,
        account_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Account]:
        """获取科目列表"""
        query = select(Account)

        if account_type:
            query = query.where(Account.account_type == account_type)

        if is_active is not None:
            query = query.where(Account.is_active == is_active)

        query = query.order_by(Account.code).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_account_tree(self) -> List[dict]:
        """获取科目树形结构"""
        # 获取所有科目
        result = await self.db.execute(
            select(Account).where(Account.is_active == True).order_by(Account.code)
        )
        accounts = result.scalars().all()

        # 构建树形结构
        account_map = {acc.id: {
            'id': acc.id,
            'code': acc.code,
            'name': acc.name,
            'account_type': acc.account_type,
            'parent_id': acc.parent_id,
            'level': acc.level,
            'description': acc.description,
            'is_active': acc.is_active,
            'children': []
        } for acc in accounts}

        tree = []
        for account in accounts:
            node = account_map[account.id]
            if account.parent_id and account.parent_id in account_map:
                account_map[account.parent_id]['children'].append(node)
            else:
                tree.append(node)

        return tree

    async def get_account(self, account_id: int) -> Account:
        """获取科目详情"""
        result = await self.db.execute(
            select(Account).where(Account.id == account_id)
        )
        account = result.scalar_one_or_none()

        if not account:
            raise NotFoundError("科目不存在")

        return account

    async def update_account(self, account_id: int, data: AccountUpdate) -> Account:
        """更新科目"""
        account = await self.get_account(account_id)

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(account, field, value)

        account.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(account)

        return account

    async def delete_account(self, account_id: int) -> None:
        """删除科目"""
        account = await self.get_account(account_id)

        # 检查是否有子科目
        result = await self.db.execute(
            select(func.count(Account.id)).where(Account.parent_id == account_id)
        )
        count = result.scalar()

        if count > 0:
            raise BadRequestError("该科目下有子科目，无法删除")

        # 软删除
        account.is_active = False
        account.updated_at = datetime.now(timezone.utc)
        await self.db.commit()


class PaymentMethodService:
    """付款方式服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_payment_method(self, data: PaymentMethodCreate) -> PaymentMethod:
        """创建付款方式"""
        # 检查编码是否已存在
        result = await self.db.execute(
            select(PaymentMethod).where(PaymentMethod.code == data.code)
        )
        if result.scalar_one_or_none():
            raise BadRequestError("付款方式编码已存在")

        payment_method = PaymentMethod(
            **data.model_dump(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.db.add(payment_method)
        await self.db.commit()
        await self.db.refresh(payment_method)

        return payment_method

    async def get_payment_methods(
        self,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[PaymentMethod]:
        """获取付款方式列表"""
        query = select(PaymentMethod)

        if is_active is not None:
            query = query.where(PaymentMethod.is_active == is_active)

        query = query.order_by(PaymentMethod.code).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_payment_method(self, payment_method_id: int) -> PaymentMethod:
        """获取付款方式详情"""
        result = await self.db.execute(
            select(PaymentMethod).where(PaymentMethod.id == payment_method_id)
        )
        payment_method = result.scalar_one_or_none()

        if not payment_method:
            raise NotFoundError("付款方式不存在")

        return payment_method

    async def update_payment_method(
        self, payment_method_id: int, data: PaymentMethodUpdate
    ) -> PaymentMethod:
        """更新付款方式"""
        payment_method = await self.get_payment_method(payment_method_id)

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(payment_method, field, value)

        payment_method.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(payment_method)

        return payment_method

    async def delete_payment_method(self, payment_method_id: int) -> None:
        """删除付款方式"""
        payment_method = await self.get_payment_method(payment_method_id)

        # 检查是否有关联的收付款记录
        result = await self.db.execute(
            select(func.count(Payment.id)).where(
                Payment.payment_method_id == payment_method_id,
                Payment.is_deleted == False,
            )
        )
        count = result.scalar()

        if count > 0:
            raise BadRequestError("该付款方式有关联的收付款记录，无法删除")

        payment_method.is_active = False
        payment_method.updated_at = datetime.now(timezone.utc)
        await self.db.commit()


class ReceivableService:
    """应收账款服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_receivable(self, data: ReceivableCreate) -> Receivable:
        """创建应收账款"""
        # 验证客户
        result = await self.db.execute(
            select(Customer).where(Customer.id == data.customer_id)
        )
        if not result.scalar_one_or_none():
            raise BadRequestError("客户不存在")

        # 生成应收单号
        receivable_no = f"AR-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        receivable = Receivable(
            **data.model_dump(),
            receivable_no=receivable_no,
            paid_amount=Decimal(0),
            remaining_amount=data.amount,
            status=ReceivableStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.db.add(receivable)
        await self.db.commit()
        await self.db.refresh(receivable)

        return receivable

    async def get_receivables(
        self,
        customer_id: Optional[int] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Receivable]:
        """获取应收账款列表"""
        query = select(Receivable).where(Receivable.is_deleted == False)

        if customer_id:
            query = query.where(Receivable.customer_id == customer_id)

        if status:
            query = query.where(Receivable.status == status)

        if keyword:
            query = query.where(Receivable.receivable_no.like(f"%{keyword}%"))

        query = query.order_by(Receivable.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_receivable(self, receivable_id: int) -> Receivable:
        """获取应收账款详情"""
        result = await self.db.execute(
            select(Receivable)
            .options(selectinload(Receivable.payments))
            .where(
                Receivable.id == receivable_id,
                Receivable.is_deleted == False,
            )
        )
        receivable = result.scalar_one_or_none()

        if not receivable:
            raise NotFoundError("应收账款不存在")

        return receivable

    async def update_receivable(
        self, receivable_id: int, data: ReceivableUpdate
    ) -> Receivable:
        """更新应收账款"""
        receivable = await self.get_receivable(receivable_id)

        for field, value in data.model_dump(exclude_unset=True).items():
            if field == 'amount' and value is not None:
                # 更新金额时需同步剩余金额
                receivable.remaining_amount = value - receivable.paid_amount
            setattr(receivable, field, value)

        receivable.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(receivable)

        return receivable

    async def update_receivable_status(self, receivable_id: int) -> Receivable:
        """更新应收账款状态"""
        receivable = await self.get_receivable(receivable_id)

        # 根据已收金额和剩余金额更新状态
        if receivable.remaining_amount <= 0:
            receivable.status = ReceivableStatus.PAID
        elif receivable.paid_amount > 0:
            receivable.status = ReceivableStatus.PARTIAL_PAID
        elif receivable.due_date and receivable.due_date < datetime.now(timezone.utc):
            receivable.status = ReceivableStatus.OVERDUE
        else:
            receivable.status = ReceivableStatus.PENDING

        receivable.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(receivable)

        return receivable

    async def delete_receivable(self, receivable_id: int) -> None:
        """删除应收账款（软删除）"""
        receivable = await self.get_receivable(receivable_id)

        if receivable.paid_amount > 0:
            raise BadRequestError("该应收账款已有收款记录，无法删除")

        receivable.is_deleted = True
        receivable.updated_at = datetime.now(timezone.utc)
        await self.db.commit()

    async def check_overdue_receivables(self) -> List[Receivable]:
        """检查逾期应收账款"""
        result = await self.db.execute(
            select(Receivable).where(
                and_(
                    Receivable.status.in_([
                        ReceivableStatus.PENDING,
                        ReceivableStatus.PARTIAL_PAID,
                    ]),
                    Receivable.due_date < datetime.now(timezone.utc),
                    Receivable.remaining_amount > 0,
                    Receivable.is_deleted == False,
                )
            )
        )
        receivables = result.scalars().all()

        # 更新状态
        for receivable in receivables:
            receivable.status = ReceivableStatus.OVERDUE
            receivable.updated_at = datetime.now(timezone.utc)

        await self.db.commit()

        return receivables


class PayableService:
    """应付账款服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_payable(self, data: PayableCreate) -> Payable:
        """创建应付账款"""
        # 验证供应商
        result = await self.db.execute(
            select(Supplier).where(Supplier.id == data.supplier_id)
        )
        if not result.scalar_one_or_none():
            raise BadRequestError("供应商不存在")

        # 生成应付单号
        payable_no = f"AP-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        payable = Payable(
            **data.model_dump(),
            payable_no=payable_no,
            paid_amount=Decimal(0),
            remaining_amount=data.amount,
            status=PayableStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.db.add(payable)
        await self.db.commit()
        await self.db.refresh(payable)

        return payable

    async def get_payables(
        self,
        supplier_id: Optional[int] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Payable]:
        """获取应付账款列表"""
        query = select(Payable).where(Payable.is_deleted == False)

        if supplier_id:
            query = query.where(Payable.supplier_id == supplier_id)

        if status:
            query = query.where(Payable.status == status)

        if keyword:
            query = query.where(Payable.payable_no.like(f"%{keyword}%"))

        query = query.order_by(Payable.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_payable(self, payable_id: int) -> Payable:
        """获取应付账款详情"""
        result = await self.db.execute(
            select(Payable)
            .options(selectinload(Payable.payments))
            .where(
                Payable.id == payable_id,
                Payable.is_deleted == False,
            )
        )
        payable = result.scalar_one_or_none()

        if not payable:
            raise NotFoundError("应付账款不存在")

        return payable

    async def update_payable(
        self, payable_id: int, data: PayableUpdate
    ) -> Payable:
        """更新应付账款"""
        payable = await self.get_payable(payable_id)

        for field, value in data.model_dump(exclude_unset=True).items():
            if field == 'amount' and value is not None:
                # 更新金额时需同步剩余金额
                payable.remaining_amount = value - payable.paid_amount
            setattr(payable, field, value)

        payable.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(payable)

        return payable

    async def update_payable_status(self, payable_id: int) -> Payable:
        """更新应付账款状态"""
        payable = await self.get_payable(payable_id)

        # 根据已付金额和剩余金额更新状态
        if payable.remaining_amount <= 0:
            payable.status = PayableStatus.PAID
        elif payable.paid_amount > 0:
            payable.status = PayableStatus.PARTIAL_PAID
        elif payable.due_date and payable.due_date < datetime.now(timezone.utc):
            payable.status = PayableStatus.OVERDUE
        else:
            payable.status = PayableStatus.PENDING

        payable.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(payable)

        return payable

    async def delete_payable(self, payable_id: int) -> None:
        """删除应付账款（软删除）"""
        payable = await self.get_payable(payable_id)

        if payable.paid_amount > 0:
            raise BadRequestError("该应付账款已有付款记录，无法删除")

        payable.is_deleted = True
        payable.updated_at = datetime.now(timezone.utc)
        await self.db.commit()

    async def check_overdue_payables(self) -> List[Payable]:
        """检查逾期应付账款"""
        result = await self.db.execute(
            select(Payable).where(
                and_(
                    Payable.status.in_([
                        PayableStatus.PENDING,
                        PayableStatus.PARTIAL_PAID,
                    ]),
                    Payable.due_date < datetime.now(timezone.utc),
                    Payable.remaining_amount > 0,
                    Payable.is_deleted == False,
                )
            )
        )
        payables = result.scalars().all()

        # 更新状态
        for payable in payables:
            payable.status = PayableStatus.OVERDUE
            payable.updated_at = datetime.now(timezone.utc)

        await self.db.commit()

        return payables


class PaymentService:
    """收付款记录服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_payment(self, data: PaymentCreate, created_by: int) -> Payment:
        """创建收付款记录"""
        # 验证付款方式
        if data.payment_method_id:
            result = await self.db.execute(
                select(PaymentMethod).where(PaymentMethod.id == data.payment_method_id)
            )
            if not result.scalar_one_or_none():
                raise BadRequestError("付款方式不存在")

        # 生成收付款单号
        prefix = "RCPT" if data.payment_type == PaymentType.RECEIPT else "PAY"
        payment_no = f"{prefix}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        payment = Payment(
            **data.model_dump(),
            payment_no=payment_no,
            created_by=created_by,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.db.add(payment)
        await self.db.flush()

        # 更新关联的应收/应付账款
        if data.payment_type == PaymentType.RECEIPT and data.receivable_id:
            await self._process_receipt_payment(payment)
        elif data.payment_type == PaymentType.PAYMENT and data.payable_id:
            await self._process_payment_payment(payment)

        await self.db.commit()
        await self.db.refresh(payment)

        return payment

    async def _process_receipt_payment(self, payment: Payment) -> None:
        """处理收款关联应收账款"""
        receivable_service = ReceivableService(self.db)
        receivable = await receivable_service.get_receivable(payment.receivable_id)

        if payment.amount > receivable.remaining_amount:
            raise BadRequestError("收款金额超过剩余应收金额")

        # 更新应收账款
        receivable.paid_amount += payment.amount
        receivable.remaining_amount -= payment.amount
        await receivable_service.update_receivable_status(receivable.id)

    async def _process_payment_payment(self, payment: Payment) -> None:
        """处理付款关联应付账款"""
        payable_service = PayableService(self.db)
        payable = await payable_service.get_payable(payment.payable_id)

        if payment.amount > payable.remaining_amount:
            raise BadRequestError("付款金额超过剩余应付金额")

        # 更新应付账款
        payable.paid_amount += payment.amount
        payable.remaining_amount -= payment.amount
        await payable_service.update_payable_status(payable.id)

    async def get_payments(
        self,
        payment_type: Optional[str] = None,
        status: Optional[str] = None,
        receivable_id: Optional[int] = None,
        payable_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Payment]:
        """获取收付款记录列表"""
        query = select(Payment).where(Payment.is_deleted == False)

        if payment_type:
            query = query.where(Payment.payment_type == payment_type)

        if status:
            query = query.where(Payment.status == status)

        if receivable_id:
            query = query.where(Payment.receivable_id == receivable_id)

        if payable_id:
            query = query.where(Payment.payable_id == payable_id)

        query = query.order_by(Payment.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_payment(self, payment_id: int) -> Payment:
        """获取收付款记录详情"""
        result = await self.db.execute(
            select(Payment).where(
                Payment.id == payment_id,
                Payment.is_deleted == False,
            )
        )
        payment = result.scalar_one_or_none()

        if not payment:
            raise NotFoundError("收付款记录不存在")

        return payment

    async def update_payment(
        self, payment_id: int, data: PaymentUpdate
    ) -> Payment:
        """更新收付款记录"""
        payment = await self.get_payment(payment_id)

        if payment.status == PaymentStatus.COMPLETED:
            raise BadRequestError("已完成的收付款记录无法修改")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(payment, field, value)

        payment.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(payment)

        return payment

    async def complete_payment(self, payment_id: int) -> Payment:
        """完成收付款"""
        payment = await self.get_payment(payment_id)

        if payment.status != PaymentStatus.PENDING:
            raise BadRequestError(f"收付款状态为{payment.status}，无法完成")

        payment.status = PaymentStatus.COMPLETED
        payment.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(payment)

        return payment

    async def cancel_payment(self, payment_id: int) -> Payment:
        """取消收付款"""
        payment = await self.get_payment(payment_id)

        if payment.status == PaymentStatus.COMPLETED:
            raise BadRequestError("已完成的收付款记录无法取消")

        payment.status = PaymentStatus.CANCELLED
        payment.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(payment)

        return payment

    async def delete_payment(self, payment_id: int) -> None:
        """删除收付款记录（软删除）"""
        payment = await self.get_payment(payment_id)

        if payment.status == PaymentStatus.COMPLETED:
            raise BadRequestError("已完成的收付款记录无法删除")

        payment.is_deleted = True
        payment.updated_at = datetime.now(timezone.utc)
        await self.db.commit()

    async def get_finance_summary(self) -> dict:
        """获取财务汇总数据"""
        # 应收账款汇总
        result = await self.db.execute(
            select(
                func.sum(Receivable.amount).label('total_receivable'),
                func.sum(Receivable.paid_amount).label('total_paid'),
                func.sum(Receivable.remaining_amount).label('total_remaining'),
                func.count(case(
                    (Receivable.status == ReceivableStatus.OVERDUE, 1),
                    else_=None
                )).label('overdue_count'),
            ).where(Receivable.is_deleted == False)
        )
        row = result.one()
        receivable_summary = {
            'total_receivable': row.total_receivable or Decimal(0),
            'total_paid_receivable': row.total_paid or Decimal(0),
            'total_remaining_receivable': row.total_remaining or Decimal(0),
            'overdue_receivable_count': row.overdue_count or 0,
        }

        # 应付账款汇总
        result = await self.db.execute(
            select(
                func.sum(Payable.amount).label('total_payable'),
                func.sum(Payable.paid_amount).label('total_paid'),
                func.sum(Payable.remaining_amount).label('total_remaining'),
                func.count(case(
                    (Payable.status == PayableStatus.OVERDUE, 1),
                    else_=None
                )).label('overdue_count'),
            ).where(Payable.is_deleted == False)
        )
        row = result.one()
        payable_summary = {
            'total_payable': row.total_payable or Decimal(0),
            'total_paid_payable': row.total_paid or Decimal(0),
            'total_remaining_payable': row.total_remaining or Decimal(0),
            'overdue_payable_count': row.overdue_count or 0,
        }

        # 收付款汇总
        result = await self.db.execute(
            select(
                func.sum(case(
                    (Payment.payment_type == PaymentType.RECEIPT, Payment.amount),
                    else_=0
                )).label('total_in'),
                func.sum(case(
                    (Payment.payment_type == PaymentType.PAYMENT, Payment.amount),
                    else_=0
                )).label('total_out'),
            ).where(
                and_(
                    Payment.status == PaymentStatus.COMPLETED,
                    Payment.is_deleted == False,
                )
            )
        )
        row = result.one()
        payment_summary = {
            'total_payment_in': row.total_in or Decimal(0),
            'total_payment_out': row.total_out or Decimal(0),
        }

        return {
            **receivable_summary,
            **payable_summary,
            **payment_summary,
        }
