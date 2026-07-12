"""
库存管理数据模型

@description 库存模块相关的数据库模型

@models
- Warehouse: 仓库
- Product: 产品
- Inventory: 库存
- InventoryTransaction: 库存流水
- InventoryTransfer: 库存调拨
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class ProductStatus(str, enum.Enum):
    """产品状态"""
    ACTIVE = "active"  # 正常
    DISCONTINUED = "discontinued"  # 停产
    OBSOLETE = "obsolete"  # 淘汰


class Product(Base):
    """
    产品表

    @description 存储产品基本信息

    @attributes
    - id: 产品ID
    - code: 产品编码（唯一）
    - name: 产品名称
    - specification: 规格型号
    - unit: 单位
    - category: 分类
    - barcode: 条码
    - cost_price: 成本价
    - selling_price: 销售价
    - min_stock: 最小库存（预警）
    - max_stock: 最大库存
    - lead_time: 采购提前期（天）
    - notes: 备注
    - status: 状态
    - is_deleted: 是否删除
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True, comment="产品编码")
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="产品名称")
    specification: Mapped[Optional[str]] = mapped_column(String(100), comment="规格型号")
    unit: Mapped[Optional[str]] = mapped_column(String(20), comment="单位")
    category: Mapped[Optional[str]] = mapped_column(String(100), comment="分类")
    barcode: Mapped[Optional[str]] = mapped_column(String(50), comment="条码")
    cost_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, comment="成本价"
    )
    selling_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, comment="销售价"
    )
    min_stock: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, comment="最小库存"
    )
    max_stock: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, comment="最大库存"
    )
    lead_time: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="采购提前期（天）"
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
    status: Mapped[str] = mapped_column(
        SQLEnum(ProductStatus),
        default=ProductStatus.ACTIVE,
        nullable=False,
        comment="状态"
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="是否删除")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="更新时间")

    # 关系
    inventories = relationship("Inventory", back_populates="product")


class Warehouse(Base):
    """
    仓库表

    @description 存储仓库基本信息

    @attributes
    - id: 仓库ID
    - code: 仓库编码（唯一）
    - name: 仓库名称
    - address: 地址
    - manager_id: 负责人ID
    - contact: 联系电话
    - capacity: 容量
    - notes: 备注
    - is_deleted: 是否删除
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "warehouses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True, comment="仓库编码")
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="仓库名称")
    address: Mapped[Optional[str]] = mapped_column(Text, comment="地址")
    manager_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), comment="负责人ID"
    )
    contact: Mapped[Optional[str]] = mapped_column(String(50), comment="联系电话")
    capacity: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, comment="容量"
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="是否删除")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="更新时间")

    # 关系
    inventories = relationship("Inventory", back_populates="warehouse")


class Inventory(Base):
    """
    库存表

    @description 存储产品在各仓库的库存数量

    @attributes
    - id: 库存ID
    - warehouse_id: 仓库ID
    - product_id: 产品ID
    - quantity: 库存数量
    - allocated_quantity: 已分配数量
    - available_quantity: 可用数量
    - last_updated: 最后更新时间
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "inventories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    warehouse_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("warehouses.id"), nullable=False, index=True, comment="仓库ID"
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False, index=True, comment="产品ID"
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, default=0, comment="库存数量"
    )
    allocated_quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, default=0, comment="已分配数量"
    )
    available_quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, default=0, comment="可用数量"
    )
    last_updated: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="最后更新时间"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="更新时间")

    # 关系
    warehouse = relationship("Warehouse", back_populates="inventories")
    product = relationship("Product", back_populates="inventories")


class TransactionType(str, enum.Enum):
    """库存流水类型"""
    PURCHASE_IN = "purchase_in"  # 采购入库
    PURCHASE_RETURN = "purchase_return"  # 采购退货
    SALES_OUT = "sales_out"  # 销售出库
    SALES_RETURN = "sales_return"  # 销售退货
    TRANSFER_IN = "transfer_in"  # 调拨入库
    TRANSFER_OUT = "transfer_out"  # 调拨出库
    ADJUSTMENT_IN = "adjustment_in"  # 盘盈
    ADJUSTMENT_OUT = "adjustment_out"  # 盘亏
    OTHER_IN = "other_in"  # 其他入库
    OTHER_OUT = "other_out"  # 其他出库


class InventoryTransaction(Base):
    """
    库存流水表

    @description 记录所有库存变动历史

    @attributes
    - id: 流水ID
    - warehouse_id: 仓库ID
    - product_id: 产品ID
    - transaction_type: 流水类型
    - quantity: 数量（正数为入库，负数为出库）
    - before_quantity: 变动前数量
    - after_quantity: 变动后数量
    - reference_type: 关联单据类型
    - reference_id: 关联单据ID
    - reference_no: 关联单据号
    - notes: 备注
    - created_by: 创建人ID
    - created_at: 创建时间
    """

    __tablename__ = "inventory_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    warehouse_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("warehouses.id"), nullable=False, index=True, comment="仓库ID"
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False, index=True, comment="产品ID"
    )
    transaction_type: Mapped[str] = mapped_column(
        SQLEnum(TransactionType),
        nullable=False,
        comment="流水类型"
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


class TransferStatus(str, enum.Enum):
    """调拨状态"""
    DRAFT = "draft"  # 草稿
    PENDING = "pending"  # 待审核
    APPROVED = "approved"  # 已批准
    REJECTED = "rejected"  # 已拒绝
    IN_TRANSIT = "in_transit"  # 调拨中
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消


class InventoryTransfer(Base):
    """
    库存调拨表

    @description 仓库之间的库存调拨

    @attributes
    - id: 调拨ID
    - transfer_no: 调拨单号（唯一）
    - from_warehouse_id: 调出仓库ID
    - to_warehouse_id: 调入仓库ID
    - transfer_date: 调拨日期
    - notes: 备注
    - status: 状态
    - is_deleted: 是否删除
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "inventory_transfers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    transfer_no: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True, comment="调拨单号"
    )
    from_warehouse_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("warehouses.id"), nullable=False, comment="调出仓库ID"
    )
    to_warehouse_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("warehouses.id"), nullable=False, comment="调入仓库ID"
    )
    transfer_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="调拨日期"
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
    status: Mapped[str] = mapped_column(
        SQLEnum(TransferStatus),
        default=TransferStatus.DRAFT,
        nullable=False,
        comment="状态"
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="是否删除")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="更新时间")


class InventoryTransferItem(Base):
    """
    库存调拨明细表

    @description 库存调拨的明细项

    @attributes
    - id: 明细ID
    - transfer_id: 调拨ID
    - product_id: 产品ID
    - quantity: 数量
    - notes: 备注
    """

    __tablename__ = "inventory_transfer_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    transfer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("inventory_transfers.id"), nullable=False, comment="调拨ID"
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False, comment="产品ID"
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, comment="数量"
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
