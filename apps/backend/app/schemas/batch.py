"""
批号管理 Pydantic Schemas

@description 批号模块的请求/响应模型
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# ============ 库存批号相关 ============

class InventoryBatchBase(BaseModel):
    """库存批号基础模型"""
    batch_no: str = Field(..., max_length=50, description="批号")
    product_id: int = Field(..., description="产品ID")
    warehouse_id: int = Field(..., description="仓库ID")
    quantity: Decimal = Field(..., description="数量")
    production_date: Optional[datetime] = Field(None, description="生产日期")
    expiry_date: Optional[datetime] = Field(None, description="有效期")
    supplier_id: Optional[int] = Field(None, description="供应商ID")
    receipt_id: Optional[int] = Field(None, description="收货单ID")
    cost_price: Optional[Decimal] = Field(None, description="成本价")
    notes: Optional[str] = Field(None, description="备注")


class InventoryBatchCreate(InventoryBatchBase):
    """创建库存批号"""
    pass


class InventoryBatchUpdate(BaseModel):
    """更新库存批号"""
    quantity: Optional[Decimal] = Field(None, description="数量")
    cost_price: Optional[Decimal] = Field(None, description="成本价")
    notes: Optional[str] = Field(None, description="备注")
    status: Optional[str] = Field(None, description="状态")


class InventoryBatchResponse(InventoryBatchBase):
    """库存批号响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    available_quantity: Optional[Decimal] = None
    status: str
    created_at: datetime
    updated_at: datetime


class InventoryBatchDetail(InventoryBatchResponse):
    """库存批号详情"""
    days_to_expiry: Optional[int] = Field(None, description="距离过期天数")
    is_expired: bool = Field(False, description="是否已过期")


class BatchExpiryAlert(BaseModel):
    """批号过期预警"""
    batch_id: int
    batch_no: str
    product_id: int
    product_name: str
    warehouse_id: int
    warehouse_name: str
    expiry_date: datetime
    days_to_expiry: int
    quantity: Decimal


# ============ 批号流水相关 ============

class BatchTransactionResponse(BaseModel):
    """批号流水响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    batch_id: int
    transaction_type: str
    quantity: Decimal
    before_quantity: Optional[Decimal] = None
    after_quantity: Optional[Decimal] = None
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    reference_no: Optional[str] = None
    notes: Optional[str] = None
    created_by: Optional[int] = None
    created_at: datetime


class BatchAdjustment(BaseModel):
    """批号调整"""
    batch_id: int = Field(..., description="批次ID")
    adjust_quantity: Decimal = Field(..., description="调整数量（正数增加，负数减少）")
    notes: Optional[str] = Field(None, description="备注")


class BatchTransfer(BaseModel):
    """批号调拨"""
    batch_id: int = Field(..., description="源批次ID")
    to_warehouse_id: int = Field(..., description="目标仓库ID")
    quantity: Decimal = Field(..., description="调拨数量")
    new_batch_no: Optional[str] = Field(None, description="新批号（可选）")
    notes: Optional[str] = Field(None, description="备注")
