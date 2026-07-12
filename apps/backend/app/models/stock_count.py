"""
库存盘点数据模型

@description 库存盘点单和盘点差异管理

@models
- StockCount: 库存盘点单
- StockCountItem: 盘点单明细
- StockCountDifference: 盘点差异记录
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class StockCountStatus(str, enum.Enum):
    """盘点单状态"""
    DRAFT = "draft"  # 草稿
    PENDING = "pending"  # 待审核
    APPROVED = "approved"  # 已批准
    IN_PROGRESS = "in_progress"  # 盘点中
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消


class DifferenceStatus(str, enum.Enum):
    """差异状态"""
    PENDING = "pending"  # 待处理
    APPROVED = "approved"  # 已批准调整
    REJECTED = "rejected"  # 已拒绝
    AUTO_ADJUSTED = "auto_adjusted"  # 自动调整


class StockCount(Base):
    """
    库存盘点单表

    @description 库存盘点主单

    @attributes
    - id: 盘点单ID
    - count_no: 盘点单号（唯一）
    - warehouse_id: 仓库ID
    - count_date: 盘点日期
    - count_type: 盘点类型（全面/循环/抽样）
    - operator_id: 盘点人ID
    - reviewer_id: 复核人ID
    - total_items: 盘点品目数
    - total_quantity: 系统总数量
    - counted_quantity: 实盘总数量
    - difference_quantity: 差异数量
    - difference_amount: 差异金额
    - notes: 备注
    - status: 状态
    - reviewed_at: 复核时间
    - completed_at: 完成时间
    - is_deleted: 是否删除
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "stock_counts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    count_no: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True, comment="盘点单号"
    )
    warehouse_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("warehouses.id"), nullable=False, index=True, comment="仓库ID"
    )
    count_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="盘点日期"
    )
    count_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="full", comment="盘点类型"
    )
    operator_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), comment="盘点人ID"
    )
    reviewer_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), comment="复核人ID"
    )
    total_items: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=0, comment="盘点品目数"
    )
    total_quantity: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, default=0, comment="系统总数量"
    )
    counted_quantity: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, default=0, comment="实盘总数量"
    )
    difference_quantity: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, default=0, comment="差异数量"
    )
    difference_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, default=0, comment="差异金额"
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
    status: Mapped[str] = mapped_column(
        SQLEnum(StockCountStatus),
        default=StockCountStatus.DRAFT,
        nullable=False,
        comment="状态"
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="复核时间"
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="完成时间"
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="是否删除")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="更新时间")

    # 关系
    items = relationship("StockCountItem", back_populates="stock_count", cascade="all, delete-orphan")
    differences = relationship("StockCountDifference", back_populates="stock_count", cascade="all, delete-orphan")


class StockCountItem(Base):
    """
    盘点单明细表

    @description 盘点单的明细项

    @attributes
    - id: 明细ID
    - count_id: 盘点单ID
    - product_id: 产品ID
    - system_quantity: 系统数量
    - counted_quantity: 实盘数量
    - difference_quantity: 差异数量
    - unit_cost: 单位成本
    - difference_amount: 差异金额
    - location: 存放位置
    - batch_no: 批号
    - serial_number: 序列号
    - notes: 备注
    - checked_at: 核对时间
    - checked_by: 核对人ID
    """

    __tablename__ = "stock_count_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    count_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("stock_counts.id"), nullable=False, comment="盘点单ID"
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False, comment="产品ID"
    )
    system_quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, comment="系统数量"
    )
    counted_quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, default=0, comment="实盘数量"
    )
    difference_quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, default=0, comment="差异数量"
    )
    unit_cost: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, comment="单位成本"
    )
    difference_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, default=0, comment="差异金额"
    )
    location: Mapped[Optional[str]] = mapped_column(
        String(100), comment="存放位置"
    )
    batch_no: Mapped[Optional[str]] = mapped_column(
        String(50), comment="批号"
    )
    serial_number: Mapped[Optional[str]] = mapped_column(
        String(100), comment="序列号"
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
    checked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="核对时间"
    )
    checked_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), comment="核对人ID"
    )

    # 关系
    stock_count = relationship("StockCount", back_populates="items")


class StockCountDifference(Base):
    """
    盘点差异记录表

    @description 记录盘点差异的处理情况

    @attributes
    - id: 差异ID
    - count_id: 盘点单ID
    - item_id: 盘点明细ID
    - product_id: 产品ID
    - difference_quantity: 差异数量
    - difference_amount: 差异金额
    - adjust_type: 调整类型（盘盈/盘亏）
    - status: 处理状态
    - handled_by: 处理人ID
    - handled_at: 处理时间
    - notes: 备注
    """

    __tablename__ = "stock_count_differences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    count_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("stock_counts.id"), nullable=False, comment="盘点单ID"
    )
    item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("stock_count_items.id"), nullable=False, comment="盘点明细ID"
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False, comment="产品ID"
    )
    difference_quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, comment="差异数量"
    )
    difference_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, comment="差异金额"
    )
    adjust_type: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="调整类型（profit/loss）"
    )
    status: Mapped[str] = mapped_column(
        SQLEnum(DifferenceStatus),
        default=DifferenceStatus.PENDING,
        nullable=False,
        comment="处理状态"
    )
    handled_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), comment="处理人ID"
    )
    handled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="处理时间"
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")

    # 关系
    stock_count = relationship("StockCount", back_populates="differences")
