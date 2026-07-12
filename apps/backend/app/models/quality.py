"""
质量管理数据模型

@description 质量管理模块，包含质检方案、来料检验、过程检验、出货检验、质量追溯

@models
- InspectionScheme: 质检方案
- InspectionItem: 检验项目
- InspectionStandard: 检验标准
- SamplingPlan: 抽样方案
- IncomingInspection: 来料检验单
- IncomingInspectionItem: 来料检验明细
- ProcessInspection: 过程检验单
- ProcessInspectionItem: 过程检验明细
- OutgoingInspection: 出货检验单
- OutgoingInspectionItem: 出货检验明细
- QualityTrace: 质量追溯记录
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey, Enum as SQLEnum, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class InspectionType(str, enum.Enum):
    """检验类型"""
    INCOMING = "incoming"  # 来料检验
    PROCESS = "process"  # 过程检验
    OUTGOING = "outgoing"  # 出货检验


class InspectionMethod(str, enum.Enum):
    """检验方法"""
    QUANTITATIVE = "quantitative"  # 计量检验
    QUALITATIVE = "qualitative"  # 计数检验
    VISUAL = "visual"  # 目视检验
    MEASUREMENT = "measurement"  # 测量检验
    TEST = "test"  # 试验检验


class InspectionResult(str, enum.Enum):
    """检验结果"""
    PENDING = "pending"  # 待检验
    QUALIFIED = "qualified"  # 合格
    UNQUALIFIED = "unqualified"  # 不合格
    PARTIAL = "partial"  # 部分合格


class InspectionStatus(str, enum.Enum):
    """检验单状态"""
    DRAFT = "draft"  # 草稿
    PENDING = "pending"  # 待检验
    INSPECTING = "inspecting"  # 检验中
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消


class DefectLevel(str, enum.Enum):
    """缺陷等级"""
    CRITICAL = "critical"  # 致命
    MAJOR = "major"  # 严重
    MINOR = "minor"  # 轻微
    NORMAL = "normal"  # 正常


class InspectionScheme(Base):
    """
    质检方案表

    @description 质量检验方案定义

    @attributes
    - id: 方案ID
    - code: 方案编码
    - name: 方案名称
    - inspection_type: 检验类型
    - description: 描述
    - sampling_plan_id: 抽样方案ID
    - is_default: 是否默认方案
    - is_active: 是否启用
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "inspection_schemes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="方案编码"
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="方案名称"
    )
    inspection_type: Mapped[str] = mapped_column(
        SQLEnum(InspectionType),
        nullable=False,
        comment="检验类型"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, comment="描述"
    )
    sampling_plan_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("sampling_plans.id"), comment="抽样方案ID"
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="是否默认"
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

    # 关系
    items = relationship("InspectionItem", back_populates="scheme", cascade="all, delete-orphan")


class InspectionItem(Base):
    """
    检验项目表

    @description 检验项目定义

    @attributes
    - id: 项目ID
    - scheme_id: 方案ID
    - code: 项目编码
    - name: 项目名称
    - inspection_method: 检验方法
    - defect_level: 缺陷等级
    - description: 描述
    - sequence: 序号
    - is_required: 是否必检
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "inspection_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    scheme_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("inspection_schemes.id"), nullable=False, comment="方案ID"
    )
    code: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="项目编码"
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="项目名称"
    )
    inspection_method: Mapped[str] = mapped_column(
        SQLEnum(InspectionMethod),
        default=InspectionMethod.QUALITATIVE,
        nullable=False,
        comment="检验方法"
    )
    defect_level: Mapped[str] = mapped_column(
        SQLEnum(DefectLevel),
        default=DefectLevel.NORMAL,
        nullable=False,
        comment="缺陷等级"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, comment="描述"
    )
    sequence: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="序号"
    )
    is_required: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, comment="是否必检"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="更新时间"
    )

    # 关系
    scheme = relationship("InspectionScheme", back_populates="items")
    standards = relationship("InspectionStandard", back_populates="item", cascade="all, delete-orphan")


class InspectionStandard(Base):
    """
    检验标准表

    @description 检验项目的标准值

    @attributes
    - id: 标准ID
    - item_id: 项目ID
    - product_id: 产品ID
    - min_value: 最小值
    - max_value: 最大值
    - standard_value: 标准值
    - unit: 单位
    - tolerance: 公差
    - description: 描述
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "inspection_standards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("inspection_items.id"), nullable=False, comment="项目ID"
    )
    product_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("products.id"), comment="产品ID"
    )
    min_value: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 4), comment="最小值"
    )
    max_value: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 4), comment="最大值"
    )
    standard_value: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 4), comment="标准值"
    )
    unit: Mapped[Optional[str]] = mapped_column(
        String(20), comment="单位"
    )
    tolerance: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 4), comment="公差"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, comment="描述"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="更新时间"
    )

    # 关系
    item = relationship("InspectionItem", back_populates="standards")


