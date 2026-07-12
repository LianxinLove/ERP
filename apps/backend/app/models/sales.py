"""
销售管理数据模型

@description 销售模块相关的数据库模型，包含发货单等完善功能

@models
- Customer: 客户
- SalesOrder: 销售订单
- SalesOrderItem: 销售订单明细
- SalesReturn: 销售退货
- SalesReturnItem: 销售退货明细
- DeliveryOrder: 发货单（新增）
- DeliveryOrderItem: 发货单明细（新增）
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class CustomerStatus(str, enum.Enum):
    """客户状态"""
    ACTIVE = "active"  # 正常
    INACTIVE = "inactive"  # 停用
    BLACKLIST = "blacklist"  # 黑名单


class Customer(Base):
    """
    客户表

    @description 存储客户基本信息

    @attributes
    - id: 客户ID
    - code: 客户编码（唯一）
    - name: 客户名称
    - contact: 联系人
    - phone: 联系电话
    - email: 邮箱
    - address: 地址
    - tax_number: 税号
    - bank_name: 开户银行
    - bank_account: 银行账号
    - credit_limit: 信用额度
    - payment_terms: 付款条件（天数）
    - notes: 备注
    - status: 状态
    - is_deleted: 是否删除
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True, comment="客户编码")
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="客户名称")
    contact: Mapped[Optional[str]] = mapped_column(String(100), comment="联系人")
    phone: Mapped[Optional[str]] = mapped_column(String(50), comment="联系电话")
    email: Mapped[Optional[str]] = mapped_column(String(100), comment="邮箱")
    address: Mapped[Optional[str]] = mapped_column(Text, comment="地址")
    tax_number: Mapped[Optional[str]] = mapped_column(String(50), comment="税号")
    bank_name: Mapped[Optional[str]] = mapped_column(String(100), comment="开户银行")
    bank_account: Mapped[Optional[str]] = mapped_column(String(50), comment="银行账号")
    credit_limit: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, default=0, comment="信用额度"
    )
    credit_used: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, default=0, comment="已用信用额度"
    )
    payment_terms: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=30, comment="付款条件（天数）"
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
    status: Mapped[str] = mapped_column(
        SQLEnum(CustomerStatus),
        default=CustomerStatus.ACTIVE,
        nullable=False,
        comment="状态"
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="是否删除")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="更新时间")

    # 关系
    sales_orders = relationship("SalesOrder", back_populates="customer")
    delivery_orders = relationship("DeliveryOrder", back_populates="customer")


class SalesOrderStatus(str, enum.Enum):
    """销售订单状态"""
    DRAFT = "draft"  # 草稿
    PENDING = "pending"  # 待审核
    CONFIRMED = "confirmed"  # 已确认
    PARTIAL_SHIPPED = "partial_shipped"  # 部分发货
    SHIPPED = "shipped"  # 已发货
    PARTIAL_PAID = "partial_paid"  # 部分收款
    PAID = "paid"  # 已收款
    CANCELLED = "cancelled"  # 已取消
    CLOSED = "closed"  # 已关闭


