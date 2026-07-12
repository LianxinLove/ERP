"""
生产制造数据模型

@description 生产制造模块，包含BOM、生产订单、车间管理等

@models
- BOM: 物料清单主表
- BOMItem: BOM明细表
- BOMVersion: BOM版本管理
- ProductionOrder: 生产订单
- ProductionOrderItem: 生产订单明细
- ProductionProcess: 生产工序
- Routing: 工艺路线
- WorkOrder: 派工单
- WorkReport: 报工单
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class BOMStatus(str, enum.Enum):
    """BOM状态"""
    DRAFT = "draft"  # 草稿
    ACTIVE = "active"  # 生效
    EXPIRED = "expired"  # 过期
    ARCHIVED = "archived"  # 归档


class BOMItemType(str, enum.Enum):
    """BOM明细类型"""
    MATERIAL = "material"  # 材料
    SEMI_FINISHED = "semi_finished"  # 半成品
    SUBCONTRACTING = "subcontracting"  # 外协
    BY_PRODUCT = "by_product"  # 联产品
    WASTE = "waste"  # 废料


class ProductionOrderStatus(str, enum.Enum):
    """生产订单状态"""
    DRAFT = "draft"  # 草稿
    PENDING = "pending"  # 待审核
    CONFIRMED = "confirmed"  # 已确认
    RELEASED = "released"  # 已下达
    IN_PROGRESS = "in_progress"  # 生产中
    COMPLETED = "completed"  # 已完工
    CANCELLED = "cancelled"  # 已取消
    CLOSED = "closed"  # 已关闭


class WorkOrderStatus(str, enum.Enum):
    """派工单状态"""
    PENDING = "pending"  # 待派工
    ASSIGNED = "assigned"  # 已派工
    IN_PROGRESS = "in_progress"  # 加工中
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消


class BOM(Base):
    """
    物料清单表（Bill of Materials）

    @description 定义产品结构和物料配比

    @attributes
    - id: BOM ID
    - product_id: 产品ID
    - product_code: 产品编码
    - product_name: 产品名称
    - version: 版本号
    - description: 描述
    - base_quantity: 基准数量（父件数量）
    - unit: 单位
    - status: 状态
    - effective_date: 生效日期
    - expiry_date: 失效日期
    - cost_standard: 标准成本
    - notes: 备注
    - is_default: 是否默认
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "boms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # 产品信息
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False, unique=True, comment="产品ID"
    )
    product_code: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="产品编码"
    )
    product_name: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="产品名称"
    )
    version: Mapped[str] = mapped_column(
        String(20), default="1.0", nullable=False, comment="版本号"
    )

    # BOM信息
    description: Mapped[Optional[str]] = mapped_column(
        Text, comment="描述"
    )
    base_quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("1.00"), nullable=False, comment="基准数量"
    )
    unit: Mapped[Optional[str]] = mapped_column(
        String(20), comment="单位"
    )

    # 状态和日期
    status: Mapped[str] = mapped_column(
        SQLEnum(BOMStatus),
        default=BOMStatus.DRAFT,
        nullable=False,
        index=True,
        comment="状态"
    )
    effective_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="生效日期"
    )
    expiry_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="失效日期"
    )

    # 成本信息
    cost_standard: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 4), comment="标准成本"
    )
    cost_material: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 4), comment="材料成本"
    )
    cost_labor: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 4), comment="人工成本"
    )
    cost_overhead: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 4), comment="制造费用"
    )

    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")
    is_default: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="是否默认"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="更新时间"
    )

    # 关系
    items = relationship("BOMItem", back_populates="bom", cascade="all, delete-orphan")
    production_orders = relationship("ProductionOrder", back_populates="bom")