class SamplingPlan(Base):
    """
    抽样方案表

    @description 抽样检验方案

    @attributes
    - id: 方案ID
    - code: 方案编码
    - name: 方案名称
    - plan_type: 方案类型
    - batch_size: 批量大小
    - sample_size: 样本量
    - accept_number: 接收数
    - reject_number: 拒收数
    - aql: AQL值
    - description: 描述
    - is_active: 是否启用
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "sampling_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="方案编码"
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="方案名称"
    )
    plan_type: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="方案类型"
    )
    batch_size: Mapped[Optional[int]] = mapped_column(
        Integer, comment="批量大小"
    )
    sample_size: Mapped[Optional[int]] = mapped_column(
        Integer, comment="样本量"
    )
    accept_number: Mapped[Optional[int]] = mapped_column(
        Integer, comment="接收数"
    )
    reject_number: Mapped[Optional[int]] = mapped_column(
        Integer, comment="拒收数"
    )
    aql: Mapped[Optional[str]] = mapped_column(
        String(20), comment="AQL值"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, comment="描述"
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


class IncomingInspection(Base):
    """
    来料检验单表

    @description 采购收货检验单

    @attributes
    - id: 检验单ID
    - inspection_no: 检验单号（唯一）
    - purchase_order_id: 采购订单ID
    - receipt_id: 收货单ID
    - supplier_id: 供应商ID
    - product_id: 产品ID
    - batch_no: 批号
    - quantity: 数量
    - sample_quantity: 抽样数量
    - qualified_quantity: 合格数量
    - rejected_quantity: 不合格数量
    - inspection_result: 检验结果
    - status: 状态
    - inspector_id: 检验员ID
    - inspection_date: 检验日期
    - notes: 备注
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "incoming_inspections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    inspection_no: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True, comment="检验单号"
    )

    # 关联信息
    purchase_order_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("purchase_orders.id"), comment="采购订单ID"
    )
    receipt_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("receipt_orders.id"), comment="收货单ID"
    )
    supplier_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("suppliers.id"), nullable=False, comment="供应商ID"
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False, comment="产品ID"
    )

    # 数量信息
    batch_no: Mapped[Optional[str]] = mapped_column(
        String(50), comment="批号"
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, comment="数量"
    )
    sample_quantity: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), comment="抽样数量"
    )
    qualified_quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), nullable=False, comment="合格数量"
    )
    rejected_quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), nullable=False, comment="不合格数量"
    )

    # 结果和状态
    inspection_result: Mapped[str] = mapped_column(
        SQLEnum(InspectionResult),
        default=InspectionResult.PENDING,
        nullable=False,
        comment="检验结果"
    )
    status: Mapped[str] = mapped_column(
        SQLEnum(InspectionStatus),
        default=InspectionStatus.DRAFT,
        nullable=False,
        index=True,
        comment="状态"
    )

    # 检验信息
    inspector_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), comment="检验员ID"
    )
    inspection_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="检验日期"
    )

    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="更新时间"
    )

    # 关系
    items = relationship("IncomingInspectionItem", back_populates="inspection", cascade="all, delete-orphan")


