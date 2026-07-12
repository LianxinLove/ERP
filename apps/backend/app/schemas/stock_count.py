"""
库存盘点 Pydantic Schemas

@description 盘点模块的请求/响应模型
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# ============ 盘点单明细相关 ============

class StockCountItemBase(BaseModel):
    """盘点单明细基础模型"""
    product_id: int = Field(..., description="产品ID")
    system_quantity: Decimal = Field(..., description="系统数量")
    counted_quantity: Decimal = Field(default=Decimal(0), description="实盘数量")
    location: Optional[str] = Field(None, max_length=100, description="存放位置")
    batch_no: Optional[str] = Field(None, max_length=50, description="批号")
    serial_number: Optional[str] = Field(None, max_length=100, description="序列号")
    notes: Optional[str] = Field(None, description="备注")


class StockCountItemCreate(StockCountItemBase):
    """创建盘点单明细"""
    pass


class StockCountItemUpdate(BaseModel):
    """更新盘点单明细"""
    counted_quantity: Decimal = Field(..., description="实盘数量")
    notes: Optional[str] = Field(None, description="备注")


class StockCountItemResponse(StockCountItemBase):
    """盘点单明细响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    difference_quantity: Decimal
    unit_cost: Optional[Decimal] = None
    difference_amount: Optional[Decimal] = None
    checked_at: Optional[datetime] = None
    checked_by: Optional[int] = None


# ============ 盘点单相关 ============

class StockCountBase(BaseModel):
    """盘点单基础模型"""
    warehouse_id: int = Field(..., description="仓库ID")
    count_date: datetime = Field(..., description="盘点日期")
    count_type: Optional[str] = Field("full", description="盘点类型")
    operator_id: Optional[int] = Field(None, description="盘点人ID")
    reviewer_id: Optional[int] = Field(None, description="复核人ID")
    notes: Optional[str] = Field(None, description="备注")


class StockCountCreate(StockCountBase):
    """创建盘点单"""
    items: List[StockCountItemCreate] = Field(..., description="明细列表")


class StockCountUpdate(BaseModel):
    """更新盘点单"""
    operator_id: Optional[int] = Field(None, description="盘点人ID")
    reviewer_id: Optional[int] = Field(None, description="复核人ID")
    notes: Optional[str] = Field(None, description="备注")
    status: Optional[str] = Field(None, description="状态")


class StockCountApprove(BaseModel):
    """审核盘点单"""
    approved: bool = Field(..., description="是否批准")
    notes: Optional[str] = Field(None, description="备注")


class StockCountComplete(BaseModel):
    """完成盘点"""
    auto_adjust: bool = Field(False, description="是否自动调整库存")
    notes: Optional[str] = Field(None, description="备注")


class StockCountResponse(StockCountBase):
    """盘点单响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    count_no: str
    total_items: Optional[int] = None
    total_quantity: Optional[Decimal] = None
    counted_quantity: Optional[Decimal] = None
    difference_quantity: Optional[Decimal] = None
    difference_amount: Optional[Decimal] = None
    status: str
    reviewed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class StockCountDetail(StockCountResponse):
    """盘点单详情"""
    items: List[StockCountItemResponse] = []


# ============ 盘点差异相关 ============

class StockCountDifferenceResponse(BaseModel):
    """盘点差异响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    count_id: int
    item_id: int
    product_id: int
    difference_quantity: Decimal
    difference_amount: Optional[Decimal] = None
    adjust_type: str
    status: str
    handled_by: Optional[int] = None
    handled_at: Optional[datetime] = None
    notes: Optional[str] = None


class DifferenceHandle(BaseModel):
    """差异处理"""
    approved: bool = Field(..., description="是否批准调整")
    notes: Optional[str] = Field(None, description="备注")


class StockCountSummary(BaseModel):
    """盘点汇总"""
    total_counts: int = Field(..., description="盘点单总数")
    in_progress_counts: int = Field(..., description="进行中盘点")
    completed_counts: int = Field(..., description="已完成盘点")
    total_difference_quantity: Decimal = Field(..., description="总差异数量")
    total_difference_amount: Decimal = Field(..., description="总差异金额")
    pending_differences: int = Field(..., description="待处理差异数")