class BOMItem(Base):
    """
    BOM明细表

    @description BOM的子件明细

    @attributes
    - id: 明细ID
    - bom_id: BOM ID
    - line_no: 行号
    - component_id: 子件ID
    - component_code: 子件编码
    - component_name: 子件名称
    - item_type: 子件类型
    - quantity: 用量
    - unit: 单位
    - scrap_rate: 损耗率(%)
    - effective_date: 生效日期
    - expiry_date: 失效日期
    - substitute_for: 替代物料ID
    - is_optional: 是否可选
    - notes: 备注
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "bom_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    bom_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("boms.id"), nullable=False, comment="BOM ID"
    )
    line_no: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="行号"
    )

    # 子件信息
    component_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("products.id"), comment="子件ID"
    )
    component_code: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="子件编码"
    )
    component_name: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="子件名称"
    )
    item_type: Mapped[str] = mapped_column(
        SQLEnum(BOMItemType),
        default=BOMItemType.MATERIAL,
        nullable=False,
        comment="子件类型"
    )

    # 用量信息
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 4), nullable=False, comment="用量"
    )
    unit: Mapped[Optional[str]] = mapped_column(
        String(20), comment="单位"
    )
    scrap_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2), default=Decimal("0.00"), comment="损耗率(%)"
    )

    # 日期
    effective_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="生效日期"
    )
    expiry_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="失效日期"
    )

    # 替代和选项
    substitute_for: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("bom_items.id"), comment="替代物料ID"
    )
    is_optional: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="是否可选"
    )

    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="更新时间"
    )

    # 关系
    bom = relationship("BOM", back_populates="items")


class ProductionOrder(Base):
    """
    生产订单表

    @description 生产工单主表

    @attributes
    - id: 生产订单ID
    - order_no: 生产订单号（唯一）
    - bom_id: BOM ID
    - product_id: 产品ID
    - product_code: 产品编码
    - product_name: 产品名称
    - quantity: 数量
    - unit: 单位
    - plan_start_date: 计划开始日期
    - plan_end_date: 计划完成日期
    - actual_start_date: 实际开始日期
    - actual_end_date: 实际完成日期
    - warehouse_id: 生产仓库ID
    - sales_order_id: 关联销售订单ID
    - priority: 优先级
    - status: 状态
    - notes: 备注
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "production_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    order_no: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True, comment="生产订单号"
    )

    # BOM和产品信息
    bom_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("boms.id"), comment="BOM ID"
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False, comment="产品ID"
    )
    product_code: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="产品编码"
    )
    product_name: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="产品名称"
    )

    # 数量信息
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, comment="数量"
    )
    unit: Mapped[Optional[str]] = mapped_column(
        String(20), comment="单位"
    )
    completed_quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), nullable=False, comment="完工数量"
    )
    qualified_quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), nullable=False, comment="合格数量"
    )
    rejected_quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), nullable=False, comment="不合格数量"
    )

    # 计划日期
    plan_start_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="计划开始日期"
    )
    plan_end_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="计划完成日期"
    )
    actual_start_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="实际开始日期"
    )
    actual_end_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="实际完成日期"
    )

    # 仓库和关联
    warehouse_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("warehouses.id"), comment="生产仓库ID"
    )
    sales_order_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("sales_orders.id"), comment="关联销售订单ID"
    )

    # 优先级和状态
    priority: Mapped[int] = mapped_column(
        Integer, default=5, nullable=False, comment="优先级(1-10)"
    )
    status: Mapped[str] = mapped_column(
        SQLEnum(ProductionOrderStatus),
        default=ProductionOrderStatus.DRAFT,
        nullable=False,
        index=True,
        comment="状态"
    )

    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="更新时间"
    )

    # 关系
    bom = relationship("BOM", back_populates="production_orders")
    items = relationship("ProductionOrderItem", back_populates="production_order", cascade="all, delete-orphan")
    work_orders = relationship("WorkOrder", back_populates="production_order")


class ProductionOrderItem(Base):
    """
    生产订单明细表

    @description 生产订单的子件需求明细

    @attributes
    - id: 明细ID
    - order_id: 生产订单ID
    - component_id: 子件ID
    - component_code: 子件编码
    - component_name: 子件名称
    - required_quantity: 需求数量
    - issued_quantity: 已领数量
    - unit: 单位
    - notes: 备注
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "production_order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("production_orders.id"), nullable=False, comment="生产订单ID"
    )

    # 子件信息
    component_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("products.id"), comment="子件ID"
    )
    component_code: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="子件编码"
    )
    component_name: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="子件名称"
    )

    # 数量信息
    required_quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, comment="需求数量"
    )
    issued_quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), nullable=False, comment="已领数量"
    )
    unit: Mapped[Optional[str]] = mapped_column(
        String(20), comment="单位"
    )

    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="更新时间"
    )

    # 关系
    production_order = relationship("ProductionOrder", back_populates="items")


class ProductionProcess(Base):
    """
    生产工序表

    @description 生产工序定义

    @attributes
    - id: 工序ID
    - code: 工序编码
    - name: 工序名称
    - description: 描述
    - work_center_id: 工作中心ID
    - standard_hours: 标准工时
    - standard_labor: 标准人工
    - standard_machine: 标准机时
    - cost_per_hour: 每小时成本
    - is_active: 是否启用
    - sort_order: 排序
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "production_processes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="工序编码"
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="工序名称"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, comment="描述"
    )

    # 工作中心
    work_center_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("work_centers.id"), comment="工作中心ID"
    )

    # 标准信息
    standard_hours: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 4), comment="标准工时"
    )
    standard_labor: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 4), comment="标准人工"
    )
    standard_machine: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 4), comment="标准机时"
    )
    cost_per_hour: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 4), comment="每小时成本"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, comment="是否启用"
    )
    sort_order: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="排序"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="更新时间"
    )


