"""
生产管理API端点
"""

from datetime import datetime
from typing import Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.core.permissions import require_permission
from app.models.user import User
from app.services.production import (
    BOMService,
    ProductionOrderService,
    WorkOrderService,
    WorkCenterService,
    ProductionProcessService,
)
from app.schemas.production import (
    BOMCreate,
    BOMResponse,
    BOMItemCreate,
    ProductionOrderCreate,
    ProductionOrderResponse,
    WorkOrderCreate,
    WorkOrderResponse,
    WorkCenterCreate,
    WorkCenterResponse,
    BOMCostResponse,
)

router = APIRouter(prefix="/production", tags=["生产制造"])


# ========== BOM相关 ==========

@router.post("/boms", summary="创建BOM")
@require_permission("production.bom.create")
async def create_bom(
    data: BOMCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建物料清单"""
    service = BOMService(db)
    bom = service.create_bom(
        product_id=data.product_id,
        product_code=data.product_code,
        product_name=data.product_name,
        version=data.version,
        base_quantity=data.base_quantity,
        description=data.description,
    )
    return {"id": bom.id, "message": "BOM创建成功"}


@router.post("/boms/{bom_id}/items", summary="添加BOM明细")
@require_permission("production.bom.create")
async def add_bom_item(
    bom_id: int,
    data: BOMItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """添加BOM明细"""
    service = BOMService(db)
    item = service.add_bom_item(
        bom_id=bom_id,
        line_no=data.line_no,
        component_code=data.component_code,
        component_name=data.component_name,
        quantity=data.quantity,
        item_type=data.item_type,
        unit=data.unit,
        scrap_rate=data.scrap_rate,
    )
    return {"id": item.id, "message": "BOM明细添加成功"}


@router.get("/boms/product/{product_id}", summary="获取产品BOM")
@require_permission("production.bom.read")
async def get_product_bom(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取产品的生效BOM"""
    service = BOMService(db)
    bom = service.get_bom_by_product(product_id)
    if not bom:
        raise HTTPException(status_code=404, detail="BOM不存在")

    return BOMResponse.model_validate(bom)


@router.get("/boms/{bom_id}/cost", summary="计算BOM成本")
@require_permission("production.bom.read")
async def calculate_bom_cost(
    bom_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """计算BOM成本"""
    service = BOMService(db)
    cost = service.calculate_bom_cost(bom_id)
    if not cost:
        raise HTTPException(status_code=404, detail="BOM不存在")
    return BOMCostResponse(**cost)


@router.put("/boms/{bom_id}/activate", summary="激活BOM")
@require_permission("production.bom.update")
async def activate_bom(
    bom_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """激活BOM"""
    service = BOMService(db)
    bom = service.activate_bom(bom_id)
    if not bom:
        raise HTTPException(status_code=404, detail="BOM不存在")
    return {"message": "BOM已激活"}


# ========== 生产订单相关 ==========

@router.post("/orders", summary="创建生产订单")
@require_permission("production.order.create")
async def create_production_order(
    data: ProductionOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建生产订单"""
    service = ProductionOrderService(db)
    order = service.create_production_order(
        order_no=data.order_no,
        product_id=data.product_id,
        product_code=data.product_code,
        product_name=data.product_name,
        quantity=data.quantity,
        bom_id=data.bom_id,
        plan_start_date=data.plan_start_date,
        plan_end_date=data.plan_end_date,
        warehouse_id=data.warehouse_id,
        sales_order_id=data.sales_order_id,
        priority=data.priority,
        notes=data.notes,
    )
    return {"id": order.id, "order_no": order.order_no, "message": "生产订单创建成功"}


@router.put("/orders/{order_id}/release", summary="下达生产订单")
@require_permission("production.order.update")
async def release_production_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """下达生产订单"""
    service = ProductionOrderService(db)
    order = service.release_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="生产订单不存在")
    return {"message": "生产订单已下达"}


@router.put("/orders/{order_id}/complete", summary="完成生产订单")
@require_permission("production.order.update")
async def complete_production_order(
    order_id: int,
    qualified_quantity: Decimal = Query(..., description="合格数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """完成生产订单"""
    service = ProductionOrderService(db)
    order = service.complete_order(order_id, qualified_quantity)
    if not order:
        raise HTTPException(status_code=404, detail="生产订单不存在")
    return {"message": "生产订单已完成"}


@router.get("/orders", summary="获取生产订单列表")
@require_permission("production.order.read")
async def get_production_orders(
    status: Optional[str] = Query(None, description="状态"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取生产订单列表"""
    from app.models.production import ProductionOrder

    query = db.query(ProductionOrder)

    if status:
        query = query.filter(ProductionOrder.status == status)

    total = query.count()
    orders = query.order_by(ProductionOrder.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    return {
        "items": [ProductionOrderResponse.model_validate(order) for order in orders],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


# ========== 派工单相关 ==========

@router.post("/work-orders", summary="创建派工单")
@require_permission("production.work_order.create")
async def create_work_order(
    data: WorkOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建派工单"""
    service = WorkOrderService(db)
    work_order = service.create_work_order(
        work_no=data.work_no,
        production_order_id=data.production_order_id,
        process_id=data.process_id,
        quantity=data.quantity,
        work_center_id=data.work_center_id,
        worker_id=data.worker_id,
        plan_start_time=data.plan_start_time,
        plan_end_time=data.plan_end_time,
    )
    return {"id": work_order.id, "work_no": work_order.work_no, "message": "派工单创建成功"}


@router.put("/work-orders/{work_order_id}/start", summary="开始加工")
@require_permission("production.work_order.update")
async def start_work(
    work_order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """开始加工"""
    service = WorkOrderService(db)
    work_order = service.start_work(work_order_id)
    if not work_order:
        raise HTTPException(status_code=404, detail="派工单不存在")
    return {"message": "加工已开始"}


@router.put("/work-orders/{work_order_id}/complete", summary="完成加工")
@require_permission("production.work_order.update")
async def complete_work(
    work_order_id: int,
    qualified_quantity: Decimal = Query(..., description="合格数量"),
    rejected_quantity: Decimal = Query(0, description="不合格数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """完成加工"""
    service = WorkOrderService(db)
    work_order = service.complete_work(work_order_id, qualified_quantity, rejected_quantity)
    if not work_order:
        raise HTTPException(status_code=404, detail="派工单不存在")
    return {"message": "加工已完成"}


# ========== 工作中心相关 ==========

@router.post("/work-centers", summary="创建工作中心")
@require_permission("production.work_center.create")
async def create_work_center(
    data: WorkCenterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建工作中心"""
    service = WorkCenterService(db)
    work_center = service.create_work_center(
        code=data.code,
        name=data.name,
        capacity=data.capacity,
        efficiency=data.efficiency,
        cost_per_hour=data.cost_per_hour,
        description=data.description,
    )
    return {"id": work_center.id, "message": "工作中心创建成功"}


@router.get("/work-centers/{work_center_id}/load", summary="获取工作中心负荷")
@require_permission("production.work_center.read")
async def get_work_center_load(
    work_center_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取工作中心负荷"""
    service = WorkCenterService(db)
    load = service.get_work_center_load(work_center_id)
    return load


@router.get("/work-centers", summary="获取工作中心列表")
@require_permission("production.work_center.read")
async def get_work_centers(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取工作中心列表"""
    from app.models.production import WorkCenter

    query = db.query(WorkCenter).filter(WorkCenter.is_active == True)

    total = query.count()
    work_centers = query.order_by(WorkCenter.code).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    return {
        "items": [WorkCenterResponse.model_validate(wc) for wc in work_centers],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


# ========== 工序相关 ==========

@router.post("/processes", summary="创建工序")
@require_permission("production.process.create")
async def create_process(
    code: str = Query(..., description="工序编码"),
    name: str = Query(..., description="工序名称"),
    work_center_id: Optional[int] = Query(None, description="工作中心ID"),
    standard_hours: Optional[Decimal] = Query(None, description="标准工时"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建工序"""
    service = ProductionProcessService(db)
    process = service.create_process(
        code=code,
        name=name,
        work_center_id=work_center_id,
        standard_hours=standard_hours,
    )
    return {"id": process.id, "message": "工序创建成功"}
