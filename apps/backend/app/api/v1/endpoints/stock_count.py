"""
库存盘点 API 端点

@description 盘点模块的 API 接口

@endpoints
- 盘点单管理
- 盘点审核
- 盘点完成
- 差异处理
"""
from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_current_superuser, get_db
from app.schemas.user import UserResponse
from app.schemas.stock_count import (
    StockCountCreate,
    StockCountUpdate,
    StockCountResponse,
    StockCountDetail,
    StockCountApprove,
    StockCountComplete,
    StockCountDifferenceResponse,
    DifferenceHandle,
    StockCountSummary,
)
from app.services.stock_count import StockCountService

router = APIRouter()


@router.get("/stock-counts", response_model=List[StockCountResponse])
async def get_stock_counts(
    warehouse_id: Annotated[Optional[int], Query(description="仓库筛选")] = None,
    status: Annotated[Optional[str], Query(description="状态筛选")] = None,
    keyword: Annotated[Optional[str], Query(description="关键词搜索")] = None,
    skip: Annotated[int, Query(description="跳过条数")] = 0,
    limit: Annotated[int, Query(description="限制条数")] = 100,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取盘点单列表"""
    service = StockCountService(db)
    return await service.get_stock_counts(
        warehouse_id=warehouse_id,
        status=status,
        keyword=keyword,
        skip=skip,
        limit=limit,
    )


@router.get("/stock-counts/summary", response_model=StockCountSummary)
async def get_stock_count_summary(
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取盘点汇总统计"""
    service = StockCountService(db)
    return await service.get_summary()


@router.get("/stock-counts/{count_id}", response_model=StockCountDetail)
async def get_stock_count(
    count_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取盘点单详情"""
    service = StockCountService(db)
    return await service.get_stock_count(count_id)


@router.post("/stock-counts", response_model=StockCountResponse, status_code=status.HTTP_201_CREATED)
async def create_stock_count(
    data: StockCountCreate,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """创建盘点单"""
    service = StockCountService(db)
    return await service.create_stock_count(data, current_user.id)


@router.post("/stock-counts/{count_id}/approve", response_model=StockCountResponse)
async def approve_stock_count(
    count_id: int,
    data: StockCountApprove,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """审核盘点单（需超级管理员权限）"""
    service = StockCountService(db)
    return await service.approve_stock_count(count_id, data)


@router.post("/stock-counts/{count_id}/complete", response_model=StockCountResponse)
async def complete_stock_count(
    count_id: int,
    data: StockCountComplete,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """完成盘点单"""
    service = StockCountService(db)
    return await service.complete_stock_count(count_id, data)


@router.get("/stock-counts/differences", response_model=List[StockCountDifferenceResponse])
async def get_differences(
    count_id: Annotated[Optional[int], Query(description="盘点单筛选")] = None,
    status: Annotated[Optional[str], Query(description="状态筛选")] = None,
    skip: Annotated[int, Query(description="跳过条数")] = 0,
    limit: Annotated[int, Query(description="限制条数")] = 100,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取盘点差异列表"""
    from app.models.stock_count import StockCountDifference

    query = select(StockCountDifference)

    if count_id:
        query = query.where(StockCountDifference.count_id == count_id)
    if status:
        query = query.where(StockCountDifference.status == status)

    query = query.order_by(StockCountDifference.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


@router.post("/stock-counts/differences/{difference_id}/handle", response_model=StockCountDifferenceResponse)
async def handle_difference(
    difference_id: int,
    data: DifferenceHandle,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """处理盘点差异（需超级管理员权限）"""
    service = StockCountService(db)
    return await service.handle_difference(difference_id, data, current_user.id)
