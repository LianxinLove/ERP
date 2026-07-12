"""
采购管理数据模型

@description 采购模块相关的数据库模型，包含收货单等完善功能

@models
- Supplier: 供应商
- PurchaseRequest: 采购申请
- PurchaseRequestItem: 采购申请明细
- PurchaseOrder: 采购订单
- PurchaseOrderItem: 采购订单明细
- ReceiptOrder: 收货单（新增）
- ReceiptOrderItem: 收货单明细（新增）
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.mysql import TEXT
import enum

from app.core.database import Base


class SupplierStatus(str, enum.Enum):
    """供应商状态"""
    ACTIVE = "active"  # 正常
    INACTIVE = "inactive"  # 停用
    BLACKLIST = "blacklist"  # 黑名单


class Supplier(Base):
    """
    供应商表

    @description 存储供应商基本信息

    @attributes
    - id: 供应商ID
    - code: 供应商编码（唯一）
    - name: 供应商名称
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

    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True, comment="供应商编码")
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="供应商名称")
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
    payment_terms: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=30, comment="付款条件（天数）"
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
    status: Mapped[str] = mapped_column(
        SQLEnum(SupplierStatus),
        default=SupplierStatus.ACTIVE,
        nullable=False,
        comment="状态"
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="是否删除")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="更新时间")

    # 关系
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")
    receipt_orders = relationship("ReceiptOrder", back_populates="supplier")


class PurchaseRequestStatus(str, enum.Enum):
    """采购申请状态"""
    DRAFT = "draft"  # 草稿
    PENDING = "pending"  # 待审批
    APPROVED = "approved"  # 已批准
    REJECTED = "rejected"  # 已拒绝
    CONVERTED = "converted"  # 已转订单


class PurchaseRequest(Base):
    """
    采购申请表

    @description 采购申请单主表

    @attributes
    - id: 申请ID
    - request_no: 申请单号（唯一）
    - title: 申请标题
    - request_date: 需求日期
    - applicant_id: 申请人ID
    - department_id: 申请部门ID
    - total_amount: 总金额
    - reason: 申请原因
    - status: 状态
    - workflow_instance_id: 审批流程实例ID
    - is_deleted: 是否删除
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "purchase_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_no: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True, comment="申请单号"
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="申请标题")
    request_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="需求日期"
    )
    applicant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, comment="申请人ID"
    )
    department_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("departments.id"), comment="申请部门ID"
    )
    total_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, default=0, comment="总金额"
    )
    reason: Mapped[Optional[str]] = mapped_column(Text, comment="申请原因")
    status: Mapped[str] = mapped_column(
        SQLEnum(PurchaseRequestStatus),
        default=PurchaseRequestStatus.DRAFT,
        nullable=False,
        comment="状态"
    )
    workflow_instance_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("workflow_instances.id"), comment="审批流程实例ID"
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="是否删除")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="更新时间")

    # 关系
    items = relationship("PurchaseRequestItem", back_populates="request", cascade="all, delete-orphan")


class PurchaseRequestItem(Base):
    """
    采购申请明细表

    @description 采购申请的明细项

    @attributes
    - id: 明细ID
    - request_id: 申请ID
    - product_code: 产品编码
    - product_name: 产品名称
    - specification: 规格型号
    - unit: 单位
    - quantity: 数量
    - estimated_price: 预估单价
    - estimated_amount: 预估金额
    - notes: 备注
    """

    __tablename__ = "purchase_request_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("purchase_requests.id"), nullable=False, comment="申请ID"
    )
    product_code: Mapped[Optional[str]] = mapped_column(String(50), comment="产品编码")
    product_name: Mapped[str] = mapped_column(String(200), nullable=False, comment="产品名称")
    specification: Mapped[Optional[str]] = mapped_column(String(100), comment="规格型号")
    unit: Mapped[Optional[str]] = mapped_column(String(20), comment="单位")
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, comment="数量"
    )
    estimated_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, comment="预估单价"
    )
    estimated_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, comment="预估金额"
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")

    # 关系
    request = relationship("PurchaseRequest", back_populates="items")


class PurchaseOrderStatus(str, enum.Enum):
    """采购订单状态"""
    DRAFT = "draft"  # 草稿
    PENDING = "pending"  # 待审核
    CONFIRMED = "confirmed"  # 已确认
    PARTIAL_RECEIVED = "partial_received"  # 部分收货
    RECEIVED = "received"  # 已收货
    CANCELLED = "cancelled"  # 已取消
    CLOSED = "closed"  # 已关闭


class PurchaseOrder(Base):
    """
    采购订单表

    @description 采购订单主表

    @attributes
    - id: 订单ID
    - order_no: 订单号（唯一）
    - request_id: 采购申请ID（可选）
    - supplier_id: 供应商ID
    - order_date: 订单日期
    - expected_date: 预计到货日期
    - total_amount: 总金额
    - tax_amount: 税额
    - tax_inclusive: 是否含税
    - payment_terms: 付款条件
    - delivery_address: 送货地址
    - contact: 联系人
    - contact_phone: 联系电话
    - notes: 备注
    - status: 状态
    - is_deleted: 是否删除
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "purchase_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_no: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True, comment="订单号"
    )
    request_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("purchase_requests.id"), comment="采购申请ID"
    )
    supplier_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("suppliers.id"), nullable=False, comment="供应商ID"
    )
    order_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="订单日期"
    )
    expected_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="预计到货日期"
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
    payment_terms: Mapped[Optional[int]] = mapped_column(
        Integer, comment="付款条件（天数）"
    )
    delivery_address: Mapped[Optional[str]] = mapped_column(Text, comment="送货地址")
    contact: Mapped[Optional[str]] = mapped_column(String(100), comment="联系人")
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50), comment="联系电话")
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
    status: Mapped[str] = mapped_column(
        SQLEnum(PurchaseOrderStatus),
        default=PurchaseOrderStatus.DRAFT,
        nullable=False,
        comment="状态"
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="是否删除")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="更新时间")

    # 关系
    supplier = relationship("Supplier", back_populates="purchase_orders")
    items = relationship("PurchaseOrderItem", back_populates="order", cascade="all, delete-orphan")
    receipt_orders = relationship("ReceiptOrder", back_populates="purchase_order")