class IncomingInspectionItem(Base):
    """
    来料检验明细表

    @description 来料检验项目明细

    @attributes
    - id: 明细ID
    - inspection_id: 检验单ID
    - item_id: 检验项目ID
    - item_name: 项目名称
    - measured_value: 测量值
    - standard_value: 标准值
    - min_value: 最小值
    - max_value: 最大值
    - is_qualified: 是否合格
    - defect_level: 缺陷等级
    - notes: 备注
    - created_at: 创建时间
    """

    __tablename__ = "incoming_inspection_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    inspection_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("incoming_inspections.id"), nullable=False, comment="检验单ID"
    )
    item_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("inspection_items.id"), comment="检验项目ID"
    )
    item_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="项目名称"
    )
    measured_value: Mapped[Optional[str]] = mapped_column(
        String(100), comment="测量值"
    )
    standard_value: Mapped[Optional[str]] = mapped_column(
        String(100), comment="标准值"
    )
    min_value: Mapped[Optional[str]] = mapped_column(
        String(50), comment="最小值"
    )
    max_value: Mapped[Optional[str]] = mapped_column(
        String(50), comment="最大值"
    )
    is_qualified: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, comment="是否合格"
    )
    defect_level: Mapped[Optional[str]] = mapped_column(
        SQLEnum(DefectLevel),
        comment="缺陷等级"
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )

    # 关系
    inspection = relationship("IncomingInspection", back_populates="items")


class ProcessInspection(Base):
    """
    过程检验单表

    @description 生产过程检验单

    @attributes
    - id: 检验单ID
    - inspection_no: 检验单号（唯一）
    - production_order_id: 生产订单ID
    - work_order_id: 派工单ID
    - process_id: 工序ID
    - product_id: 产品ID
    - batch_no: 批号
    - quantity: 数量
    - sample_quantity: 抽样数量
    - qualified_quantity: 合格数量
    - rejected_quantity: 不合格数量
    - inspection_result: 检验结果
    - status: 状态
    - inspector_id: 检验员ID
    - inspection_date: 检验日期
    - notes: 备注
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "process_inspections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    inspection_no: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True, comment="检验单号"
    )

    # 关联信息
    production_order_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("production_orders.id"), comment="生产订单ID"
    )
    work_order_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("work_orders.id"), comment="派工单ID"
    )
    process_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("production_processes.id"), comment="工序ID"
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False, comment="产品ID"
    )

    # 数量信息
    batch_no: Mapped[Optional[str]] = mapped_column(
        String(50), comment="批号"
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, comment="数量"
    )
    sample_quantity: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), comment="抽样数量"
    )
    qualified_quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), nullable=False, comment="合格数量"
    )
    rejected_quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), nullable=False, comment="不合格数量"
    )

    # 结果和状态
    inspection_result: Mapped[str] = mapped_column(
        SQLEnum(InspectionResult),
        default=InspectionResult.PENDING,
        nullable=False,
        comment="检验结果"
    )
    status: Mapped[str] = mapped_column(
        SQLEnum(InspectionStatus),
        default=InspectionStatus.DRAFT,
        nullable=False,
        index=True,
        comment="状态"
    )

    # 检验信息
    inspector_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), comment="检验员ID"
    )
    inspection_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="检验日期"
    )

    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="更新时间"
    )

    # 关系
    items = relationship("ProcessInspectionItem", back_populates="inspection", cascade="all, delete-orphan")


class ProcessInspectionItem(Base):
    """
    过程检验明细表

    @description 过程检验项目明细

    @attributes
    - id: 明细ID
    - inspection_id: 检验单ID
    - item_id: 检验项目ID
    - item_name: 项目名称
    - measured_value: 测量值
    - standard_value: 标准值
    - is_qualified: 是否合格
    - defect_level: 缺陷等级
    - notes: 备注
    - created_at: 创建时间
    """

    __tablename__ = "process_inspection_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    inspection_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("process_inspections.id"), nullable=False, comment="检验单ID"
    )
    item_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("inspection_items.id"), comment="检验项目ID"
    )
    item_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="项目名称"
    )
    measured_value: Mapped[Optional[str]] = mapped_column(
        String(100), comment="测量值"
    )
    standard_value: Mapped[Optional[str]] = mapped_column(
        String(100), comment="标准值"
    )
    is_qualified: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, comment="是否合格"
    )
    defect_level: Mapped[Optional[str]] = mapped_column(
        SQLEnum(DefectLevel),
        comment="缺陷等级"
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )

    # 关系
    inspection = relationship("ProcessInspection", back_populates="items")


class OutgoingInspection(Base):
    """
    出货检验单表

    @description 成品出货检验单

    @attributes
    - id: 检验单ID
    - inspection_no: 检验单号（唯一）
    - delivery_order_id: 发货单ID
    - sales_order_id: 销售订单ID
    - customer_id: 客户ID
    - product_id: 产品ID
    - batch_no: 批号
    - quantity: 数量
    - sample_quantity: 抽样数量
    - qualified_quantity: 合格数量
    - rejected_quantity: 不合格数量
    - inspection_result: 检验结果
    - status: 状态
    - inspector_id: 检验员ID
    - inspection_date: 检验日期
    - certificate_no: 合格证编号
    - notes: 备注
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "outgoing_inspections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    inspection_no: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True, comment="检验单号"
    )

    # 关联信息
    delivery_order_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("delivery_orders.id"), comment="发货单ID"
    )
    sales_order_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("sales_orders.id"), comment="销售订单ID"
    )
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("customers.id"), nullable=False, comment="客户ID"
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False, comment="产品ID"
    )

    # 数量信息
    batch_no: Mapped[Optional[str]] = mapped_column(
        String(50), comment="批号"
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, comment="数量"
    )
    sample_quantity: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), comment="抽样数量"
    )
    qualified_quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), nullable=False, comment="合格数量"
    )
    rejected_quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), nullable=False, comment="不合格数量"
    )

    # 结果和状态
    inspection_result: Mapped[str] = mapped_column(
        SQLEnum(InspectionResult),
        default=InspectionResult.PENDING,
        nullable=False,
        comment="检验结果"
    )
    status: Mapped[str] = mapped_column(
        SQLEnum(InspectionStatus),
        default=InspectionStatus.DRAFT,
        nullable=False,
        index=True,
        comment="状态"
    )

    # 检验信息
    inspector_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), comment="检验员ID"
    )
    inspection_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="检验日期"
    )
    certificate_no: Mapped[Optional[str]] = mapped_column(
        String(50), comment="合格证编号"
    )

    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="更新时间"
    )

    # 关系
    items = relationship("OutgoingInspectionItem", back_populates="inspection", cascade="all, delete-orphan")


