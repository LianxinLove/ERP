"""
多单位换算 Pydantic Schemas

@description 单位换算模块的请求/响应模型
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# ============ 产品单位相关 ============

class ProductUnitBase(BaseModel):
    """产品单位基础模型"""
    product_id: int = Field(..., description="产品ID")
    unit_code: str = Field(..., max_length=20, description="单位编码")
    unit_name: str = Field(..., max_length=50, description="单位名称")
    unit_type: Optional[str] = Field("base", description="单位类型")
    is_base: Optional[bool] = Field(False, description="是否为基本单位")
    conversion_rate: Optional[Decimal] = Field(None, description="换算率")
    precision: Optional[int] = Field(2, description="小数位数")
    notes: Optional[str] = Field(None, description="备注")


class ProductUnitCreate(ProductUnitBase):
    """创建产品单位"""
    pass


class ProductUnitUpdate(BaseModel):
    """更新产品单位"""
    unit_name: Optional[str] = Field(None, max_length=50, description="单位名称")
    unit_type: Optional[str] = Field(None, description="单位类型")
    is_base: Optional[bool] = Field(None, description="是否为基本单位")
    conversion_rate: Optional[Decimal] = Field(None, description="换算率")
    precision: Optional[int] = Field(None, description="小数位数")
    notes: Optional[str] = Field(None, description="备注")


class ProductUnitResponse(ProductUnitBase):
    """产品单位响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


# ============ 单位换算相关 ============

class UnitConversionBase(BaseModel):
    """单位换算基础模型"""
    product_id: int = Field(..., description="产品ID")
    from_unit_id: int = Field(..., description="源单位ID")
    to_unit_id: int = Field(..., description="目标单位ID")
    conversion_rate: Decimal = Field(..., description="换算率")
    is_direct: Optional[bool] = Field(True, description="是否为直接换算")
    notes: Optional[str] = Field(None, description="备注")


class UnitConversionCreate(UnitConversionBase):
    """创建单位换算"""
    pass


class UnitConversionResponse(UnitConversionBase):
    """单位换算响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


# ============ 单位换算请求相关 ============

class UnitConversionRequest(BaseModel):
    """单位换算请求"""
    product_id: int = Field(..., description="产品ID")
    from_unit_id: int = Field(..., description="源单位ID")
    to_unit_id: int = Field(..., description="目标单位ID")
    quantity: Decimal = Field(..., description="数量")


class UnitConversionResult(BaseModel):
    """单位换算结果"""
    product_id: int
    from_unit_id: int
    from_unit_code: str
    from_unit_name: str
    to_unit_id: int
    to_unit_code: str
    to_unit_name: str
    original_quantity: Decimal
    converted_quantity: Decimal
    conversion_rate: Decimal
