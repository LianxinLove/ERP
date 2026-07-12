"""
销售管理 API 端点

@description 销售模块的 API 接口

@endpoints
- 客户管理
- 销售订单管理
- 销售退货管理
- 发货单管理
"""

from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_current_superuser, get_db
from app.schemas.user import UserResponse
from app.schemas.sales import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    SalesOrderCreate,
    SalesOrderUpdate,
    SalesOrderResponse,
    SalesOrderDetail,
    SalesReturnCreate,
    SalesReturnUpdate,
    SalesReturnResponse,
    SalesReturnDetail,
    DeliveryOrderCreate,
    DeliveryOrderUpdate,
    DeliveryOrderResponse,
    DeliveryOrderDetail,
    DeliveryOrderShip,
    DeliveryOrderReceive,
)
from app.services.sales import (
    CustomerService,
    SalesOrderService,
    SalesReturnService,
    DeliveryOrderService,
)

router = APIRouter()


# ============ 客户相关端点 ============

@router.get("/customers", response_model=List[CustomerResponse])
async def get_customers(
    status: Annotated[Optional[str], Query(description="状态筛选")] = None,
    keyword: Annotated[Optional[str], Query(description="关键词搜索")] = None,
    skip: Annotated[int, Query(description="跳过条数")] = 0,
    limit: Annotated[int, Query(description="限制条数")] = 100,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取客户列表"""
    service = CustomerService(db)
    return await service.get_customers(status=status, keyword=keyword, skip=skip, limit=limit)


@router.get("/customers/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取客户详情"""
    service = CustomerService(db)
    return await service.get_customer(customer_id)


@router.post("/customers", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    data: CustomerCreate,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """创建客户"""
    service = CustomerService(db)
    return await service.create_customer(data)


@router.put("/customers/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    data: CustomerUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """更新客户"""
    service = CustomerService(db)
    return await service.update_customer(customer_id, data)


@router.delete("/customers/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """删除客户"""
    service = CustomerService(db)
    await service.delete_customer(customer_id)


# ============ 销售订单相关端点 ============

@router.get("/orders", response_model=List[SalesOrderResponse])
async def get_sales_orders(
    customer_id: Annotated[Optional[int], Query(description="客户筛选")] = None,
    status: Annotated[Optional[str], Query(description="状态筛选")] = None,
    keyword: Annotated[Optional[str], Query(description="关键词搜索")] = None,
    skip: Annotated[int, Query(description="跳过条数")] = 0,
    limit: Annotated[int, Query(description="限制条数")] = 100,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取销售订单列表"""
    service = SalesOrderService(db)
    return await service.get_orders(
        customer_id=customer_id,
        status=status,
        keyword=keyword,
        skip=skip,
        limit=limit,
    )


@router.get("/orders/{order_id}", response_model=SalesOrderDetail)
async def get_sales_order(
    order_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取销售订单详情"""
    service = SalesOrderService(db)
    return await service.get_order(order_id)


@router.post("/orders", response_model=SalesOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_sales_order(
    data: SalesOrderCreate,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """创建销售订单"""
    service = SalesOrderService(db)
    return await service.create_order(data)


@router.put("/orders/{order_id}", response_model=SalesOrderResponse)
async def update_sales_order(
    order_id: int,
    data: SalesOrderUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """更新销售订单"""
    service = SalesOrderService(db)
    return await service.update_order(order_id, data)


@router.post("/orders/{order_id}/confirm", response_model=SalesOrderResponse)
async def confirm_sales_order(
    order_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    确认销售订单

    需要用户拥有销售管理权限
    """
    # 权限检查：只有超级管理员或具有销售管理权限的用户才能确认订单
    # TODO: 实现细粒度权限检查时，应检查 "sales.order.confirm" 权限
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要销售管理员权限才能确认销售订单"
        )
    service = SalesOrderService(db)
    return await service.confirm_order(order_id)


@router.post("/orders/{order_id}/cancel", response_model=SalesOrderResponse)
async def cancel_sales_order(
    order_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    取消销售订单

    需要用户拥有销售管理权限
    """
    # 权限检查：只有超级管理员或具有销售管理权限的用户才能取消订单
    # TODO: 实现细粒度权限检查时，应检查 "sales.order.cancel" 权限
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要销售管理员权限才能取消销售订单"
        )
    service = SalesOrderService(db)
    return await service.cancel_order(order_id)


@router.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sales_order(
    order_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """删除销售订单"""
    service = SalesOrderService(db)
    await service.delete_order(order_id)


# ============ 销售退货相关端点 ============

@router.get("/returns", response_model=List[SalesReturnResponse])
async def get_sales_returns(
    customer_id: Annotated[Optional[int], Query(description="客户筛选")] = None,
    status: Annotated[Optional[str], Query(description="状态筛选")] = None,
    keyword: Annotated[Optional[str], Query(description="关键词搜索")] = None,
    skip: Annotated[int, Query(description="跳过条数")] = 0,
    limit: Annotated[int, Query(description="限制条数")] = 100,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取销售退货列表"""
    service = SalesReturnService(db)
    return await service.get_returns(
        customer_id=customer_id,
        status=status,
        keyword=keyword,
        skip=skip,
        limit=limit,
    )


@router.get("/returns/{return_id}", response_model=SalesReturnDetail)
async def get_sales_return(
    return_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取销售退货详情"""
    service = SalesReturnService(db)
    return await service.get_return(return_id)


@router.post("/returns", response_model=SalesReturnResponse, status_code=status.HTTP_201_CREATED)
async def create_sales_return(
    data: SalesReturnCreate,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """创建销售退货"""
    service = SalesReturnService(db)
    return await service.create_return(data)


@router.delete("/returns/{return_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sales_return(
    return_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """删除销售退货"""
    service = SalesReturnService(db)
    await service.delete_return(return_id)


# ============ 发货单相关端点 ============

@router.get("/deliveries", response_model=List[DeliveryOrderResponse])
async def get_delivery_orders(
    customer_id: Annotated[Optional[int], Query(description="客户筛选")] = None,
    order_id: Annotated[Optional[int], Query(description="订单筛选")] = None,
    status: Annotated[Optional[str], Query(description="状态筛选")] = None,
    keyword: Annotated[Optional[str], Query(description="关键词搜索")] = None,
    skip: Annotated[int, Query(description="跳过条数")] = 0,
    limit: Annotated[int, Query(description="限制条数")] = 100,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取发货单列表"""
    service = DeliveryOrderService(db)
    return await service.get_deliveries(
        customer_id=customer_id,
        order_id=order_id,
        status=status,
        keyword=keyword,
        skip=skip,
        limit=limit,
    )


@router.get("/deliveries/{delivery_id}", response_model=DeliveryOrderDetail)
async def get_delivery_order(
    delivery_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取发货单详情"""
    service = DeliveryOrderService(db)
    return await service.get_delivery(delivery_id)


@router.post("/deliveries", response_model=DeliveryOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_delivery_order(
    data: DeliveryOrderCreate,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """创建发货单"""
    service = DeliveryOrderService(db)
    return await service.create_delivery(data)


@router.post("/deliveries/{delivery_id}/ship", response_model=DeliveryOrderResponse)
async def ship_delivery_order(
    delivery_id: int,
    data: DeliveryOrderShip,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """确认发货"""
    service = DeliveryOrderService(db)
    return await service.ship_delivery(delivery_id, data)


@router.post("/deliveries/{delivery_id}/receive", response_model=DeliveryOrderResponse)
async def receive_delivery_order(
    delivery_id: int,
    data: DeliveryOrderReceive,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """确认签收"""
    service = DeliveryOrderService(db)
    return await service.receive_delivery(delivery_id, data)


@router.post("/deliveries/{delivery_id}/cancel", response_model=DeliveryOrderResponse)
async def cancel_delivery_order(
    delivery_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_db),
):
    """取消发货单"""
    service = DeliveryOrderService(db)
    return await service.cancel_delivery(delivery_id)
