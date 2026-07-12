"""
发票管理 API 端点

@description 发票模块的 API 接口

@endpoints
- 销售发票管理
- 采购发票管理
- 发票勾稽
"""

from typing import Annotated, List, Optional, Dict, Any
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_current_superuser, get_db
from app.schemas.user import UserResponse
from app.schemas.invoice import (
    # 销售发票
    SalesInvoiceCreate,
    SalesInvoiceResponse,
    SalesInvoiceDetail,
    SalesInvoiceIssue,
    SalesInvoiceSend,
    # 采购发票
    PurchaseInvoiceCreate,
    PurchaseInvoiceResponse,
    PurchaseInvoiceDetail,
    PurchaseInvoiceReceive,
    PurchaseInvoiceVerify,
    # 勾稽
    InvoiceMatchRequest,
    InvoiceMatchResponse,
)
from app.services.invoice import (
    SalesInvoiceService,
    PurchaseInvoiceService,
    InvoiceMatchService,
)

router = APIRouter()


# ============ 销售发票相关端点 ============

@router.get("/sales", response_model=List[SalesInvoiceResponse])
async def get_sales_invoices(
    customer_id: Annotated[Optional[int], Query(description="客户筛选")] = None,
    status: Annotated[Optional[str], Query(description="状态筛选")] = None,
    keyword: Annotated[Optional[str], Query(description="关键词搜索")] = None,
    skip: Annotated[int, Query(description="跳过条数")] = 0,
    limit: Annotated[int, Query(description="限制条数")] = 100,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取销售发票列表"""
    service = SalesInvoiceService(db)
    return await service.get_invoices(
        customer_id=customer_id,
        status=status,
        keyword=keyword,
        skip=skip,
        limit=limit,
    )


@router.get("/sales/{invoice_id}", response_model=SalesInvoiceDetail)
async def get_sales_invoice(
    invoice_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取销售发票详情"""
    service = SalesInvoiceService(db)
    return await service.get_invoice(invoice_id)


@router.post("/sales", response_model=SalesInvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_sales_invoice(
    data: SalesInvoiceCreate,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """创建销售发票"""
    service = SalesInvoiceService(db)
    return await service.create_invoice(data)


@router.post("/sales/{invoice_id}/issue", response_model=SalesInvoiceResponse)
async def issue_sales_invoice(
    invoice_id: int,
    data: SalesInvoiceIssue,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """开具销售发票"""
    service = SalesInvoiceService(db)
    return await service.issue_invoice(invoice_id, data)


@router.post("/sales/{invoice_id}/send", response_model=SalesInvoiceResponse)
async def send_sales_invoice(
    invoice_id: int,
    data: SalesInvoiceSend,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """发送销售发票"""
    service = SalesInvoiceService(db)
    return await service.send_invoice(invoice_id, data)


@router.post("/sales/{invoice_id}/cancel", response_model=SalesInvoiceResponse)
async def cancel_sales_invoice(
    invoice_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """作废销售发票"""
    service = SalesInvoiceService(db)
    return await service.cancel_invoice(invoice_id)


# ============ 采购发票相关端点 ============

@router.get("/purchase", response_model=List[PurchaseInvoiceResponse])
async def get_purchase_invoices(
    supplier_id: Annotated[Optional[int], Query(description="供应商筛选")] = None,
    status: Annotated[Optional[str], Query(description="状态筛选")] = None,
    keyword: Annotated[Optional[str], Query(description="关键词搜索")] = None,
    skip: Annotated[int, Query(description="跳过条数")] = 0,
    limit: Annotated[int, Query(description="限制条数")] = 100,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取采购发票列表"""
    service = PurchaseInvoiceService(db)
    return await service.get_invoices(
        supplier_id=supplier_id,
        status=status,
        keyword=keyword,
        skip=skip,
        limit=limit,
    )


@router.get("/purchase/{invoice_id}", response_model=PurchaseInvoiceDetail)
async def get_purchase_invoice(
    invoice_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取采购发票详情"""
    service = PurchaseInvoiceService(db)
    return await service.get_invoice(invoice_id)


@router.post("/purchase", response_model=PurchaseInvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_invoice(
    data: PurchaseInvoiceCreate,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """创建采购发票"""
    service = PurchaseInvoiceService(db)
    return await service.create_invoice(data)


@router.post("/purchase/{invoice_id}/receive", response_model=PurchaseInvoiceResponse)
async def receive_purchase_invoice(
    invoice_id: int,
    data: PurchaseInvoiceReceive,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """接收采购发票"""
    service = PurchaseInvoiceService(db)
    return await service.receive_invoice(invoice_id, data)


@router.post("/purchase/{invoice_id}/verify", response_model=PurchaseInvoiceResponse)
async def verify_purchase_invoice(
    invoice_id: int,
    data: PurchaseInvoiceVerify,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """认证采购发票"""
    service = PurchaseInvoiceService(db)
    return await service.verify_invoice(invoice_id, data)


# ============ 发票勾稽相关端点 ============

@router.post("/sales/{invoice_id}/match", response_model=InvoiceMatchResponse)
async def match_sales_invoice(
    invoice_id: int,
    delivery_id: Annotated[Optional[int], Query(description="发货单ID")] = None,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """销售发票勾稽验证"""
    service = InvoiceMatchService(db)
    result = await service.match_sales_invoice(invoice_id, delivery_id)
    return InvoiceMatchResponse(**result)


@router.post("/purchase/{invoice_id}/match", response_model=InvoiceMatchResponse)
async def match_purchase_invoice(
    invoice_id: int,
    receipt_id: Annotated[Optional[int], Query(description="收货单ID")] = None,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """采购发票勾稽验证"""
    service = InvoiceMatchService(db)
    result = await service.match_purchase_invoice(invoice_id, receipt_id)
    return InvoiceMatchResponse(**result)
