"""
序列号管理 API 端点

@description 序列号模块的 API 接口

@endpoints
- 序列号管理
- 序列号销售
- 序列号退货
- 序列号保修
- 序列号追溯
"""

from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_current_superuser, get_db
from app.schemas.user import UserResponse
from app.schemas.serial_number import (
    ProductSerialNumberCreate,
    ProductSerialNumberUpdate,
    ProductSerialNumberResponse,
    ProductSerialNumberDetail,
    SerialNumberSale,
    SerialNumberReturn,
    SerialNumberWarranty,
    SerialNumberTransactionResponse,
)
from app.services.serial_number import SerialNumberService

router = APIRouter()


@router.get("/serial-numbers", response_model=List[ProductSerialNumberResponse])
async def get_serial_numbers(
    product_id: Annotated[Optional[int], Query(description="产品筛选")] = None,
    warehouse_id: Annotated[Optional[int], Query(description="仓库筛选")] = None,
    status: Annotated[Optional[str], Query(description="状态筛选")] = None,
    keyword: Annotated[Optional[str], Query(description="关键词搜索")] = None,
    skip: Annotated[int, Query(description="跳过条数")] = 0,
    limit: Annotated[int, Query(description="限制条数")] = 100,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取序列号列表"""
    service = SerialNumberService(db)
    return await service.get_serial_numbers(
        product_id=product_id,
        warehouse_id=warehouse_id,
        status=status,
        keyword=keyword,
        skip=skip,
        limit=limit,
    )


@router.get("/serial-numbers/{serial_id}", response_model=ProductSerialNumberDetail)
async def get_serial_number(
    serial_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取序列号详情"""
    service = SerialNumberService(db)
    serial = await service.get_serial_number(serial_id)

    # 计算距离保修到期天数
    days_to_warranty_expiry = None
    is_warranty_expired = False
    if serial.warranty_expiry:
        days_to_warranty_expiry = (serial.warranty_expiry - datetime.now(serial.warranty_expiry.tzinfo)).days
        is_warranty_expired = days_to_warranty_expiry < 0

    # 获取交易次数
    transactions = await service.get_serial_number_transactions(serial_id, limit=1000)
    transaction_count = len(transactions)

    return ProductSerialNumberDetail(
        **serial.__dict__,
        days_to_warranty_expiry=days_to_warranty_expiry,
        is_warranty_expired=is_warranty_expired,
        transaction_count=transaction_count,
    )


@router.post("/serial-numbers", response_model=ProductSerialNumberResponse, status_code=status.HTTP_201_CREATED)
async def create_serial_number(
    data: ProductSerialNumberCreate,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """创建序列号"""
    service = SerialNumberService(db)
    return await service.create_serial_number(data)


@router.post("/serial-numbers/sale", response_model=List[ProductSerialNumberResponse])
async def sale_serial_numbers(
    data: SerialNumberSale,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """销售序列号"""
    service = SerialNumberService(db)
    return await service.sale_serial_numbers(data)


@router.post("/serial-numbers/{serial_id}/return", response_model=ProductSerialNumberResponse)
async def return_serial_number(
    serial_id: int,
    data: SerialNumberReturn,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """序列号退货"""
    service = SerialNumberService(db)
    return await service.return_serial_number(serial_id, data)


@router.post("/serial-numbers/{serial_id}/warranty", response_model=ProductSerialNumberResponse)
async def update_serial_number_warranty(
    serial_id: int,
    data: SerialNumberWarranty,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """更新序列号保修信息"""
    service = SerialNumberService(db)
    return await service.update_warranty(serial_id, data)


@router.get("/serial-numbers/warranty-alerts")
async def get_warranty_alerts(
    days_threshold: Annotated[int, Query(description="天数阈值")] = 30,
    skip: Annotated[int, Query(description="跳过条数")] = 0,
    limit: Annotated[int, Query(description="限制条数")] = 100,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取即将过保的序列号列表"""
    service = SerialNumberService(db)
    return await service.get_warranty_alerts(
        days_threshold=days_threshold,
        skip=skip,
        limit=limit,
    )


@router.get("/serial-numbers/{serial_id}/trace")
async def trace_serial_number(
    serial_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """追溯序列号完整历史"""
    service = SerialNumberService(db)
    return await service.trace_serial_number(serial_id)


@router.get("/serial-numbers/{serial_id}/transactions", response_model=List[SerialNumberTransactionResponse])
async def get_serial_number_transactions(
    serial_id: int,
    skip: Annotated[int, Query(description="跳过条数")] = 0,
    limit: Annotated[int, Query(description="限制条数")] = 100,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取序列号流水列表"""
    service = SerialNumberService(db)
    return await service.get_serial_number_transactions(serial_id, skip=skip, limit=limit)