class Routing(Base):
    """
    工艺路线表

    @description 产品生产工艺路线

    @attributes
    - id: 路线ID
    - product_id: 产品ID
    - code: 路线编码
    - name: 路线名称
    - version: 版本号
    - status: 状态
    - is_default: 是否默认
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "routings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False, comment="产品ID"
    )
    code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="路线编码"
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="路线名称"
    )
    version: Mapped[str] = mapped_column(
        String(20), default="1.0", nullable=False, comment="版本号"
    )
    status: Mapped[str] = mapped_column(
        String(20), default="draft", nullable=False, comment="状态"
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="是否默认"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="更新时间"
    )


class WorkOrder(Base):
    """
    派工单表

    @description 车间派工单

    @attributes
    - id: 派工单ID
    - work_no: 派工单号（唯一）
    - production_order_id: 生产订单ID
    - process_id: 工序ID
    - work_center_id: 工作中心ID
    - quantity: 数量
    - completed_quantity: 完工数量
    - qualified_quantity: 合格数量
    - rejected_quantity: 不合格数量
    - plan_start_time: 计划开始时间
    - plan_end_time: 计划结束时间
    - actual_start_time: 实际开始时间
    - actual_end_time: 实际结束时间
    - worker_id: 操作员ID
    - status: 状态
    - notes: 备注
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "work_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    work_no: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True, comment="派工单号"
    )

    production_order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("production_orders.id"), nullable=False, comment="生产订单ID"
    )
    process_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("production_processes.id"), nullable=False, comment="工序ID"
    )
    work_center_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("work_centers.id"), comment="工作中心ID"
    )

    # 数量
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, comment="数量"
    )
    completed_quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), nullable=False, comment="完工数量"
    )
    qualified_quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), nullable=False, comment="合格数量"
    )
    rejected_quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), nullable=False, comment="不合格数量"
    )

    # 时间
    plan_start_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="计划开始时间"
    )
    plan_end_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="计划结束时间"
    )
    actual_start_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="实际开始时间"
    )
    actual_end_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="实际结束时间"
    )

    # 操作员
    worker_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), comment="操作员ID"
    )

    status: Mapped[str] = mapped_column(
        SQLEnum(WorkOrderStatus),
        default=WorkOrderStatus.PENDING,
        nullable=False,
        index=True,
        comment="状态"
    )

    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="更新时间"
    )

    # 关系
    production_order = relationship("ProductionOrder", back_populates="work_orders")


class WorkReport(Base):
    """
    报工单表

    @description 生产报工记录

    @attributes
    - id: 报工单ID
    - work_order_id: 派工单ID
    - worker_id: 操作员ID
    - report_time: 报工时间
    - quantity: 数量
    - qualified_quantity: 合格数量
    - rejected_quantity: 不合格数量
    - work_hours: 工作时长
    - notes: 备注
    - created_at: 创建时间
    """

    __tablename__ = "work_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    work_order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("work_orders.id"), nullable=False, comment="派工单ID"
    )
    worker_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), comment="操作员ID"
    )
    report_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="报工时间"
    )

    # 数量
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, comment="数量"
    )
    qualified_quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, comment="合格数量"
    )
    rejected_quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), nullable=False, comment="不合格数量"
    )

    # 工时
    work_hours: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 4), comment="工作时长"
    )

    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )


class WorkCenter(Base):
    """
    工作中心表

    @description 生产工作中心

    @attributes
    - id: 工作中心ID
    - code: 工作中心编码
    - name: 工作中心名称
    - description: 描述
    - capacity: 产能
    - efficiency: 效率(%)
    - cost_per_hour: 每小时成本
    - is_active: 是否启用
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "work_centers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="工作中心编码"
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="工作中心名称"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, comment="描述"
    )

    capacity: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), comment="产能"
    )
    efficiency: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2), default=Decimal("100.00"), comment="效率(%)"
    )
    cost_per_hour: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 4), comment="每小时成本"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, comment="是否启用"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="更新时间"
    )
