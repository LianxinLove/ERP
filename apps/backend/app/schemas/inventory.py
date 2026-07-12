"""
库存管理 Pydantic Schemas

@description 库存模块的请求/响应模型
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# ============ 产品相关 ============

class ProductBase(BaseModel):
    """产品基础模型"""
    code: str = Field(..., max_length=50, description="产品编码")
    name: str = Field(..., max_length=200, description="产品名称")
    specification: Optional[str] = Field(None, max_length=100, description="规格型号")
    unit: Optional[str] = Field(None, max_length=20, description="单位")
    category: Optional[str] = Field(None, max_length=100, description="分类")
    barcode: Optional[str] = Field(None, max_length=50, description="条码")
    cost_price: Optional[Decimal] = Field(None, description="成本价")
    selling_price: Optional[Decimal] = Field(None, description="销售价")
    min_stock: Optional[Decimal] = Field(None, description="最小库存")
    max_stock: Optional[Decimal] = Field(None, description="最大库存")
    lead_time: Optional[int] = Field(None, description="采购提前期（天）")
    notes: Optional[str] = Field(None, description="备注")


class ProductCreate(ProductBase):
    """创建产品"""
    status: Optional[str] = Field("active", description="状态")


class ProductUpdate(BaseModel):
    """更新产品"""
    name: Optional[str] = Field(None, max_length=200, description="产品名称")
    specification: Optional[str] = Field(None, max_length=100, description="规格型号")
    unit: Optional[str] = Field(None, max_length=20, description="单位")
    category: Optional[str] = Field(None, max_length=100, description="分类")
    barcode: Optional[str] = Field(None, max_length=50, description="条码")
    cost_price: Optional[Decimal] = Field(None, description="成本价")
    selling_price: Optional[Decimal] = Field(None, description="销售价")
    min_stock: Optional[Decimal] = Field(None, description="最小库存")
    max_stock: Optional[Decimal] = Field(None, description="最大库存")
    lead_time: Optional[int] = Field(None, description="采购提前期（天）")
    notes: Optional[str] = Field(None, description="备注")
    status: Optional[str] = Field(None, description="状态")


class ProductResponse(ProductBase):
    """产品响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    created_at: datetime
    updated_at: datetime


# ============ 仓库相关 ============

class WarehouseBase(BaseModel):
    """仓库基础模型"""
    code: str = Field(..., max_length=50, description="仓库编码")
    name: str = Field(..., max_length=200, description="仓库名称")
    address: Optional[str] = Field(None, description="地址")
    manager_id: Optional[int] = Field(None, description="负责人ID")
    contact: Optional[str] = Field(None, max_length=50, description="联系电话")
    capacity: Optional[Decimal] = Field(None, description="容量")
    notes: Optional[str] = Field(None, description="备注")


class WarehouseCreate(WarehouseBase):
    """创建仓库"""
    pass


class WarehouseUpdate(BaseModel):
    """更新仓库"""
    name: Optional[str] = Field(None, max_length=200, description="仓库名称")
    address: Optional[str] = Field(None, description="地址")
    manager_id: Optional[int] = Field(None, description="负责人ID")
    contact: Optional[str] = Field(None, max_length=50, description="联系电话")
    capacity: Optional[Decimal] = Field(None, description="容量")
    notes: Optional[str] = Field(None, description="备注")


class WarehouseResponse(WarehouseBase):
    """仓库响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


# ============ 库存相关 ============

class InventoryResponse(BaseModel):
    """库存响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    warehouse_id: int
    product_id: int
    quantity: Decimal
    allocated_quantity: Decimal
    available_quantity: Decimal
    last_updated: Optional[datetime] = None


class InventoryDetail(BaseModel):
    """库存详情"""
    id: int
    warehouse_id: int
    warehouse_name: Optional[str] = None
    product_id: int
    product_code: Optional[str] = None
    product_name: Optional[str] = None
    quantity: Decimal
    allocated_quantity: Decimal
    available_quantity: Decimal
    last_updated: Optional[datetime] = None


# ============ 库存流水相关 ============

class InventoryTransactionResponse(BaseModel):
    """库存流水响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    warehouse_id: int
    product_id: int
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


# ============ 库存调拨相关 ============

class InventoryTransferItemBase(BaseModel):
    """库存调拨明细基础模型"""
    product_id: int = Field(..., description="产品ID")
    quantity: Decimal = Field(..., description="数量")
    notes: Optional[str] = Field(None, description="备注")


class InventoryTransferItemCreate(InventoryTransferItemBase):
    """创建库存调拨明细"""
    pass


class InventoryTransferItemResponse(InventoryTransferItemBase):
    """库存调拨明细响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int


class InventoryTransferBase(BaseModel):
    """库存调拨基础模型"""
    from_warehouse_id: int = Field(..., description="调出仓库ID")
    to_warehouse_id: int = Field(..., description="调入仓库ID")
    transfer_date: datetime = Field(..., description="调拨日期")
    notes: Optional[str] = Field(None, description="备注")


class InventoryTransferCreate(InventoryTransferBase):
    """创建库存调拨"""
    items: List[InventoryTransferItemCreate] = Field(..., description="明细列表")


class InventoryTransferUpdate(BaseModel):
    """更新库存调拨"""
    from_warehouse_id: Optional[int] = Field(None, description="调出仓库ID")
    to_warehouse_id: Optional[int] = Field(None, description="调入仓库ID")
    transfer_date: Optional[datetime] = Field(None, description="调拨日期")
    notes: Optional[str] = Field(None, description="备注")
    items: Optional[List[InventoryTransferItemCreate]] = Field(None, description="明细列表")
    status: Optional[str] = Field(None, description="状态")


class InventoryTransferResponse(InventoryTransferBase):
    """库存调拨响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    transfer_no: str
    status: str
    created_at: datetime
    updated_at: datetime


class InventoryTransferDetail(InventoryTransferResponse):
    """库存调拨详情"""
    items: List[InventoryTransferItemResponse] = []
