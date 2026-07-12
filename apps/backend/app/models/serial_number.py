"""
序列号管理数据模型

@description 产品序列号管理，用于唯一标识和追溯

@models
- ProductSerialNumber: 产品序列号表
- SerialNumberTransaction: 序列号流水表
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class SerialNumberStatus(str, enum.Enum):
    """序列号状态"""
    IN_STOCK = "in_stock"  # 在库
    ALLOCATED = "allocated"  # 已分配
    SOLD = "sold"  # 已售出
    RETURNED = "returned"  # 已退货
    WARRANTY = "warranty"  # 保修中
    SCRAPPED = "scrapped"  # 已报废


class ProductSerialNumber(Base):
    """
    产品序列号表

    @description 存储产品序列号信息，用于唯一标识和质量追溯

    @attributes
    - id: 序列号ID
    - serial_number: 序列号（唯一）
    - product_id: 产品ID
    - warehouse_id: 仓库ID
    - batch_id: 批次ID（可选）
    - production_date: 生产日期
    - warranty_expiry: 保修到期日期
    - cost_price: 成本价
    - supplier_id: 供应商ID（可选）
    - receipt_id: 收货单ID（可选）
    - status: 状态
    - customer_id: 客户ID（售出后）
    - sale_date: 销售日期
    - warranty_notes: 保修备注
    - notes: 备注
    - is_deleted: 是否删除
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "product_serial_numbers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    serial_number: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True, comment="序列号"
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False, index=True, comment="产品ID"
    )
    warehouse_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("warehouses.id"), nullable=False, index=True, comment="仓库ID"
    )
    batch_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("inventory_batches.id"), comment="批次ID"
    )
    production_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="生产日期"
    )
    warranty_expiry: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="保修到期日期"
    )
    cost_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, comment="成本价"
    )
    supplier_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("suppliers.id"), comment="供应商ID"
    )
    receipt_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("receipt_orders.id"), comment="收货单ID"
    )
    status: Mapped[str] = mapped_column(
        SQLEnum(SerialNumberStatus),
        default=SerialNumberStatus.IN_STOCK,
        nullable=False,
        comment="状态"
    )
    customer_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("customers.id"), comment="客户ID（售出后）"
    )
    sale_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="销售日期"
    )
    warranty_notes: Mapped[Optional[str]] = mapped_column(Text, comment="保修备注")
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="是否删除")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="更新时间")

    # 关系
    transactions = relationship("SerialNumberTransaction", back_populates="serial_number", cascade="all, delete-orphan")


class SerialNumberTransaction(Base):
    """
    序列号流水表

    @description 记录序列号状态变更历史

    @attributes
    - id: 流水ID
    - serial_number_id: 序列号ID
    - transaction_type: 流水类型
    - from_status: 变更前状态
    - to_status: 变更后状态
    - reference_type: 关联单据类型
    - reference_id: 关联单据ID
    - reference_no: 关联单据号
    - customer_id: 客户ID（销售时）
    - notes: 备注
    - created_by: 创建人ID
    - created_at: 创建时间
    """

    __tablename__ = "serial_number_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    serial_number_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("product_serial_numbers.id"), nullable=False, index=True, comment="序列号ID"
    )
    transaction_type: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="流水类型"
    )
    from_status: Mapped[Optional[str]] = mapped_column(
        String(50), comment="变更前状态"
    )
    to_status: Mapped[Optional[str]] = mapped_column(
        String(50), comment="变更后状态"
    )
    reference_type: Mapped[Optional[str]] = mapped_column(
        String(50), comment="关联单据类型"
    )
    reference_id: Mapped[Optional[int]] = mapped_column(
        Integer, comment="关联单据ID"
    )
    reference_no: Mapped[Optional[str]] = mapped_column(
        String(50), comment="关联单据号"
    )
    customer_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("customers.id"), comment="客户ID"
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
    created_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), comment="创建人ID"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="创建时间")

    # 关系
    serial_number = relationship("ProductSerialNumber", back_populates="transactions")
