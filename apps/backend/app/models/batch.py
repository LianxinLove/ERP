"""
批号管理数据模型

@description 批号追踪和有效期管理

@models
- InventoryBatch: 库存批号表
- BatchTransaction: 批号流水表
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class BatchStatus(str, enum.Enum):
    """批号状态"""
    ACTIVE = "active"  # 正常
    EXPIRED = "expired"  # 已过期
    QUARANTINE = "quarantine"  # 检疫中
    REJECTED = "rejected"  # 已拒收
    CONSUMED = "consumed"  # 已消耗
    WRITE_OFF = "write_off"  # 已核销


class InventoryBatch(Base):
    """
    库存批号表

    @description 存储产品批号信息，用于质量追溯和有效期管理

    @attributes
    - id: 批次ID
    - batch_no: 批号（唯一）
    - product_id: 产品ID
    - warehouse_id: 仓库ID
    - quantity: 数量
    - production_date: 生产日期
    - expiry_date: 有效期
    - supplier_id: 供应商ID（可选）
    - receipt_id: 收货单ID（可选）
    - cost_price: 成本价
    - status: 状态
    - notes: 备注
    - is_deleted: 是否删除
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "inventory_batches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    batch_no: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True, comment="批号"
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False, index=True, comment="产品ID"
    )
    warehouse_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("warehouses.id"), nullable=False, index=True, comment="仓库ID"
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, default=0, comment="数量"
    )
    available_quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, default=0, comment="可用数量"
    )
    production_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="生产日期"
    )
    expiry_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="有效期"
    )
    supplier_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("suppliers.id"), comment="供应商ID"
    )
    receipt_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("receipt_orders.id"), comment="收货单ID"
    )
    cost_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, comment="成本价"
    )
    status: Mapped[str] = mapped_column(
        SQLEnum(BatchStatus),
        default=BatchStatus.ACTIVE,
        nullable=False,
        comment="状态"
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="是否删除")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="更新时间")

    # 关系
    transactions = relationship("BatchTransaction", back_populates="batch", cascade="all, delete-orphan")


class BatchTransaction(Base):
    """
    批号流水表

    @description 记录批号库存变动历史

    @attributes
    - id: 流水ID
    - batch_id: 批次ID
    - transaction_type: 流水类型
    - quantity: 数量
    - before_quantity: 变动前数量
    - after_quantity: 变动后数量
    - reference_type: 关联单据类型
    - reference_id: 关联单据ID
    - reference_no: 关联单据号
    - notes: 备注
    - created_by: 创建人ID
    - created_at: 创建时间
    """

    __tablename__ = "batch_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    batch_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("inventory_batches.id"), nullable=False, index=True, comment="批次ID"
    )
    transaction_type: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="流水类型"
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, comment="数量（正负）"
    )
    before_quantity: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, comment="变动前数量"
    )
    after_quantity: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, comment="变动后数量"
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
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
    created_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), comment="创建人ID"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="创建时间")

    # 关系
    batch = relationship("InventoryBatch", back_populates="transactions")
