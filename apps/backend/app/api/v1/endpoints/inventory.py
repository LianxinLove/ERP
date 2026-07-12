"""
库存管理 API 端点

@description 库存模块的 API 接口

@endpoints
- 仓库管理
- 产品管理
- 库存查询与调整
- 库存流水
- 库存调拨
"""

from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_current_superuser, get_db
from app.schemas.user import UserResponse
from app.schemas.inventory import (
    WarehouseCreate,
    WarehouseUpdate,
    WarehouseResponse,
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    InventoryTransferCreate,
    InventoryTransferUpdate,
    InventoryTransferResponse,
    InventoryTransferDetail,
)
from app.services.inventory import (
    WarehouseService,
    ProductService,
    InventoryService,
    InventoryTransferService,
)

router = APIRouter()


# ============ 仓库相关端点 ============

@router.get("/warehouses", response_model=List[WarehouseResponse])
async def get_warehouses(
    skip: Annotated[int, Query(description="跳过条数")] = 0,
    limit: Annotated[int, Query(description="限制条数")] = 100,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取仓库列表"""
    service = WarehouseService(db)
    return await service.get_warehouses(skip=skip, limit=limit)


@router.get("/warehouses/{warehouse_id}", response_model=WarehouseResponse)
async def get_warehouse(
    warehouse_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取仓库详情"""
    service = WarehouseService(db)
    return await service.get_warehouse(warehouse_id)


@router.post("/warehouses", response_model=WarehouseResponse, status_code=status.HTTP_201_CREATED)
async def create_warehouse(
    data: WarehouseCreate,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """创建仓库"""
    service = WarehouseService(db)
    return await service.create_warehouse(data)


@router.put("/warehouses/{warehouse_id}", response_model=WarehouseResponse)
async def update_warehouse(
    warehouse_id: int,
    data: WarehouseUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """更新仓库"""
    service = WarehouseService(db)
    return await service.update_warehouse(warehouse_id, data)


@router.delete("/warehouses/{warehouse_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_warehouse(
    warehouse_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """删除仓库"""
    service = WarehouseService(db)
    await service.delete_warehouse(warehouse_id)


# ============ 产品相关端点 ============

@router.get("/products", response_model=List[ProductResponse])
async def get_products(
    category: Annotated[Optional[str], Query(description="分类筛选")] = None,
    keyword: Annotated[Optional[str], Query(description="关键词搜索")] = None,
    status: Annotated[Optional[str], Query(description="状态筛选")] = None,
    skip: Annotated[int, Query(description="跳过条数")] = 0,
    limit: Annotated[int, Query(description="限制条数")] = 100,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取产品列表"""
    service = ProductService(db)
    return await service.get_products(
        category=category,
        keyword=keyword,
        status=status,
        skip=skip,
        limit=limit,
    )


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取产品详情"""
    service = ProductService(db)
    return await service.get_product(product_id)


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """创建产品"""
    service = ProductService(db)
    return await service.create_product(data)


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """更新产品"""
    service = ProductService(db)
    return await service.update_product(product_id, data)


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """删除产品"""
    service = ProductService(db)
    await service.delete_product(product_id)


# ============ 库存查询相关端点 ============

@router.get("/inventories")
async def get_inventories(
    warehouse_id: Annotated[Optional[int], Query(description="仓库筛选")] = None,
    product_id: Annotated[Optional[int], Query(description="产品筛选")] = None,
    low_stock_only: Annotated[bool, Query(description="仅低库存")] = False,
    skip: Annotated[int, Query(description="跳过条数")] = 0,
    limit: Annotated[int, Query(description="限制条数")] = 100,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取库存列表"""
    service = InventoryService(db)
    return await service.get_inventories(
        warehouse_id=warehouse_id,
        product_id=product_id,
        low_stock_only=low_stock_only,
        skip=skip,
        limit=limit,
    )


@router.get("/transactions")
async def get_inventory_transactions(
    warehouse_id: Annotated[Optional[int], Query(description="仓库筛选")] = None,
    product_id: Annotated[Optional[int], Query(description="产品筛选")] = None,
    transaction_type: Annotated[Optional[str], Query(description="流水类型筛选")] = None,
    skip: Annotated[int, Query(description="跳过条数")] = 0,
    limit: Annotated[int, Query(description="限制条数")] = 100,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取库存流水列表"""
    service = InventoryService(db)
    return await service.get_transactions(
        warehouse_id=warehouse_id,
        product_id=product_id,
        transaction_type=transaction_type,
        skip=skip,
        limit=limit,
    )


# ============ 库存调拨相关端点 ============

@router.get("/transfers", response_model=List[InventoryTransferResponse])
async def get_inventory_transfers(
    status: Annotated[Optional[str], Query(description="状态筛选")] = None,
    skip: Annotated[int, Query(description="跳过条数")] = 0,
    limit: Annotated[int, Query(description="限制条数")] = 100,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取库存调拨列表"""
    service = InventoryTransferService(db)
    return await service.get_transfers(status=status, skip=skip, limit=limit)


@router.get("/transfers/{transfer_id}", response_model=InventoryTransferDetail)
async def get_inventory_transfer(
    transfer_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取库存调拨详情"""
    service = InventoryTransferService(db)
    return await service.get_transfer(transfer_id)


@router.post("/transfers", response_model=InventoryTransferResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory_transfer(
    data: InventoryTransferCreate,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    创建库存调拨

    需要用户拥有库存管理权限
    """
    # 权限检查：只有超级管理员或具有库存管理权限的用户才能创建调拨单
    # TODO: 实现细粒度权限检查时，应检查 "inventory.transfer.create" 权限
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要库存管理员权限才能创建库存调拨单"
        )
    service = InventoryTransferService(db)
    return await service.create_transfer(data)


@router.post("/transfers/{transfer_id}/execute", response_model=InventoryTransferResponse)
async def execute_inventory_transfer(
    transfer_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    执行库存调拨

    需要用户拥有库存管理权限
    """
    # 权限检查：只有超级管理员或具有库存管理权限的用户才能执行调拨
    # TODO: 实现细粒度权限检查时，应检查 "inventory.transfer.execute" 权限
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要库存管理员权限才能执行库存调拨"
        )
    service = InventoryTransferService(db)
    return await service.execute_transfer(transfer_id)


@router.delete("/transfers/{transfer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory_transfer(
    transfer_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    删除库存调拨

    需要用户拥有库存管理权限
    """
    # 权限检查：只有超级管理员或具有库存管理权限的用户才能删除调拨单
    # TODO: 实现细粒度权限检查时，应检查 "inventory.transfer.delete" 权限
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要库存管理员权限才能删除库存调拨单"
        )
    service = InventoryTransferService(db)
    await service.delete_transfer(transfer_id)
