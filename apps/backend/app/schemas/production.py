"""
生产制造模块的数据模式定义
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class BOMItemType(str, Enum):
    """BOM明细类型"""
    MATERIAL = "material"
    SEMI_FINISHED = "semi_finished"
    SUBCONTRACTING = "subcontracting"
    BY_PRODUCT = "by_product"
    WASTE = "waste"


class BOMStatus(str, Enum):
    """BOM状态"""
    DRAFT = "draft"
    ACTIVE = "active"
    EXPIRED = "expired"
    ARCHIVED = "archived"


class ProductionOrderStatus(str, Enum):
    """生产订单状态"""
    DRAFT = "draft"
    PENDING = "pending"
    CONFIRMED = "confirmed"
    RELEASED = "released"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    CLOSED = "closed"


class WorkOrderStatus(str, Enum):
    """派工单状态"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# ========== BOM相关 ==========

class BOMBase(BaseModel):
    """BOM基础信息"""
    product_id: int = Field(..., description="产品ID")
    product_code: str = Field(..., description="产品编码")
    product_name: str = Field(..., description="产品名称")
    version: str = Field(default="1.0", description="版本号")
    base_quantity: Decimal = Field(default=Decimal("1.00"), description="基准数量")
    unit: Optional[str] = Field(None, description="单位")
    description: Optional[str] = Field(None, description="描述")


class BOMCreate(BOMBase):
    """创建BOM请求"""
    pass


class BOMItemBase(BaseModel):
    """BOM明细基础信息"""
    line_no: int = Field(..., description="行号")
    component_code: str = Field(..., description="子件编码")
    component_name: str = Field(..., description="子件名称")
    quantity: Decimal = Field(..., description="用量")
    unit: Optional[str] = Field(None, description="单位")
    item_type: BOMItemType = Field(default=BOMItemType.MATERIAL, description="子件类型")
    scrap_rate: Optional[Decimal] = Field(None, description="损耗率(%)")


class BOMItemCreate(BOMItemBase):
    """创建BOM明细请求"""
    pass


class BOMItemResponse(BOMItemBase):
    """BOM明细响应"""
    id: int
    bom_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class BOMCostResponse(BaseModel):
    """BOM成本响应"""
    material_cost: Decimal = Field(..., description="材料成本")
    labor_cost: Decimal = Field(..., description="人工成本")
    overhead_cost: Decimal = Field(..., description="制造费用")
    total_cost: Decimal = Field(..., description="总成本")


class BOMResponse(BOMBase):
    """BOM响应"""
    id: int
    code: str
    status: BOMStatus
    cost_standard: Optional[Decimal] = None
    cost_material: Optional[Decimal] = None
    cost_labor: Optional[Decimal] = None
    cost_overhead: Optional[Decimal] = None
    effective_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    is_default: bool
    created_at: datetime
    updated_at: datetime
    items: list[BOMItemResponse] = []

    class Config:
        from_attributes = True


# ========== 生产订单相关 ==========

class ProductionOrderBase(BaseModel):
    """生产订单基础信息"""
    order_no: str = Field(..., description="生产订单号")
    product_id: int = Field(..., description="产品ID")
    product_code: str = Field(..., description="产品编码")
    product_name: str = Field(..., description="产品名称")
    quantity: Decimal = Field(..., description="数量")
    unit: Optional[str] = Field(None, description="单位")


class ProductionOrderCreate(ProductionOrderBase):
    """创建生产订单请求"""
    bom_id: Optional[int] = Field(None, description="BOM ID")
    plan_start_date: Optional[datetime] = Field(None, description="计划开始日期")
    plan_end_date: Optional[datetime] = Field(None, description="计划完成日期")
    warehouse_id: Optional[int] = Field(None, description="生产仓库ID")
    sales_order_id: Optional[int] = Field(None, description="关联销售订单ID")
    priority: int = Field(default=5, description="优先级(1-10)")
    notes: Optional[str] = Field(None, description="备注")


class ProductionOrderResponse(ProductionOrderBase):
    """生产订单响应"""
    id: int
    bom_id: Optional[int] = None
    completed_quantity: Decimal
    qualified_quantity: Decimal
    rejected_quantity: Decimal
    plan_start_date: Optional[datetime] = None
    plan_end_date: Optional[datetime] = None
    actual_start_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None
    warehouse_id: Optional[int] = None
    sales_order_id: Optional[int] = None
    priority: int
    status: ProductionOrderStatus
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== 派工单相关 ==========

class WorkOrderBase(BaseModel):
    """派工单基础信息"""
    work_no: str = Field(..., description="派工单号")
    production_order_id: int = Field(..., description="生产订单ID")
    process_id: int = Field(..., description="工序ID")
    quantity: Decimal = Field(..., description="数量")


class WorkOrderCreate(WorkOrderBase):
    """创建派工单请求"""
    work_center_id: Optional[int] = Field(None, description="工作中心ID")
    worker_id: Optional[int] = Field(None, description="操作员ID")
    plan_start_time: Optional[datetime] = Field(None, description="计划开始时间")
    plan_end_time: Optional[datetime] = Field(None, description="计划结束时间")


class WorkOrderResponse(WorkOrderBase):
    """派工单响应"""
    id: int
    work_center_id: Optional[int] = None
    completed_quantity: Decimal
    qualified_quantity: Decimal
    rejected_quantity: Decimal
    plan_start_time: Optional[datetime] = None
    plan_end_time: Optional[datetime] = None
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    worker_id: Optional[int] = None
    status: WorkOrderStatus
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== 工作中心相关 ==========

class WorkCenterBase(BaseModel):
    """工作中心基础信息"""
    code: str = Field(..., description="工作中心编码")
    name: str = Field(..., description="工作中心名称")


class WorkCenterCreate(WorkCenterBase):
    """创建工作中心请求"""
    capacity: Optional[Decimal] = Field(None, description="产能")
    efficiency: Decimal = Field(default=Decimal("100.00"), description="效率(%)")
    cost_per_hour: Optional[Decimal] = Field(None, description="每小时成本")
    description: Optional[str] = Field(None, description="描述")


class WorkCenterResponse(WorkCenterBase):
    """工作中心响应"""
    id: int
    capacity: Optional[Decimal] = None
    efficiency: Optional[Decimal] = None
    cost_per_hour: Optional[Decimal] = None
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
