"""
多单位换算数据模型

@description 产品多单位换算管理

@models
- ProductUnit: 产品单位表
- UnitConversion: 单位换算表
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey, Enum as SQLEnum, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class UnitType(str, enum.Enum):
    """单位类型"""
    BASE = "base"  # 基本单位
    PURCHASE = "purchase"  # 采购单位
    STOCK = "stock"  # 库存单位
    SALES = "sales"  # 销售单位


class ProductUnit(Base):
    """
    产品单位表

    @description 存储产品的计量单位信息

    @attributes
    - id: 单位ID
    - product_id: 产品ID
    - unit_code: 单位编码
    - unit_name: 单位名称
    - unit_type: 单位类型（基本/采购/库存/销售）
    - is_base: 是否为基本单位
    - conversion_rate: 换算率（相对于基本单位）
    - precision: 小数位数
    - notes: 备注
    - is_deleted: 是否删除
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "product_units"
    __table_args__ = (
        UniqueConstraint('product_id', 'unit_code', name='uq_product_unit_code'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False, index=True, comment="产品ID"
    )
    unit_code: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="单位编码"
    )
    unit_name: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="单位名称"
    )
    unit_type: Mapped[str] = mapped_column(
        SQLEnum(UnitType),
        default=UnitType.BASE,
        nullable=False,
        comment="单位类型"
    )
    is_base: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="是否为基本单位"
    )
    conversion_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 6), nullable=True, comment="换算率（相对于基本单位）"
    )
    precision: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=2, comment="小数位数"
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="是否删除")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="更新时间")

    # 关系
    conversions_from = relationship("UnitConversion", foreign_keys="UnitConversion.from_unit_id", back_populates="from_unit")
    conversions_to = relationship("UnitConversion", foreign_keys="UnitConversion.to_unit_id", back_populates="to_unit")


class UnitConversion(Base):
    """
    单位换算表

    @description 存储单位之间的换算关系

    @attributes
    - id: 换算ID
    - product_id: 产品ID
    - from_unit_id: 源单位ID
    - to_unit_id: 目标单位ID
    - conversion_rate: 换算率
    - is_direct: 是否为直接换算
    - notes: 备注
    - is_deleted: 是否删除
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "unit_conversions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False, index=True, comment="产品ID"
    )
    from_unit_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("product_units.id"), nullable=False, comment="源单位ID"
    )
    to_unit_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("product_units.id"), nullable=False, comment="目标单位ID"
    )
    conversion_rate: Mapped[Decimal] = mapped_column(
        Numeric(15, 6), nullable=False, comment="换算率"
    )
    is_direct: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, comment="是否为直接换算"
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="是否删除")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="更新时间")

    # 关系
    from_unit = relationship("ProductUnit", foreign_keys=[from_unit_id], back_populates="conversions_from")
    to_unit = relationship("ProductUnit", foreign_keys=[to_unit_id], back_populates="conversions_to")
