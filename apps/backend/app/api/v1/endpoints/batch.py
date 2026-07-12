"""
批号管理 API 端点

@description 批号模块的 API 接口

@endpoints
- 批号管理
- 批号调整
- 批号调拨
- 批号流水查询
"""

from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_current_superuser, get_db
from app.schemas.user import UserResponse
from app.schemas.batch import (
    InventoryBatchCreate,
    InventoryBatchUpdate,
    InventoryBatchResponse,
    InventoryBatchDetail,
    BatchAdjustment,
    BatchTransfer,
    BatchTransactionResponse,
)
from app.services.batch import BatchService

router = APIRouter()


@router.get("/batches", response_model=List[InventoryBatchResponse])
async def get_batches(
    product_id: Annotated[Optional[int], Query(description="产品筛选")] = None,
    warehouse_id: Annotated[Optional[int], Query(description="仓库筛选")] = None,
    status: Annotated[Optional[str], Query(description="状态筛选")] = None,
    include_expired: Annotated[bool, Query(description="是否包含已过期")] = False,
    skip: Annotated[int, Query(description="跳过条数")] = 0,
    limit: Annotated[int, Query(description="限制条数")] = 100,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取批号列表"""
    service = BatchService(db)
    return await service.get_batches(
        product_id=product_id,
        warehouse_id=warehouse_id,
        status=status,
        include_expired=include_expired,
        skip=skip,
        limit=limit,
    )


@router.get("/batches/{batch_id}", response_model=InventoryBatchDetail)
async def get_batch(
    batch_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取批号详情"""
    service = BatchService(db)
    batch = await service.get_batch(batch_id)

    # 计算距离过期天数
    days_to_expiry = None
    is_expired = False
    if batch.expiry_date:
        days_to_expiry = (batch.expiry_date - datetime.now(batch.expiry_date.tzinfo)).days
        is_expired = days_to_expiry < 0

    return InventoryBatchDetail(
        **batch.__dict__,
        days_to_expiry=days_to_expiry,
        is_expired=is_expired,
    )


@router.post("/batches", response_model=InventoryBatchResponse, status_code=status.HTTP_201_CREATED)
async def create_batch(
    data: InventoryBatchCreate,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """创建批号"""
    service = BatchService(db)
    return await service.create_batch(data)


@router.post("/batches/{batch_id}/adjust", response_model=InventoryBatchResponse)
async def adjust_batch(
    batch_id: int,
    data: BatchAdjustment,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """调整批号数量"""
    service = BatchService(db)
    return await service.adjust_batch(batch_id, data)


@router.post("/batches/{batch_id}/transfer", response_model=InventoryBatchResponse)
async def transfer_batch(
    batch_id: int,
    data: BatchTransfer,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """批号调拨"""
    service = BatchService(db)
    return await service.transfer_batch(batch_id, data)


@router.get("/batches/expiry-alerts")
async def get_expiry_alerts(
    days_threshold: Annotated[int, Query(description="天数阈值")] = 30,
    skip: Annotated[int, Query(description="跳过条数")] = 0,
    limit: Annotated[int, Query(description="限制条数")] = 100,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取即将过期的批号列表"""
    service = BatchService(db)
    return await service.get_expiry_alerts(
        days_threshold=days_threshold,
        skip=skip,
        limit=limit,
    )


@router.post("/batches/update-expired")
async def update_expired_batches(
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """更新过期批号状态（需超级管理员权限）"""
    service = BatchService(db)
    count = await service.update_expired_batches()
    return {"updated_count": count}


@router.get("/batches/{batch_id}/transactions", response_model=List[BatchTransactionResponse])
async def get_batch_transactions(
    batch_id: int,
    skip: Annotated[int, Query(description="跳过条数")] = 0,
    limit: Annotated[int, Query(description="限制条数")] = 100,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取批号流水列表"""
    service = BatchService(db)
    return await service.get_batch_transactions(batch_id, skip=skip, limit=limit)
