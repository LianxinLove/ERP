"""
发票管理数据模型

@description 销售发票和采购发票

@models
- SalesInvoice: 销售发票
- SalesInvoiceItem: 销售发票明细
- PurchaseInvoice: 采购发票
- PurchaseInvoiceItem: 采购发票明细
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class InvoiceType(str, enum.Enum):
    """发票类型"""
    VAT_SPECIAL = "vat_special"  # 增值税专用发票
    VAT_COMMON = "vat_common"  # 增值税普通发票
    VAT_ELECTRONIC = "vat_electronic"  # 增值税电子发票
    COMMERCIAL = "commercial"  # 商业发票
    OTHER = "other"  # 其他


class InvoiceStatus(str, enum.Enum):
    """发票状态"""
    DRAFT = "draft"  # 草稿
    ISSUED = "issued"  # 已开具
    SENT = "sent"  # 已发送
    RECEIVED = "received"  # 已接收
    VERIFIED = "verified"  # 已认证
    CANCELLED = "cancelled"  # 已作废
    REVERSED = "reversed"  # 已冲红


class SalesInvoice(Base):
    """
    销售发票表

    @description 销项发票

    @attributes
    - id: 发票ID
    - invoice_no: 发票号码
    - invoice_code: 发票代码
    - invoice_type: 发票类型
    - order_id: 关联订单ID
    - customer_id: 客户ID
    - invoice_date: 开票日期
    - total_amount: 总金额（不含税）
    - tax_amount: 税额
    - total_amount_with_tax: 价税合计
    - buyer_name: 购方名称
    - buyer_tax_no: 购方税号
    - buyer_address_phone: 购方地址电话
    - buyer_bank_account: 购方开户行及账号
    - seller_name: 销方名称
    - seller_tax_no: 销方税号
    - seller_address_phone: 销方地址电话
    - seller_bank_account: 销方开户行及账号
    - remarks: 备注
    - status: 状态
    - pdf_url: 发票PDF地址
    - is_deleted: 是否删除
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "sales_invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    invoice_no: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True, comment="发票号码"
    )
    invoice_code: Mapped[Optional[str]] = mapped_column(
        String(50), comment="发票代码"
    )
    invoice_type: Mapped[str] = mapped_column(
        SQLEnum(InvoiceType),
        default=InvoiceType.VAT_ELECTRONIC,
        nullable=False,
        comment="发票类型"
    )
    order_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("sales_orders.id"), comment="关联订单ID"
    )
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("customers.id"), nullable=False, comment="客户ID"
    )
    invoice_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="开票日期"
    )
    total_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, default=0, comment="总金额（不含税）"
    )
    tax_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, default=0, comment="税额"
    )
    total_amount_with_tax: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, default=0, comment="价税合计"
    )

    # 购方信息
    buyer_name: Mapped[Optional[str]] = mapped_column(
        String(200), comment="购方名称"
    )
    buyer_tax_no: Mapped[Optional[str]] = mapped_column(
        String(50), comment="购方税号"
    )
    buyer_address_phone: Mapped[Optional[str]] = mapped_column(
        String(200), comment="购方地址电话"
    )
    buyer_bank_account: Mapped[Optional[str]] = mapped_column(
        String(200), comment="购方开户行及账号"
    )

    # 销方信息
    seller_name: Mapped[Optional[str]] = mapped_column(
        String(200), comment="销方名称"
    )
    seller_tax_no: Mapped[Optional[str]] = mapped_column(
        String(50), comment="销方税号"
    )
    seller_address_phone: Mapped[Optional[str]] = mapped_column(
        String(200), comment="销方地址电话"
    )
    seller_bank_account: Mapped[Optional[str]] = mapped_column(
        String(200), comment="销方开户行及账号"
    )

    remarks: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
    status: Mapped[str] = mapped_column(
        SQLEnum(InvoiceStatus),
        default=InvoiceStatus.DRAFT,
        nullable=False,
        comment="状态"
    )
    pdf_url: Mapped[Optional[str]] = mapped_column(
        String(500), comment="发票PDF地址"
    )

    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="是否删除")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="更新时间")

    # 关系
    items = relationship("SalesInvoiceItem", back_populates="invoice", cascade="all, delete-orphan")


