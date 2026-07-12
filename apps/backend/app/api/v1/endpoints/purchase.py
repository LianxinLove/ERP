"""
采购管理 API 端点

@description 采购模块的 API 接口

@endpoints
- 供应商管理
- 采购申请管理
- 采购订单管理
"""

from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_current_superuser, get_db
from app.schemas.user import UserResponse
from app.schemas.purchase import (
    SupplierCreate,
    SupplierUpdate,
    SupplierResponse,
    PurchaseRequestCreate,
    PurchaseRequestUpdate,
    PurchaseRequestResponse,
    PurchaseRequestDetail,
    PurchaseOrderCreate,
    PurchaseOrderUpdate,
    PurchaseOrderResponse,
    PurchaseOrderDetail,
    ReceiptOrderCreate,
    ReceiptOrderReceive,
    ReceiptOrderInspect,
    ReceiptOrderStock,
    ReceiptOrderResponse,
    ReceiptOrderDetail,
)
from app.services.purchase import (
    SupplierService,
    PurchaseRequestService,
    PurchaseOrderService,
    ReceiptOrderService,
)

router = APIRouter()


# ============ 供应商相关端点 ============

@router.get("/suppliers", response_model=List[SupplierResponse])
async def get_suppliers(
    status: Annotated[Optional[str], Query(description="状态筛选")] = None,
    keyword: Annotated[Optional[str], Query(description="关键词搜索")] = None,
    skip: Annotated[int, Query(description="跳过条数")] = 0,
    limit: Annotated[int, Query(description="限制条数")] = 100,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取供应商列表"""
    service = SupplierService(db)
    return await service.get_suppliers(status=status, keyword=keyword, skip=skip, limit=limit)


@router.get("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(
    supplier_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取供应商详情"""
    service = SupplierService(db)
    return await service.get_supplier(supplier_id)


@router.post("/suppliers", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    data: SupplierCreate,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """创建供应商"""
    service = SupplierService(db)
    return await service.create_supplier(data)


@router.put("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: int,
    data: SupplierUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """更新供应商"""
    service = SupplierService(db)
    return await service.update_supplier(supplier_id, data)


@router.delete("/suppliers/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplier(
    supplier_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """删除供应商"""
    service = SupplierService(db)
    await service.delete_supplier(supplier_id)


# ============ 采购申请相关端点 ============

@router.get("/requests", response_model=List[PurchaseRequestResponse])
async def get_purchase_requests(
    applicant_id: Annotated[Optional[int], Query(description="申请人筛选")] = None,
    status: Annotated[Optional[str], Query(description="状态筛选")] = None,
    department_id: Annotated[Optional[int], Query(description="部门筛选")] = None,
    keyword: Annotated[Optional[str], Query(description="关键词搜索")] = None,
    skip: Annotated[int, Query(description="跳过条数")] = 0,
    limit: Annotated[int, Query(description="限制条数")] = 100,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取采购申请列表"""
    service = PurchaseRequestService(db)
    return await service.get_requests(
        applicant_id=applicant_id,
        status=status,
        department_id=department_id,
        keyword=keyword,
        skip=skip,
        limit=limit,
    )


@router.get("/requests/{request_id}", response_model=PurchaseRequestDetail)
async def get_purchase_request(
    request_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取采购申请详情"""
    service = PurchaseRequestService(db)
    return await service.get_request(request_id)


@router.post("/requests", response_model=PurchaseRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_request(
    data: PurchaseRequestCreate,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """创建采购申请"""
    service = PurchaseRequestService(db)
    return await service.create_request(data, current_user.id)


@router.put("/requests/{request_id}", response_model=PurchaseRequestResponse)
async def update_purchase_request(
    request_id: int,
    data: PurchaseRequestUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """更新采购申请"""
    service = PurchaseRequestService(db)
    return await service.update_request(request_id, data)


@router.post("/requests/{request_id}/submit", response_model=PurchaseRequestResponse)
async def submit_purchase_request(
    request_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """提交采购申请（启动审批流程）"""
    service = PurchaseRequestService(db)
    return await service.submit_request(request_id)


@router.delete("/requests/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_purchase_request(
    request_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """删除采购申请"""
    service = PurchaseRequestService(db)
    await service.delete_request(request_id)


# ============ 采购订单相关端点 ============

@router.get("/orders", response_model=List[PurchaseOrderResponse])
async def get_purchase_orders(
    supplier_id: Annotated[Optional[int], Query(description="供应商筛选")] = None,
    status: Annotated[Optional[str], Query(description="状态筛选")] = None,
    keyword: Annotated[Optional[str], Query(description="关键词搜索")] = None,
    skip: Annotated[int, Query(description="跳过条数")] = 0,
    limit: Annotated[int, Query(description="限制条数")] = 100,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取采购订单列表"""
    service = PurchaseOrderService(db)
    return await service.get_orders(
        supplier_id=supplier_id,
        status=status,
        keyword=keyword,
        skip=skip,
        limit=limit,
    )


@router.get("/orders/{order_id}", response_model=PurchaseOrderDetail)
async def get_purchase_order(
    order_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取采购订单详情"""
    service = PurchaseOrderService(db)
    return await service.get_order(order_id)


@router.post("/orders", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_order(
    data: PurchaseOrderCreate,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """创建采购订单"""
    service = PurchaseOrderService(db)
    return await service.create_order(data)


@router.put("/orders/{order_id}", response_model=PurchaseOrderResponse)
async def update_purchase_order(
    order_id: int,
    data: PurchaseOrderUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """更新采购订单"""
    service = PurchaseOrderService(db)
    return await service.update_order(order_id, data)


@router.post("/orders/{order_id}/confirm", response_model=PurchaseOrderResponse)
async def confirm_purchase_order(
    order_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    确认采购订单

    需要用户拥有采购管理权限
    """
    # 权限检查：只有超级管理员或具有采购管理权限的用户才能确认订单
    # TODO: 实现细粒度权限检查时，应检查 "purchase.order.confirm" 权限
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要采购管理员权限才能确认采购订单"
        )
    service = PurchaseOrderService(db)
    return await service.confirm_order(order_id)


@router.post("/orders/{order_id}/cancel", response_model=PurchaseOrderResponse)
async def cancel_purchase_order(
    order_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    取消采购订单

    需要用户拥有采购管理权限
    """
    # 权限检查：只有超级管理员或具有采购管理权限的用户才能取消订单
    # TODO: 实现细粒度权限检查时，应检查 "purchase.order.cancel" 权限
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要采购管理员权限才能取消采购订单"
        )
    service = PurchaseOrderService(db)
    return await service.cancel_order(order_id)


@router.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_purchase_order(
    order_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """删除采购订单"""
    service = PurchaseOrderService(db)
    await service.delete_order(order_id)


# ============ 收货单相关端点 ============

@router.get("/receipts", response_model=List[ReceiptOrderResponse])
async def get_receipt_orders(
    supplier_id: Annotated[Optional[int], Query(description="供应商筛选")] = None,
    status: Annotated[Optional[str], Query(description="状态筛选")] = None,
    keyword: Annotated[Optional[str], Query(description="关键词搜索")] = None,
    skip: Annotated[int, Query(description="跳过条数")] = 0,
    limit: Annotated[int, Query(description="限制条数")] = 100,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取收货单列表"""
    service = ReceiptOrderService(db)
    return await service.get_receipts(
        supplier_id=supplier_id,
        status=status,
        keyword=keyword,
        skip=skip,
        limit=limit,
    )


@router.get("/receipts/{receipt_id}", response_model=ReceiptOrderDetail)
async def get_receipt_order(
    receipt_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取收货单详情"""
    service = ReceiptOrderService(db)
    return await service.get_receipt(receipt_id)


@router.post("/receipts", response_model=ReceiptOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_receipt_order(
    data: ReceiptOrderCreate,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """创建收货单"""
    service = ReceiptOrderService(db)
    return await service.create_receipt(data)


@router.post("/receipts/{receipt_id}/receive", response_model=ReceiptOrderResponse)
async def receive_receipt_order(
    receipt_id: int,
    data: ReceiptOrderReceive,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """收货确认"""
    service = ReceiptOrderService(db)
    return await service.receive_receipt(receipt_id, data)


@router.post("/receipts/{receipt_id}/inspect", response_model=ReceiptOrderResponse)
async def inspect_receipt_order(
    receipt_id: int,
    data: ReceiptOrderInspect,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """质检处理"""
    service = ReceiptOrderService(db)
    return await service.inspect_receipt(receipt_id, data)


@router.post("/receipts/{receipt_id}/stock", response_model=ReceiptOrderResponse)
async def stock_receipt_order(
    receipt_id: int,
    data: ReceiptOrderStock,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """入库确认"""
    service = ReceiptOrderService(db)
    return await service.stock_receipt(receipt_id, data)


@router.post("/receipts/{receipt_id}/cancel", response_model=ReceiptOrderResponse)
async def cancel_receipt_order(
    receipt_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """取消收货单"""
    service = ReceiptOrderService(db)
    return await service.cancel_receipt(receipt_id)
