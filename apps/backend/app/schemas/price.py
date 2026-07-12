"""
价格管理Schema
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field


class PriceListLineBase(BaseModel):
    """价格表明细基础"""
    product_id: Optional[int] = None
    product_code: Optional[str] = None
    product_name: str = Field(..., max_length=200)
    unit_price: Decimal
    currency: str = "CNY"
    min_quantity: Optional[Decimal] = None
    max_quantity: Optional[Decimal] = None
    discount_rate: Optional[Decimal] = None


class PriceListLineCreate(PriceListLineBase):
    """创建价格表明细"""
    pass


class PriceListLineResponse(PriceListLineBase):
    """价格表明细响应"""
    id: int
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None

    class Config:
        from_attributes = True


class PriceListBase(BaseModel):
    """价格表基础"""
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=50)
    description: Optional[str] = None
    type: str = "standard"
    customer_id: Optional[int] = None
    customer_group: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    currency: str = "CNY"
    priority: int = 0
    notes: Optional[str] = None


class PriceListCreate(PriceListBase):
    """创建价格表"""
    lines: List[PriceListLineCreate]


class PriceListResponse(PriceListBase):
    """价格表响应"""
    id: int
    status: str
    is_default: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GetProductPriceRequest(BaseModel):
    """获取产品价格请求"""
    product_id: int
    customer_id: Optional[int] = None
    quantity: Decimal = Field(default=1, ge=1)
    currency: str = "CNY"
    date: Optional[datetime] = None


class GetProductPriceResponse(BaseModel):
    """获取产品价格响应"""
    product_id: int
    unit_price: Decimal
    currency: str
    price_list: Optional[str] = None
    discount_policy: Optional[str] = None
    final_price: Decimal
    applicable_discounts: List[str] = []
