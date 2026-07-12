"""
财务管理 API 端点

@description 财务模块的 API 接口

@endpoints
- 科目管理
- 付款方式管理
- 应收账款管理
- 应付账款管理
- 收付款记录管理
- 财务统计
"""

from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_current_superuser, get_db
from app.schemas.user import UserResponse
from app.schemas.finance import (
    # 科目相关
    AccountCreate,
    AccountUpdate,
    AccountResponse,
    AccountTree,
    # 付款方式相关
    PaymentMethodCreate,
    PaymentMethodUpdate,
    PaymentMethodResponse,
    # 应收账款相关
    ReceivableCreate,
    ReceivableUpdate,
    ReceivableResponse,
    ReceivableDetail,
    ReceivableStatus,
    # 应付账款相关
    PayableCreate,
    PayableUpdate,
    PayableResponse,
    PayableDetail,
    PayableStatus,
    # 收付款记录相关
    PaymentCreate,
    PaymentUpdate,
    PaymentResponse,
    PaymentDetail,
    PaymentType,
    PaymentStatus,
    # 统计相关
    FinanceSummary,
)
from app.services.finance import (
    AccountService,
    PaymentMethodService,
    ReceivableService,
    PayableService,
    PaymentService,
)

router = APIRouter()


# ============ 科目相关端点 ============

