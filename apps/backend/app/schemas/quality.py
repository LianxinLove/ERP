"""
质量管理模块的数据模式定义
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class InspectionType(str, Enum):
    """检验类型"""
    INCOMING = "incoming"
    PROCESS = "process"
    OUTGOING = "outgoing"


class InspectionMethod(str, Enum):
    """检验方法"""
    QUANTITATIVE = "quantitative"
    QUALITATIVE = "qualitative"
    VISUAL = "visual"
    MEASUREMENT = "measurement"
    TEST = "test"


class InspectionResult(str, Enum):
    """检验结果"""
    PENDING = "pending"
    QUALIFIED = "qualified"
    UNQUALIFIED = "unqualified"
    PARTIAL = "partial"


class InspectionStatus(str, Enum):
    """检验单状态"""
    DRAFT = "draft"
    PENDING = "pending"
    INSPECTING = "inspecting"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DefectLevel(str, Enum):
    """缺陷等级"""
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    NORMAL = "normal"


# ========== 质检方案相关 ==========

class InspectionSchemeBase(BaseModel):
    """质检方案基础信息"""
    code: str = Field(..., description="方案编码")
    name: str = Field(..., description="方案名称")
    inspection_type: InspectionType = Field(..., description="检验类型")


class InspectionSchemeCreate(InspectionSchemeBase):
    """创建质检方案请求"""
    sampling_plan_id: Optional[int] = Field(None, description="抽样方案ID")
    description: Optional[str] = Field(None, description="描述")


class InspectionSchemeResponse(InspectionSchemeBase):
    """质检方案响应"""
    id: int
    sampling_plan_id: Optional[int] = None
    description: Optional[str] = None
    is_default: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== 来料检验相关 ==========

class IncomingInspectionBase(BaseModel):
    """来料检验基础信息"""
    inspection_no: str = Field(..., description="检验单号")
    supplier_id: int = Field(..., description="供应商ID")
    product_id: int = Field(..., description="产品ID")
    quantity: Decimal = Field(..., description="数量")


class IncomingInspectionCreate(IncomingInspectionBase):
    """创建来料检验请求"""
    purchase_order_id: Optional[int] = Field(None, description="采购订单ID")
    receipt_id: Optional[int] = Field(None, description="收货单ID")
    batch_no: Optional[str] = Field(None, description="批号")


class IncomingInspectionResponse(IncomingInspectionBase):
    """来料检验响应"""
    id: int
    purchase_order_id: Optional[int] = None
    receipt_id: Optional[int] = None
    batch_no: Optional[str] = None
    sample_quantity: Optional[Decimal] = None
    qualified_quantity: Decimal
    rejected_quantity: Decimal
    inspection_result: InspectionResult
    status: InspectionStatus
    inspector_id: Optional[int] = None
    inspection_date: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InspectionResultBase(BaseModel):
    """检验结果基础信息"""
    item_id: Optional[int] = Field(None, description="检验项目ID")
    item_name: str = Field(..., description="项目名称")
    measured_value: Optional[str] = Field(None, description="测量值")
    is_qualified: bool = Field(default=True, description="是否合格")
    defect_level: Optional[DefectLevel] = Field(None, description="缺陷等级")


class InspectionResultCreate(InspectionResultBase):
    """添加检验结果请求"""
    notes: Optional[str] = Field(None, description="备注")


# ========== 过程检验相关 ==========

class ProcessInspectionBase(BaseModel):
    """过程检验基础信息"""
    inspection_no: str = Field(..., description="检验单号")
    product_id: int = Field(..., description="产品ID")
    quantity: Decimal = Field(..., description="数量")


class ProcessInspectionCreate(ProcessInspectionBase):
    """创建过程检验请求"""
    production_order_id: Optional[int] = Field(None, description="生产订单ID")
    work_order_id: Optional[int] = Field(None, description="派工单ID")
    process_id: Optional[int] = Field(None, description="工序ID")
    batch_no: Optional[str] = Field(None, description="批号")


class ProcessInspectionResponse(ProcessInspectionBase):
    """过程检验响应"""
    id: int
    production_order_id: Optional[int] = None
    work_order_id: Optional[int] = None
    process_id: Optional[int] = None
    batch_no: Optional[str] = None
    sample_quantity: Optional[Decimal] = None
    qualified_quantity: Decimal
    rejected_quantity: Decimal
    inspection_result: InspectionResult
    status: InspectionStatus
    inspector_id: Optional[int] = None
    inspection_date: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== 出货检验相关 ==========

class OutgoingInspectionBase(BaseModel):
    """出货检验基础信息"""
    inspection_no: str = Field(..., description="检验单号")
    customer_id: int = Field(..., description="客户ID")
    product_id: int = Field(..., description="产品ID")
    quantity: Decimal = Field(..., description="数量")


class OutgoingInspectionCreate(OutgoingInspectionBase):
    """创建出货检验请求"""
    delivery_order_id: Optional[int] = Field(None, description="发货单ID")
    sales_order_id: Optional[int] = Field(None, description="销售订单ID")
    batch_no: Optional[str] = Field(None, description="批号")


class OutgoingInspectionResponse(OutgoingInspectionBase):
    """出货检验响应"""
    id: int
    delivery_order_id: Optional[int] = None
    sales_order_id: Optional[int] = None
    batch_no: Optional[str] = None
    sample_quantity: Optional[Decimal] = None
    qualified_quantity: Decimal
    rejected_quantity: Decimal
    inspection_result: InspectionResult
    status: InspectionStatus
    inspector_id: Optional[int] = None
    inspection_date: Optional[datetime] = None
    certificate_no: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== 质量追溯相关 ==========

class QualityTraceBase(BaseModel):
    """质量追溯基础信息"""
    product_id: int = Field(..., description="产品ID")


class QualityTraceCreate(QualityTraceBase):
    """创建质量追溯请求"""
    batch_no: Optional[str] = Field(None, description="批号")
    serial_no: Optional[str] = Field(None, description="序列号")


class QualityTraceResponse(QualityTraceBase):
    """质量追溯响应"""
    id: int
    batch_no: Optional[str] = None
    serial_no: Optional[str] = None
    production_order_id: Optional[int] = None
    incoming_inspection_id: Optional[int] = None
    process_inspection_id: Optional[int] = None
    outgoing_inspection_id: Optional[int] = None
    supplier_id: Optional[int] = None
    quality_level: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