class SalesInvoiceItem(Base):
    """
    销售发票明细表

    @description 销售发票的明细项

    @attributes
    - id: 明细ID
    - invoice_id: 发票ID
    - product_code: 产品编码
    - product_name: 产品名称
    - specification: 规格型号
    - unit: 单位
    - quantity: 数量
    - unit_price: 单价
    - amount: 金额
    - tax_rate: 税率
    - tax_amount: 税额
    """

    __tablename__ = "sales_invoice_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    invoice_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sales_invoices.id"), nullable=False, comment="发票ID"
    )
    product_code: Mapped[Optional[str]] = mapped_column(String(50), comment="产品编码")
    product_name: Mapped[str] = mapped_column(String(200), nullable=False, comment="产品名称")
    specification: Mapped[Optional[str]] = mapped_column(String(100), comment="规格型号")
    unit: Mapped[Optional[str]] = mapped_column(String(20), comment="单位")
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, comment="数量"
    )
    unit_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, comment="单价"
    )
    amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, comment="金额"
    )
    tax_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2), nullable=True, comment="税率"
    )
    tax_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, comment="税额"
    )

    # 关系
    invoice = relationship("SalesInvoice", back_populates="items")


class PurchaseInvoice(Base):
    """
    采购发票表（进项发票）

    @description 采购发票

    @attributes
    - id: 发票ID
    - invoice_no: 发票号码
    - invoice_code: 发票代码
    - invoice_type: 发票类型
    - order_id: 关联订单ID
    - supplier_id: 供应商ID
    - invoice_date: 开票日期
    - total_amount: 总金额（不含税）
    - tax_amount: 税额
    - total_amount_with_tax: 价税合计
    - buyer_name: 购方名称
    - buyer_tax_no: 购方税号
    - seller_name: 销方名称
    - seller_tax_no: 销方税号
    - remarks: 备注
    - status: 状态
    - verification_status: 认证状态
    - verification_date: 认证日期
    - pdf_url: 发票PDF地址
    - is_deleted: 是否删除
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "purchase_invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    invoice_no: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True, comment="发票号码"
    )
    invoice_code: Mapped[Optional[str]] = mapped_column(
        String(50), comment="发票代码"
    )
    invoice_type: Mapped[str] = mapped_column(
        SQLEnum(InvoiceType),
        default=InvoiceType.VAT_ELECTRONIC,
        nullable=False,
        comment="发票类型"
    )
    order_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("purchase_orders.id"), comment="关联订单ID"
    )
    supplier_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("suppliers.id"), nullable=False, comment="供应商ID"
    )
    invoice_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="开票日期"
    )
    total_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, default=0, comment="总金额（不含税）"
    )
    tax_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, default=0, comment="税额"
    )
    total_amount_with_tax: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, default=0, comment="价税合计"
    )

    # 购方信息（本公司）
    buyer_name: Mapped[Optional[str]] = mapped_column(
        String(200), comment="购方名称"
    )
    buyer_tax_no: Mapped[Optional[str]] = mapped_column(
        String(50), comment="购方税号"
    )

    # 销方信息（供应商）
    seller_name: Mapped[Optional[str]] = mapped_column(
        String(200), comment="销方名称"
    )
    seller_tax_no: Mapped[Optional[str]] = mapped_column(
        String(50), comment="销方税号"
    )

    remarks: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
    status: Mapped[str] = mapped_column(
        SQLEnum(InvoiceStatus),
        default=InvoiceStatus.DRAFT,
        nullable=False,
        comment="状态"
    )
    verification_status: Mapped[Optional[str]] = mapped_column(
        String(20), comment="认证状态"
    )
    verification_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="认证日期"
    )
    pdf_url: Mapped[Optional[str]] = mapped_column(
        String(500), comment="发票PDF地址"
    )

    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="是否删除")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="更新时间")

    # 关系
    items = relationship("PurchaseInvoiceItem", back_populates="invoice", cascade="all, delete-orphan")


class PurchaseInvoiceItem(Base):
    """
    采购发票明细表

    @description 采购发票的明细项

    @attributes
    - id: 明细ID
    - invoice_id: 发票ID
    - product_code: 产品编码
    - product_name: 产品名称
    - specification: 规格型号
    - unit: 单位
    - quantity: 数量
    - unit_price: 单价
    - amount: 金额
    - tax_rate: 税率
    - tax_amount: 税额
    """

    __tablename__ = "purchase_invoice_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    invoice_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("purchase_invoices.id"), nullable=False, comment="发票ID"
    )
    product_code: Mapped[Optional[str]] = mapped_column(String(50), comment="产品编码")
    product_name: Mapped[str] = mapped_column(String(200), nullable=False, comment="产品名称")
    specification: Mapped[Optional[str]] = mapped_column(String(100), comment="规格型号")
    unit: Mapped[Optional[str]] = mapped_column(String(20), comment="单位")
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, comment="数量"
    )
    unit_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, comment="单价"
    )
    amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, comment="金额"
    )
    tax_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2), nullable=True, comment="税率"
    )
    tax_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, comment="税额"
    )

    # 关系
    invoice = relationship("PurchaseInvoice", back_populates="items")