class OutgoingInspectionItem(Base):
    """
    出货检验明细表

    @description 出货检验项目明细

    @attributes
    - id: 明细ID
    - inspection_id: 检验单ID
    - item_id: 检验项目ID
    - item_name: 项目名称
    - measured_value: 测量值
    - standard_value: 标准值
    - is_qualified: 是否合格
    - defect_level: 缺陷等级
    - notes: 备注
    - created_at: 创建时间
    """

    __tablename__ = "outgoing_inspection_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    inspection_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("outgoing_inspections.id"), nullable=False, comment="检验单ID"
    )
    item_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("inspection_items.id"), comment="检验项目ID"
    )
    item_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="项目名称"
    )
    measured_value: Mapped[Optional[str]] = mapped_column(
        String(100), comment="测量值"
    )
    standard_value: Mapped[Optional[str]] = mapped_column(
        String(100), comment="标准值"
    )
    is_qualified: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, comment="是否合格"
    )
    defect_level: Mapped[Optional[str]] = mapped_column(
        SQLEnum(DefectLevel),
        comment="缺陷等级"
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, comment="备注")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )

    # 关系
    inspection = relationship("OutgoingInspection", back_populates="items")


class QualityTrace(Base):
    """
    质量追溯表

    @description 产品质量追溯记录

    @attributes
    - id: 追溯ID
    - product_id: 产品ID
    - batch_no: 批号
    - serial_no: 序列号
    - production_order_id: 生产订单ID
    - incoming_inspection_id: 来料检验ID
    - process_inspection_id: 过程检验ID
    - outgoing_inspection_id: 出货检验ID
    - supplier_id: 供应商ID
    - quality_level: 质量等级
    - trace_data: 追溯数据（JSON）
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "quality_traces"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False, index=True, comment="产品ID"
    )
    batch_no: Mapped[Optional[str]] = mapped_column(
        String(50), index=True, comment="批号"
    )
    serial_no: Mapped[Optional[str]] = mapped_column(
        String(50), index=True, comment="序列号"
    )

    # 关联检验单
    production_order_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("production_orders.id"), comment="生产订单ID"
    )
    incoming_inspection_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("incoming_inspections.id"), comment="来料检验ID"
    )
    process_inspection_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("process_inspections.id"), comment="过程检验ID"
    )
    outgoing_inspection_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("outgoing_inspections.id"), comment="出货检验ID"
    )
    supplier_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("suppliers.id"), comment="供应商ID"
    )

    quality_level: Mapped[Optional[str]] = mapped_column(
        String(20), comment="质量等级"
    )
    trace_data: Mapped[Optional[dict]] = mapped_column(
        JSON, comment="追溯数据（JSON）"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="更新时间"
    )