class PurchaseOrderItem(Base):
    """
    采购订单明细表

    @description 采购订单的明细项

    @attributes
    - id: 明细ID
    - order_id: 订单ID
    - product_code: 产品编码
    - product_name: 产品名称
    - specification: 规格型号
    - unit: 单位
    - quantity: 数量
    - received_quantity: 已收货数量
    - unit_price: 单价
    - amount: 金额
    - tax_rate: 税率
    - notes: 备注
    """

    __tablename__ = "purchase_order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("purchase_orders.id"), nullable=False, comment="订单ID"
    )
    product_code: Mapped[Optional[str]] = mapped_column(String(50), comment="产品编码")
    product_name: Mapped[str] = mapped_column(String(200), nullable=False, comment="产品名称")
    specification: Mapped[Optional[str]] = mapped_column(String(100), comment="规格型号")
    unit: Mapped[Optional[str]] = mapped_column(String(20), comment="单位")
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, comment="数量"
    )
    received_quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=True, default=0, comment="已收货数量"
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
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")

    # 关系
    order = relationship("PurchaseOrder", back_populates="items")


class ReceiptOrderStatus(str, enum.Enum):
    """收货单状态"""
    DRAFT = "draft"  # 草稿
    PENDING = "pending"  # 待收货
    RECEIVED = "received"  # 已收货
    PARTIAL_INSPECTED = "partial_inspected"  # 部分质检
    INSPECTED = "inspected"  # 已质检
    PARTIAL_STOCKED = "partial_stocked"  # 部分入库
    STOCKED = "stocked"  # 已入库
    CANCELLED = "cancelled"  # 已取消
    RETURNED = "returned"  # 已退货


