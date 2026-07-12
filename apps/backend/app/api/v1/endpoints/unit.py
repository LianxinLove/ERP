"""
多单位换算 API 端点

@description 单位换算模块的 API 接口

@endpoints
- 产品单位管理
- 单位换算管理
- 单位数量换算
"""

from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_current_superuser, get_db
from app.schemas.user import UserResponse
from app.schemas.unit import (
    ProductUnitCreate,
    ProductUnitUpdate,
    ProductUnitResponse,
    UnitConversionCreate,
    UnitConversionResponse,
    UnitConversionRequest,
    UnitConversionResult,
)
from app.services.unit import UnitService, UnitConversionService

router = APIRouter()


# ============ 产品单位相关端点 ============

@router.get("/units", response_model=List[ProductUnitResponse])
async def get_units(
    product_id: Annotated[Optional[int], Query(description="产品筛选")] = None,
    unit_type: Annotated[Optional[str], Query(description="单位类型筛选")] = None,
    skip: Annotated[int, Query(description="跳过条数")] = 0,
    limit: Annotated[int, Query(description="限制条数")] = 100,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取单位列表"""
    service = UnitService(db)
    return await service.get_units(
        product_id=product_id,
        unit_type=unit_type,
        skip=skip,
        limit=limit,
    )


@router.get("/units/{unit_id}", response_model=ProductUnitResponse)
async def get_unit(
    unit_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取单位详情"""
    service = UnitService(db)
    return await service.get_unit(unit_id)


@router.post("/units", response_model=ProductUnitResponse, status_code=status.HTTP_201_CREATED)
async def create_unit(
    data: ProductUnitCreate,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """创建单位"""
    service = UnitService(db)
    return await service.create_unit(data)


@router.put("/units/{unit_id}", response_model=ProductUnitResponse)
async def update_unit(
    unit_id: int,
    data: ProductUnitUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """更新单位"""
    service = UnitService(db)
    return await service.update_unit(unit_id, data)


# ============ 单位换算相关端点 ============

@router.get("/conversions", response_model=List[UnitConversionResponse])
async def get_conversions(
    product_id: Annotated[Optional[int], Query(description="产品筛选")] = None,
    skip: Annotated[int, Query(description="跳过条数")] = 0,
    limit: Annotated[int, Query(description="限制条数")] = 100,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取换算关系列表"""
    service = UnitConversionService(db)
    return await service.get_conversions(
        product_id=product_id,
        skip=skip,
        limit=limit,
    )


@router.post("/conversions", response_model=UnitConversionResponse, status_code=status.HTTP_201_CREATED)
async def create_conversion(
    data: UnitConversionCreate,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """创建换算关系"""
    service = UnitConversionService(db)
    return await service.create_conversion(data)


@router.post("/convert", response_model=UnitConversionResult)
async def convert_quantity(
    data: UnitConversionRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """单位数量换算"""
    service = UnitConversionService(db)
    result = await service.convert_quantity(data)
    return UnitConversionResult(**result)


@router.get("/products/{product_id}/units-info")
async def get_product_units_info(
    product_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取产品的完整单位信息"""
    service = UnitConversionService(db)
    return await service.get_product_units_info(product_id)
