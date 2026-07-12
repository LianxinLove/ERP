"""
序列号管理 Pydantic Schemas

@description 序列号模块的请求/响应模型
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# ============ 产品序列号相关 ============

class ProductSerialNumberBase(BaseModel):
    """产品序列号基础模型"""
    serial_number: str = Field(..., max_length=100, description="序列号")
    product_id: int = Field(..., description="产品ID")
    warehouse_id: int = Field(..., description="仓库ID")
    batch_id: Optional[int] = Field(None, description="批次ID")
    production_date: Optional[datetime] = Field(None, description="生产日期")
    warranty_expiry: Optional[datetime] = Field(None, description="保修到期日期")
    cost_price: Optional[Decimal] = Field(None, description="成本价")
    supplier_id: Optional[int] = Field(None, description="供应商ID")
    receipt_id: Optional[int] = Field(None, description="收货单ID")
    notes: Optional[str] = Field(None, description="备注")


class ProductSerialNumberCreate(ProductSerialNumberBase):
    """创建产品序列号"""
    pass


class ProductSerialNumberUpdate(BaseModel):
    """更新产品序列号"""
    warranty_expiry: Optional[datetime] = Field(None, description="保修到期日期")
    warranty_notes: Optional[str] = Field(None, description="保修备注")
    notes: Optional[str] = Field(None, description="备注")
    status: Optional[str] = Field(None, description="状态")


class ProductSerialNumberResponse(ProductSerialNumberBase):
    """产品序列号响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    customer_id: Optional[int] = None
    sale_date: Optional[datetime] = None
    warranty_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ProductSerialNumberDetail(ProductSerialNumberResponse):
    """产品序列号详情"""
    days_to_warranty_expiry: Optional[int] = Field(None, description="距离保修到期天数")
    is_warranty_expired: bool = Field(False, description="保修是否已过期")
    transaction_count: int = Field(0, description="交易次数")


class SerialNumberAllocate(BaseModel):
    """序列号分配"""
    serial_number_id: int = Field(..., description="序列号ID")
    customer_id: Optional[int] = Field(None, description="客户ID")
    delivery_id: Optional[int] = Field(None, description="发货单ID")
    notes: Optional[str] = Field(None, description="备注")


class SerialNumberSale(BaseModel):
    """序列号销售"""
    serial_numbers: List[int] = Field(..., description="序列号ID列表")
    customer_id: int = Field(..., description="客户ID")
    sale_date: datetime = Field(..., description="销售日期")
    order_id: Optional[int] = Field(None, description="订单ID")
    notes: Optional[str] = Field(None, description="备注")


class SerialNumberReturn(BaseModel):
    """序列号退货"""
    serial_number_id: int = Field(..., description="序列号ID")
    reason: Optional[str] = Field(None, description="退货原因")
    notes: Optional[str] = Field(None, description="备注")


class SerialNumberWarranty(BaseModel):
    """序列号保修"""
    serial_number_id: int = Field(..., description="序列号ID")
    warranty_expiry: Optional[datetime] = Field(None, description="保修到期日期")
    warranty_notes: Optional[str] = Field(None, description="保修备注")
    notes: Optional[str] = Field(None, description="备注")


# ============ 序列号流水相关 ============

class SerialNumberTransactionResponse(BaseModel):
    """序列号流水响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    serial_number_id: int
    transaction_type: str
    from_status: Optional[str] = None
    to_status: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    reference_no: Optional[str] = None
    customer_id: Optional[int] = None
    notes: Optional[str] = None
    created_by: Optional[int] = None
    created_at: datetime


class SerialNumberWarrantyAlert(BaseModel):
    """序列号保修到期预警"""
    serial_number_id: int
    serial_number: str
    product_id: int
    product_name: str
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    warranty_expiry: datetime
    days_to_expiry: int
    status: str