class ReceiptOrder(Base):
    """
    收货单表

    @description 采购收货单，用于跟踪收货和质检信息

    @attributes
    - id: 收货单ID
    - receipt_no: 收货单号（唯一）
    - order_id: 采购订单ID
    - supplier_id: 供应商ID
    - receipt_date: 收货日期
    - warehouse_id: 入库仓库ID
    - total_amount: 总金额
    - total_quantity: 总数量
    - inspection_status: 质检状态
    - inspection_result: 质检结果
    - qualified_quantity: 合格数量
    - rejected_quantity: 不合格数量
    - notes: 备注
    - status: 状态
    - received_at: 收货时间
    - inspected_at: 质检时间
    - stocked_at: 入库时间
    - is_deleted: 是否删除
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "receipt_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    receipt_no: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True, comment="收货单号"
    )
    order_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("purchase_orders.id"), comment="采购订单ID"
    )
    supplier_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("suppliers.id"), nullable=False, comment="供应商ID"
    )
    receipt_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="收货日期"
    )
    warehouse_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("warehouses.id"), comment="入库仓库ID"
    )
    total_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, default=0, comment="总金额"
    )
    total_quantity: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, default=0, comment="总数量"
    )

    # 质检信息
    inspection_status: Mapped[Optional[str]] = mapped_column(
        String(20), comment="质检状态（pending/partial/complete）"
    )
    inspection_result: Mapped[Optional[str]] = mapped_column(
        String(20), comment="质检结果（qualified/conditional/rejected）"
    )
    qualified_quantity: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, default=0, comment="合格数量"
    )
    rejected_quantity: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, default=0, comment="不合格数量"
    )

    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
    status: Mapped[str] = mapped_column(
        SQLEnum(ReceiptOrderStatus),
        default=ReceiptOrderStatus.DRAFT,
        nullable=False,
        comment="状态"
    )

    # 时间戳
    received_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="收货时间"
    )
    inspected_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="质检时间"
    )
    stocked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="入库时间"
    )

    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="是否删除")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="更新时间")

    # 关系
    supplier = relationship("Supplier", back_populates="receipt_orders")
    purchase_order = relationship("PurchaseOrder", back_populates="receipt_orders", foreign_keys=[order_id])
    items = relationship("ReceiptOrderItem", back_populates="receipt_order", cascade="all, delete-orphan")


class ReceiptOrderItem(Base):
    """
    收货单明细表

    @description 收货单的明细项

    @attributes
    - id: 明细ID
    - receipt_id: 收货单ID
    - order_item_id: 采购订单明细ID
    - product_id: 产品ID
    - product_code: 产品编码
    - product_name: 产品名称
    - specification: 规格型号
    - unit: 单位
    - quantity: 收货数量
    - unit_price: 单价
    - amount: 金额
    - qualified_quantity: 合格数量
    - rejected_quantity: 不合格数量
    - batch_no: 批号
    - production_date: 生产日期
    - expiry_date: 有效期
    - notes: 备注
    """

    __tablename__ = "receipt_order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    receipt_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("receipt_orders.id"), nullable=False, comment="收货单ID"
    )
    order_item_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("purchase_order_items.id"), comment="采购订单明细ID"
    )
    product_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("products.id"), comment="产品ID"
    )
    product_code: Mapped[Optional[str]] = mapped_column(String(50), comment="产品编码")
    product_name: Mapped[str] = mapped_column(String(200), nullable=False, comment="产品名称")
    specification: Mapped[Optional[str]] = mapped_column(String(100), comment="规格型号")
    unit: Mapped[Optional[str]] = mapped_column(String(20), comment="单位")
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, comment="收货数量"
    )
    unit_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, comment="单价"
    )
    amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, comment="金额"
    )
    qualified_quantity: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, default=0, comment="合格数量"
    )
    rejected_quantity: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, default=0, comment="不合格数量"
    )
    batch_no: Mapped[Optional[str]] = mapped_column(
        String(50), comment="批号"
    )
    production_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="生产日期"
    )
    expiry_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="有效期"
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")

    # 关系
    receipt_order = relationship("ReceiptOrder", back_populates="items")
