"""
价格管理数据模型

@description 销售价格管理，支持价格表、折扣政策、阶梯定价等

@models
- PriceList: 价格表
- PriceListLine: 价格表明细
- CustomerPrice: 客户专属价格
- DiscountPolicy: 折扣政策
- ProductPriceHistory: 产品价格历史
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class PriceListStatus(str, enum.Enum):
    """价格表状态"""
    DRAFT = "draft"  # 草稿
    ACTIVE = "active"  # 生效
    EXPIRED = "expired"  # 已过期
    CANCELLED = "cancelled"  # 已取消


class PriceList(Base):
    """
    价格表

    @description 产品价格表，支持按客户、按数量、按时间定价

    @attributes
    - id: 价格表ID
    - name: 价格表名称
    - code: 价格表编码
    - description: 描述
    - type: 类型（standard/special/promotion）
    - customer_id: 适用客户ID（null表示所有客户）
    - customer_group: 客户分组
    - valid_from: 生效日期
    - valid_until: 失效日期
    - currency: 币种
    - status: 状态
    - is_default: 是否默认价格表
    - priority: 优先级（数值越大优先级越高）
    - notes: 备注
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "price_lists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="价格表名称")
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="价格表编码")
    description: Mapped[Optional[str]] = mapped_column(Text, comment="描述")
    type: Mapped[str] = mapped_column(
        String(20), default="standard", nullable=False, comment="类型"
    )
    customer_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("customers.id"), comment="适用客户ID"
    )
    customer_group: Mapped[Optional[str]] = mapped_column(
        String(50), comment="客户分组"
    )
    valid_from: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="生效日期"
    )
    valid_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="失效日期"
    )
    currency: Mapped[str] = mapped_column(
        String(10), default="CNY", nullable=False, comment="币种"
    )
    status: Mapped[str] = mapped_column(
        SQLEnum(PriceListStatus),
        default=PriceListStatus.DRAFT,
        nullable=False,
        comment="状态"
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="是否默认"
    )
    priority: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="优先级"
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="更新时间"
    )

    # 关系
    lines = relationship("PriceListLine", back_populates="price_list", cascade="all, delete-orphan")


class PriceListLine(Base):
    """
    价格表明细

    @description 价格表的产品明细

    @attributes
    - id: 明细ID
    - price_list_id: 价格表ID
    - product_id: 产品ID
    - product_code: 产品编码
    - product_name: 产品名称
    - unit_price: 单价
    - currency: 币种
    - min_quantity: 最小数量（阶梯定价用）
    - max_quantity: 最大数量（阶梯定价用）
    - discount_rate: 折扣率（%）
    - valid_from: 生效日期
    - valid_until: 失效日期
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "price_list_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    price_list_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("price_lists.id"), nullable=False, comment="价格表ID"
    )
    product_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("products.id"), comment="产品ID"
    )
    product_code: Mapped[Optional[str]] = mapped_column(
        String(50), comment="产品编码"
    )
    product_name: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="产品名称"
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, comment="单价"
    )
    currency: Mapped[str] = mapped_column(
        String(10), default="CNY", nullable=False, comment="币种"
    )
    min_quantity: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, comment="最小数量"
    )
    max_quantity: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, comment="最大数量"
    )
    discount_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2), nullable=True, comment="折扣率(%)"
    )
    valid_from: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="生效日期"
    )
    valid_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="失效日期"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="更新时间"
    )

    # 关系
    price_list = relationship("PriceList", back_populates="lines")


class CustomerPrice(Base):
    """
    客户专属价格

    @description 特定客户的专属价格（优先级最高）

    @attributes
    - id: ID
    - customer_id: 客户ID
    - product_id: 产品ID
    - unit_price: 单价
    - currency: 币种
    - min_quantity: 最小数量
    - max_quantity: 最大数量
    - valid_from: 生效日期
    - valid_until: 失效日期
    - notes: 备注
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "customer_prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("customers.id"), nullable=False, comment="客户ID"
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False, comment="产品ID"
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, comment="单价"
    )
    currency: Mapped[str] = mapped_column(
        String(10), default="CNY", nullable=False, comment="币种"
    )
    min_quantity: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, comment="最小数量"
    )
    max_quantity: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, comment="最大数量"
    )
    valid_from: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="生效日期"
    )
    valid_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="失效日期"
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="更新时间"
    )


class DiscountPolicy(Base):
    """
    折扣政策

    @description 折扣政策规则

    @attributes
    - id: 政策ID
    - name: 政策名称
    - code: 政策编码
    - type: 类型（percentage/fixed/阶梯）
    - discount_value: 折扣值
    - min_amount: 最小金额
    - customer_id: 适用客户
    - customer_group: 客户分组
    - product_category: 产品分类
    - valid_from: 生效日期
    - valid_until: 失效日期
    - is_active: 是否启用
    - notes: 备注
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "discount_policies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="政策名称")
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="政策编码")
    type: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="类型"
    )
    discount_value: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, comment="折扣值"
    )
    min_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, comment="最小金额"
    )
    customer_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("customers.id"), comment="适用客户"
    )
    customer_group: Mapped[Optional[str]] = mapped_column(
        String(50), comment="客户分组"
    )
    product_category: Mapped[Optional[str]] = mapped_column(
        String(100), comment="产品分类"
    )
    valid_from: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="生效日期"
    )
    valid_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="失效日期"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, comment="是否启用"
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="更新时间"
    )


class ProductPriceHistory(Base):
    """
    产品价格历史

    @description 记录产品价格变更历史

    @attributes
    - id: ID
    - product_id: 产品ID
    - old_price: 旧价格
    - new_price: 新价格
    - change_reason: 变更原因
    - changed_by: 变更人
    - changed_at: 变更时间
    """

    __tablename__ = "product_price_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False, comment="产品ID"
    )
    old_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, comment="旧价格"
    )
    new_price: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, comment="新价格"
    )
    change_reason: Mapped[Optional[str]] = mapped_column(
        String(200), comment="变更原因"
    )
    changed_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), comment="变更人"
    )
    changed_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="变更时间"
    )