class SalesOrder(Base):
    """
    销售订单表

    @description 销售订单主表

    @attributes
    - id: 订单ID
    - order_no: 订单号（唯一）
    - customer_id: 客户ID
    - order_date: 订单日期
    - delivery_date: 交货日期
    - total_amount: 总金额
    - tax_amount: 税额
    - tax_inclusive: 是否含税
    - discount_amount: 折扣金额
    - paid_amount: 已收金额
    - payment_terms: 付款条件
    - delivery_address: 送货地址
    - contact: 联系人
    - contact_phone: 联系电话
    - salesperson_id: 销售员ID
    - notes: 备注
    - status: 状态
    - is_deleted: 是否删除
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "sales_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_no: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True, comment="订单号"
    )
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("customers.id"), nullable=False, comment="客户ID"
    )
    order_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="订单日期"
    )
    delivery_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="交货日期"
    )
    total_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, default=0, comment="总金额"
    )
    tax_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, default=0, comment="税额"
    )
    tax_inclusive: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="是否含税"
    )
    discount_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, default=0, comment="折扣金额"
    )
    paid_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, default=0, comment="已收金额"
    )
    payment_terms: Mapped[Optional[int]] = mapped_column(
        Integer, comment="付款条件（天数）"
    )
    delivery_address: Mapped[Optional[str]] = mapped_column(Text, comment="送货地址")
    contact: Mapped[Optional[str]] = mapped_column(String(100), comment="联系人")
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50), comment="联系电话")
    salesperson_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), comment="销售员ID"
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
    status: Mapped[str] = mapped_column(
        SQLEnum(SalesOrderStatus),
        default=SalesOrderStatus.DRAFT,
        nullable=False,
        comment="状态"
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="是否删除")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="更新时间")

    # 关系
    customer = relationship("Customer", back_populates="sales_orders")
    items = relationship("SalesOrderItem", back_populates="order", cascade="all, delete-orphan")
    delivery_orders = relationship("DeliveryOrder", back_populates="sales_order")


class SalesOrderItem(Base):
    """
    销售订单明细表

    @description 销售订单的明细项

    @attributes
    - id: 明细ID
    - order_id: 订单ID
    - product_code: 产品编码
    - product_name: 产品名称
    - specification: 规格型号
    - unit: 单位
    - quantity: 数量
    - shipped_quantity: 已发货数量
    - unit_price: 单价
    - discount_rate: 折扣率
    - amount: 金额
    - tax_rate: 税率
    - notes: 备注
    """

    __tablename__ = "sales_order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sales_orders.id"), nullable=False, comment="订单ID"
    )
    product_code: Mapped[Optional[str]] = mapped_column(String(50), comment="产品编码")
    product_name: Mapped[str] = mapped_column(String(200), nullable=False, comment="产品名称")
    specification: Mapped[Optional[str]] = mapped_column(String(100), comment="规格型号")
    unit: Mapped[Optional[str]] = mapped_column(String(20), comment="单位")
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, comment="数量"
    )
    shipped_quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=True, default=0, comment="已发货数量"
    )
    unit_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, comment="单价"
    )
    discount_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2), nullable=True, comment="折扣率(%)"
    )
    amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, comment="金额"
    )
    tax_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2), nullable=True, comment="税率"
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")

    # 关系
    order = relationship("SalesOrder", back_populates="items")


class DeliveryOrderStatus(str, enum.Enum):
    """发货单状态"""
    DRAFT = "draft"  # 草稿
    PENDING = "pending"  # 待发货
    SHIPPED = "shipped"  # 已发货
    PARTIAL_RECEIVED = "partial_received"  # 部分签收
    RECEIVED = "received"  # 已签收
    CANCELLED = "cancelled"  # 已取消


class DeliveryOrder(Base):
    """
    发货单表

    @description 销售发货单，用于跟踪发货和物流信息

    @attributes
    - id: 发货单ID
    - delivery_no: 发货单号（唯一）
    - order_id: 销售订单ID
    - customer_id: 客户ID
    - delivery_date: 发货日期
    - warehouse_id: 发货仓库ID
    - total_amount: 总金额
    - total_quantity: 总数量
    - delivery_address: 送货地址
    - contact: 联系人
    - contact_phone: 联系电话
    - logistics_company: 物流公司
    - logistics_no: 物流单号
    - logistics_fee: 物流费用
    - notes: 备注
    - status: 状态
    - shipped_at: 发货时间
    - received_at: 签收时间
    - received_by: 签收人
    - is_deleted: 是否删除
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "delivery_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    delivery_no: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True, comment="发货单号"
    )
    order_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("sales_orders.id"), comment="销售订单ID"
    )
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("customers.id"), nullable=False, comment="客户ID"
    )
    delivery_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="发货日期"
    )
    warehouse_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("warehouses.id"), comment="发货仓库ID"
    )
    total_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, default=0, comment="总金额"
    )
    total_quantity: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, default=0, comment="总数量"
    )

    # 收货信息
    delivery_address: Mapped[Optional[str]] = mapped_column(Text, comment="送货地址")
    contact: Mapped[Optional[str]] = mapped_column(String(100), comment="联系人")
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50), comment="联系电话")

    # 物流信息
    logistics_company: Mapped[Optional[str]] = mapped_column(
        String(100), comment="物流公司"
    )
    logistics_no: Mapped[Optional[str]] = mapped_column(
        String(50), comment="物流单号"
    )
    logistics_fee: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, comment="物流费用"
    )

    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
    status: Mapped[str] = mapped_column(
        SQLEnum(DeliveryOrderStatus),
        default=DeliveryOrderStatus.DRAFT,
        nullable=False,
        comment="状态"
    )

    # 时间戳
    shipped_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="发货时间"
    )
    received_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="签收时间"
    )
    received_by: Mapped[Optional[str]] = mapped_column(
        String(100), comment="签收人"
    )

    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="是否删除")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="更新时间")

    # 关系
    customer = relationship("Customer", back_populates="delivery_orders")
    sales_order = relationship("SalesOrder", back_populates="delivery_orders", foreign_keys=[order_id])
    items = relationship("DeliveryOrderItem", back_populates="delivery_order", cascade="all, delete-orphan")