@router.get("/accounts/tree", response_model=List[AccountTree])
async def get_account_tree(
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取科目树形结构"""
    service = AccountService(db)
    return await service.get_account_tree()


@router.get("/accounts", response_model=List[AccountResponse])
async def get_accounts(
    account_type: Annotated[Optional[str], Query(description="科目类型筛选")] = None,
    is_active: Annotated[Optional[bool], Query(description="是否启用")] = None,
    skip: Annotated[int, Query(description="跳过条数")] = 0,
    limit: Annotated[int, Query(description="限制条数")] = 100,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取科目列表"""
    service = AccountService(db)
    return await service.get_accounts(
        account_type=account_type,
        is_active=is_active,
        skip=skip,
        limit=limit,
    )


@router.get("/accounts/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取科目详情"""
    service = AccountService(db)
    return await service.get_account(account_id)


@router.post("/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    data: AccountCreate,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """创建科目"""
    service = AccountService(db)
    return await service.create_account(data)


@router.put("/accounts/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int,
    data: AccountUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """更新科目"""
    service = AccountService(db)
    return await service.update_account(account_id, data)


@router.delete("/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """删除科目"""
    service = AccountService(db)
    await service.delete_account(account_id)


# ============ 付款方式相关端点 ============

@router.get("/payment-methods", response_model=List[PaymentMethodResponse])
async def get_payment_methods(
    is_active: Annotated[Optional[bool], Query(description="是否启用")] = None,
    skip: Annotated[int, Query(description="跳过条数")] = 0,
    limit: Annotated[int, Query(description="限制条数")] = 100,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取付款方式列表"""
    service = PaymentMethodService(db)
    return await service.get_payment_methods(
        is_active=is_active,
        skip=skip,
        limit=limit,
    )


@router.get("/payment-methods/{method_id}", response_model=PaymentMethodResponse)
async def get_payment_method(
    method_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取付款方式详情"""
    service = PaymentMethodService(db)
    return await service.get_payment_method(method_id)


@router.post("/payment-methods", response_model=PaymentMethodResponse, status_code=status.HTTP_201_CREATED)
async def create_payment_method(
    data: PaymentMethodCreate,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """创建付款方式"""
    service = PaymentMethodService(db)
    return await service.create_payment_method(data)


@router.put("/payment-methods/{method_id}", response_model=PaymentMethodResponse)
async def update_payment_method(
    method_id: int,
    data: PaymentMethodUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """更新付款方式"""
    service = PaymentMethodService(db)
    return await service.update_payment_method(method_id, data)


@router.delete("/payment-methods/{method_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment_method(
    method_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """删除付款方式"""
    service = PaymentMethodService(db)
    await service.delete_payment_method(method_id)


# ============ 应收账款相关端点 ============

@router.get("/receivables", response_model=List[ReceivableResponse])
async def get_receivables(
    customer_id: Annotated[Optional[int], Query(description="客户筛选")] = None,
    status: Annotated[Optional[str], Query(description="状态筛选")] = None,
    keyword: Annotated[Optional[str], Query(description="关键词搜索")] = None,
    skip: Annotated[int, Query(description="跳过条数")] = 0,
    limit: Annotated[int, Query(description="限制条数")] = 100,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取应收账款列表"""
    service = ReceivableService(db)
    return await service.get_receivables(
        customer_id=customer_id,
        status=status if status and status.strip() else None,
        keyword=keyword,
        skip=skip,
        limit=limit,
    )


@router.get("/receivables/{receivable_id}", response_model=ReceivableDetail)
async def get_receivable(
    receivable_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取应收账款详情"""
    service = ReceivableService(db)
    return await service.get_receivable(receivable_id)


@router.post("/receivables", response_model=ReceivableResponse, status_code=status.HTTP_201_CREATED)
async def create_receivable(
    data: ReceivableCreate,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """创建应收账款"""
    service = ReceivableService(db)
    return await service.create_receivable(data)


@router.put("/receivables/{receivable_id}", response_model=ReceivableResponse)
async def update_receivable(
    receivable_id: int,
    data: ReceivableUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """更新应收账款"""
    service = ReceivableService(db)
    return await service.update_receivable(receivable_id, data)


@router.delete("/receivables/{receivable_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_receivable(
    receivable_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """删除应收账款"""
    service = ReceivableService(db)
    await service.delete_receivable(receivable_id)


@router.post("/receivables/check-overdue", response_model=List[ReceivableResponse])
async def check_overdue_receivables(
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """检查逾期应收账款"""
    service = ReceivableService(db)
    return await service.check_overdue_receivables()


# ============ 应付账款相关端点 ============

@router.get("/payables", response_model=List[PayableResponse])
async def get_payables(
    supplier_id: Annotated[Optional[int], Query(description="供应商筛选")] = None,
    status: Annotated[Optional[str], Query(description="状态筛选")] = None,
    keyword: Annotated[Optional[str], Query(description="关键词搜索")] = None,
    skip: Annotated[int, Query(description="跳过条数")] = 0,
    limit: Annotated[int, Query(description="限制条数")] = 100,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取应付账款列表"""
    service = PayableService(db)
    return await service.get_payables(
        supplier_id=supplier_id,
        status=status if status and status.strip() else None,
        keyword=keyword,
        skip=skip,
        limit=limit,
    )


@router.get("/payables/{payable_id}", response_model=PayableDetail)
async def get_payable(
    payable_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取应付账款详情"""
    service = PayableService(db)
    return await service.get_payable(payable_id)


@router.post("/payables", response_model=PayableResponse, status_code=status.HTTP_201_CREATED)
async def create_payable(
    data: PayableCreate,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """创建应付账款"""
    service = PayableService(db)
    return await service.create_payable(data)


@router.put("/payables/{payable_id}", response_model=PayableResponse)
async def update_payable(
    payable_id: int,
    data: PayableUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """更新应付账款"""
    service = PayableService(db)
    return await service.update_payable(payable_id, data)


@router.delete("/payables/{payable_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payable(
    payable_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """删除应付账款"""
    service = PayableService(db)
    await service.delete_payable(payable_id)


@router.post("/payables/check-overdue", response_model=List[PayableResponse])
async def check_overdue_payables(
    current_user: Annotated[UserResponse, Depends(get_current_superuser)] = None,
    db: AsyncSession = Depends(get_db),
):
    """检查逾期应付账款"""
    service = PayableService(db)
    return await service.check_overdue_payables()


# ============ 收付款记录相关端点 ============

@router.get("/payments", response_model=List[PaymentResponse])
async def get_payments(
    payment_type: Annotated[Optional[str], Query(description="类型筛选")] = None,
    status: Annotated[Optional[str], Query(description="状态筛选")] = None,
    receivable_id: Annotated[Optional[int], Query(description="应收账款筛选")] = None,
    payable_id: Annotated[Optional[int], Query(description="应付账款筛选")] = None,
    skip: Annotated[int, Query(description="跳过条数")] = 0,
    limit: Annotated[int, Query(description="限制条数")] = 100,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取收付款记录列表"""
    service = PaymentService(db)
    return await service.get_payments(
        payment_type=payment_type if payment_type and payment_type.strip() else None,
        status=status if status and status.strip() else None,
        receivable_id=receivable_id,
        payable_id=payable_id,
        skip=skip,
        limit=limit,
    )


@router.get("/payments/{payment_id}", response_model=PaymentDetail)
async def get_payment(
    payment_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取收付款记录详情"""
    service = PaymentService(db)
    return await service.get_payment(payment_id)


@router.post("/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    data: PaymentCreate,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """创建收付款记录"""
    service = PaymentService(db)
    return await service.create_payment(data, current_user.id)


@router.put("/payments/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: int,
    data: PaymentUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """更新收付款记录"""
    service = PaymentService(db)
    return await service.update_payment(payment_id, data)


@router.post("/payments/{payment_id}/complete", response_model=PaymentResponse)
async def complete_payment(
    payment_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    完成收付款

    需要用户拥有财务操作权限
    """
    # 权限检查：只有超级管理员或具有财务权限的用户才能完成收付款
    # TODO: 实现细粒度权限检查时，应检查 "finance.complete" 权限
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要财务管理员权限才能完成收付款操作"
        )
    service = PaymentService(db)
    return await service.complete_payment(payment_id)


@router.post("/payments/{payment_id}/cancel", response_model=PaymentResponse)
async def cancel_payment(
    payment_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """取消收付款"""
    service = PaymentService(db)
    return await service.cancel_payment(payment_id)


@router.delete("/payments/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(
    payment_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """删除收付款记录"""
    service = PaymentService(db)
    await service.delete_payment(payment_id)


# ============ 财务统计端点 ============

@router.get("/summary", response_model=FinanceSummary)
async def get_finance_summary(
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取财务汇总数据"""
    service = PaymentService(db)
    return await service.get_finance_summary()
