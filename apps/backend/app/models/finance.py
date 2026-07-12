"""
财务管理数据模型

@description 财务模块相关的数据库模型

@models
- Account: 科目
- PaymentMethod: 付款方式
- Receivable: 应收账款
- Payable: 应付账款
- Payment: 收付款记录
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class AccountType(str, enum.Enum):
    """科目类型"""
    ASSET = "asset"  # 资产
    LIABILITY = "liability"  # 负债
    EQUITY = "equity"  # 所有者权益
    REVENUE = "revenue"  # 收入
    EXPENSE = "expense"  # 费用


class Account(Base):
    """
    科目表

    @description 会计科目

    @attributes
    - id: 科目ID
    - code: 科目编码
    - name: 科目名称
    - account_type: 科目类型
    - parent_id: 父科目ID
    - level: 级别
    - description: 描述
    - is_active: 是否启用
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True, comment="科目编码")
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="科目名称")
    account_type: Mapped[str] = mapped_column(
        SQLEnum(AccountType),
        nullable=False,
        comment="科目类型"
    )
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("accounts.id"), comment="父科目ID"
    )
    level: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, comment="级别"
    )
    description: Mapped[Optional[str]] = mapped_column(Text, comment="描述")
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, comment="是否启用"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="更新时间")


class PaymentMethod(Base):
    """
    付款方式表

    @description 支付/收款方式

    @attributes
    - id: 方式ID
    - code: 编码
    - name: 名称
    - description: 描述
    - is_active: 是否启用
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "payment_methods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, comment="编码")
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="名称")
    description: Mapped[Optional[str]] = mapped_column(Text, comment="描述")
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, comment="是否启用"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="更新时间")

    # 关系
    payments = relationship("Payment", back_populates="payment_method")


class ReceivableStatus(str, enum.Enum):
    """应收账款状态"""
    PENDING = "pending"  # 待收款
    PARTIAL_PAID = "partial_paid"  # 部分收款
    PAID = "paid"  # 已收款
    OVERDUE = "overdue"  # 逾期
    WRITE_OFF = "write_off"  # 坏账核销


class Receivable(Base):
    """
    应收账款表

    @description 应收账款记录

    @attributes
    - id: 记录ID
    - receivable_no: 应收单号
    - customer_id: 客户ID
    - sales_order_id: 销售订单ID
    - amount: 金额
    - paid_amount: 已收金额
    - remaining_amount: 剩余金额
    - due_date: 到期日期
    - status: 状态
    - notes: 备注
    - is_deleted: 是否删除
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "receivables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    receivable_no: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True, comment="应收单号"
    )
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("customers.id"), nullable=False, index=True, comment="客户ID"
    )
    sales_order_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("sales_orders.id"), comment="销售订单ID"
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, comment="金额"
    )
    paid_amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, default=0, comment="已收金额"
    )
    remaining_amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, comment="剩余金额"
    )
    due_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="到期日期"
    )
    status: Mapped[str] = mapped_column(
        SQLEnum(ReceivableStatus),
        default=ReceivableStatus.PENDING,
        nullable=False,
        comment="状态"
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="是否删除")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="更新时间")

    # 关系
    payments = relationship("Payment", back_populates="receivable")


class PayableStatus(str, enum.Enum):
    """应付账款状态"""
    PENDING = "pending"  # 待付款
    PARTIAL_PAID = "partial_paid"  # 部分付款
    PAID = "paid"  # 已付款
    OVERDUE = "overdue"  # 逾期


class Payable(Base):
    """
    应付账款表

    @description 应付账款记录

    @attributes
    - id: 记录ID
    - payable_no: 应付单号
    - supplier_id: 供应商ID
    - purchase_order_id: 采购订单ID
    - amount: 金额
    - paid_amount: 已付金额
    - remaining_amount: 剩余金额
    - due_date: 到期日期
    - status: 状态
    - notes: 备注
    - is_deleted: 是否删除
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "payables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    payable_no: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True, comment="应付单号"
    )
    supplier_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("suppliers.id"), nullable=False, index=True, comment="供应商ID"
    )
    purchase_order_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("purchase_orders.id"), comment="采购订单ID"
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, comment="金额"
    )
    paid_amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, default=0, comment="已付金额"
    )
    remaining_amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, comment="剩余金额"
    )
    due_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="到期日期"
    )
    status: Mapped[str] = mapped_column(
        SQLEnum(PayableStatus),
        default=PayableStatus.PENDING,
        nullable=False,
        comment="状态"
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="是否删除")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="更新时间")

    # 关系
    payments = relationship("Payment", back_populates="payable")


class PaymentType(str, enum.Enum):
    """收付款类型"""
    RECEIPT = "receipt"  # 收款
    PAYMENT = "payment"  # 付款


class PaymentStatus(str, enum.Enum):
    """收付款状态"""
    PENDING = "pending"  # 待处理
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消


class Payment(Base):
    """
    收付款记录表

    @description 收款和付款记录

    @attributes
    - id: 记录ID
    - payment_no: 收付款单号
    - payment_type: 类型（收款/付款）
    - receivable_id: 应收账款ID
    - payable_id: 应付账款ID
    - amount: 金额
    - payment_method_id: 付款方式ID
    - payment_date: 收付款日期
    - reference_no: 参考号/支票号
    - notes: 备注
    - status: 状态
    - is_deleted: 是否删除
    - created_by: 创建人ID
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    payment_no: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True, comment="收付款单号"
    )
    payment_type: Mapped[str] = mapped_column(
        SQLEnum(PaymentType),
        nullable=False,
        comment="类型"
    )
    receivable_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("receivables.id"), comment="应收账款ID"
    )
    payable_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("payables.id"), comment="应付账款ID"
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, comment="金额"
    )
    payment_method_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("payment_methods.id"), comment="付款方式ID"
    )
    payment_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="收付款日期"
    )
    reference_no: Mapped[Optional[str]] = mapped_column(
        String(100), comment="参考号/支票号"
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
    status: Mapped[str] = mapped_column(
        SQLEnum(PaymentStatus),
        default=PaymentStatus.PENDING,
        nullable=False,
        comment="状态"
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="是否删除")
    created_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), comment="创建人ID"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="更新时间")

    # 关系
    receivable = relationship("Receivable", foreign_keys=[receivable_id], back_populates="payments")
    payable = relationship("Payable", foreign_keys=[payable_id], back_populates="payments")
    payment_method = relationship("PaymentMethod", back_populates="payments")