class DeliveryOrderItem(Base):
    """
    发货单明细表

    @description 发货单的明细项

    @attributes
    - id: 明细ID
    - delivery_id: 发货单ID
    - order_item_id: 销售订单明细ID
    - product_code: 产品编码
    - product_name: 产品名称
    - specification: 规格型号
    - unit: 单位
    - quantity: 数量
    - unit_price: 单价
    - amount: 金额
    - batch_no: 批号
    - notes: 备注
    """

    __tablename__ = "delivery_order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    delivery_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("delivery_orders.id"), nullable=False, comment="发货单ID"
    )
    order_item_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("sales_order_items.id"), comment="销售订单明细ID"
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
    batch_no: Mapped[Optional[str]] = mapped_column(
        String(50), comment="批号"
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")

    # 关系
    delivery_order = relationship("DeliveryOrder", back_populates="items")


class SalesReturnStatus(str, enum.Enum):
    """销售退货状态"""
    DRAFT = "draft"  # 草稿
    PENDING = "pending"  # 待审核
    APPROVED = "approved"  # 已批准
    REJECTED = "rejected"  # 已拒绝
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消


class SalesReturn(Base):
    """
    销售退货表

    @description 销售退货主表

    @attributes
    - id: 退货ID
    - return_no: 退货单号（唯一）
    - order_id: 原销售订单ID
    - customer_id: 客户ID
    - return_date: 退货日期
    - total_amount: 总金额
    - refund_amount: 退款金额
    - reason: 退货原因
    - notes: 备注
    - status: 状态
    - is_deleted: 是否删除
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "sales_returns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    return_no: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True, comment="退货单号"
    )
    order_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("sales_orders.id"), comment="原销售订单ID"
    )
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("customers.id"), nullable=False, comment="客户ID"
    )
    return_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="退货日期"
    )
    total_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, default=0, comment="总金额"
    )
    refund_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, default=0, comment="退款金额"
    )
    reason: Mapped[Optional[str]] = mapped_column(Text, comment="退货原因")
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
    status: Mapped[str] = mapped_column(
        SQLEnum(SalesReturnStatus),
        default=SalesReturnStatus.DRAFT,
        nullable=False,
        comment="状态"
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="是否删除")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="更新时间")

    # 关系
    items = relationship("SalesReturnItem", back_populates="sales_return", cascade="all, delete-orphan")


class SalesReturnItem(Base):
    """
    销售退货明细表

    @description 销售退货的明细项

    @attributes
    - id: 明细ID
    - return_id: 退货ID
    - product_code: 产品编码
    - product_name: 产品名称
    - specification: 规格型号
    - unit: 单位
    - quantity: 数量
    - unit_price: 单价
    - amount: 金额
    - notes: 备注
    """

    __tablename__ = "sales_return_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    return_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sales_returns.id"), nullable=False, comment="退货ID"
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
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")

    # 关系
    sales_return = relationship("SalesReturn", back_populates="items")
