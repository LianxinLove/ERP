"""
质量管理API端点
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
from app.services.quality import (
    InspectionSchemeService,
    IncomingInspectionService,
    ProcessInspectionService,
    OutgoingInspectionService,
    QualityTraceService,
)
from app.schemas.quality import (
    InspectionSchemeCreate,
    InspectionSchemeResponse,
    IncomingInspectionCreate,
    IncomingInspectionResponse,
    InspectionResultCreate,
    ProcessInspectionCreate,
    ProcessInspectionResponse,
    OutgoingInspectionCreate,
    OutgoingInspectionResponse,
    QualityTraceCreate,
    QualityTraceResponse,
)

router = APIRouter(prefix="/quality", tags=["质量管理"])


# ========== 质检方案相关 ==========

@router.post("/schemes", summary="创建质检方案")
@require_permission("quality.scheme.create")
async def create_inspection_scheme(
    data: InspectionSchemeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建质检方案"""
    service = InspectionSchemeService(db)
    scheme = service.create_scheme(
        code=data.code,
        name=data.name,
        inspection_type=data.inspection_type,
        sampling_plan_id=data.sampling_plan_id,
        description=data.description,
    )
    return {"id": scheme.id, "message": "质检方案创建成功"}


@router.get("/schemes/default", summary="获取默认质检方案")
@require_permission("quality.scheme.read")
async def get_default_scheme(
    inspection_type: str = Query(..., description="检验类型"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取指定类型的默认质检方案"""
    service = InspectionSchemeService(db)
    scheme = service.get_default_scheme(inspection_type)
    if not scheme:
        raise HTTPException(status_code=404, detail="未找到默认质检方案")
    return InspectionSchemeResponse.model_validate(scheme)


# ========== 来料检验相关 ==========

@router.post("/incoming", summary="创建来料检验单")
@require_permission("quality.inspection.create")
async def create_incoming_inspection(
    data: IncomingInspectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建来料检验单"""
    service = IncomingInspectionService(db)
    inspection = service.create_inspection(
        inspection_no=data.inspection_no,
        supplier_id=data.supplier_id,
        product_id=data.product_id,
        quantity=data.quantity,
        purchase_order_id=data.purchase_order_id,
        receipt_id=data.receipt_id,
        batch_no=data.batch_no,
    )
    return {"id": inspection.id, "inspection_no": inspection.inspection_no, "message": "来料检验单创建成功"}


@router.put("/incoming/{inspection_id}/start", summary="开始检验")
@require_permission("quality.inspection.update")
async def start_incoming_inspection(
    inspection_id: int,
    inspector_id: int = Query(..., description="检验员ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """开始来料检验"""
    service = IncomingInspectionService(db)
    inspection = service.start_inspection(inspection_id, inspector_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="检验单不存在")
    return {"message": "检验已开始"}


@router.post("/incoming/{inspection_id}/results", summary="添加检验结果")
@require_permission("quality.inspection.update")
async def add_inspeection_result(
    inspection_id: int,
    data: InspectionResultCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """添加检验结果"""
    service = IncomingInspectionService(db)
    item = service.add_inspection_result(
        inspection_id=inspection_id,
        item_id=data.item_id,
        item_name=data.item_name,
        measured_value=data.measured_value,
        is_qualified=data.is_qualified,
        defect_level=data.defect_level,
    )
    return {"id": item.id, "message": "检验结果已添加"}


@router.put("/incoming/{inspection_id}/complete", summary="完成检验")
@require_permission("quality.inspection.update")
async def complete_incoming_inspection(
    inspection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """完成来料检验"""
    service = IncomingInspectionService(db)
    inspection = service.complete_inspection(inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="检验单不存在")
    return {
        "message": "检验已完成",
        "result": inspection.inspection_result,
        "qualified_quantity": float(inspection.qualified_quantity),
        "rejected_quantity": float(inspection.rejected_quantity),
    }


@router.get("/incoming", summary="获取来料检验列表")
@require_permission("quality.inspection.read")
async def get_incoming_inspections(
    status: Optional[str] = Query(None, description="状态"),
    supplier_id: Optional[int] = Query(None, description="供应商ID"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取来料检验列表"""
    from app.models.quality import IncomingInspection

    query = db.query(IncomingInspection)

    if status:
        query = query.filter(IncomingInspection.status == status)
    if supplier_id:
        query = query.filter(IncomingInspection.supplier_id == supplier_id)

    total = query.count()
    inspections = query.order_by(IncomingInspection.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    return {
        "items": [IncomingInspectionResponse.model_validate(i) for i in inspections],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


# ========== 过程检验相关 ==========

@router.post("/process", summary="创建过程检验单")
@require_permission("quality.inspection.create")
async def create_process_inspection(
    data: ProcessInspectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建过程检验单"""
    service = ProcessInspectionService(db)
    inspection = service.create_inspection(
        inspection_no=data.inspection_no,
        product_id=data.product_id,
        quantity=data.quantity,
        production_order_id=data.production_order_id,
        work_order_id=data.work_order_id,
        process_id=data.process_id,
        batch_no=data.batch_no,
    )
    return {"id": inspection.id, "inspection_no": inspection.inspection_no, "message": "过程检验单创建成功"}


@router.put("/process/{inspection_id}/complete", summary="完成过程检验")
@require_permission("quality.inspection.update")
async def complete_process_inspection(
    inspection_id: int,
    inspector_id: int = Query(..., description="检验员ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """完成过程检验"""
    service = ProcessInspectionService(db)
    inspection = service.complete_inspection(inspection_id, inspector_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="检验单不存在")
    return {
        "message": "检验已完成",
        "result": inspection.inspection_result,
        "qualified_quantity": float(inspection.qualified_quantity),
        "rejected_quantity": float(inspection.rejected_quantity),
    }


# ========== 出货检验相关 ==========

@router.post("/outgoing", summary="创建出货检验单")
@require_permission("quality.inspection.create")
async def create_outgoing_inspection(
    data: OutgoingInspectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建出货检验单"""
    service = OutgoingInspectionService(db)
    inspection = service.create_inspection(
        inspection_no=data.inspection_no,
        customer_id=data.customer_id,
        product_id=data.product_id,
        quantity=data.quantity,
        delivery_order_id=data.delivery_order_id,
        sales_order_id=data.sales_order_id,
        batch_no=data.batch_no,
    )
    return {"id": inspection.id, "inspection_no": inspection.inspection_no, "message": "出货检验单创建成功"}


@router.put("/outgoing/{inspection_id}/complete", summary="完成出货检验")
@require_permission("quality.inspection.update")
async def complete_outgoing_inspection(
    inspection_id: int,
    inspector_id: int = Query(..., description="检验员ID"),
    certificate_no: Optional[str] = Query(None, description="合格证编号"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """完成出货检验"""
    service = OutgoingInspectionService(db)
    inspection = service.complete_inspection(inspection_id, inspector_id, certificate_no)
    if not inspection:
        raise HTTPException(status_code=404, detail="检验单不存在")
    return {
        "message": "检验已完成",
        "result": inspection.inspection_result,
        "qualified_quantity": float(inspection.qualified_quantity),
        "rejected_quantity": float(inspection.rejected_quantity),
        "certificate_no": inspection.certificate_no,
    }


@router.get("/outgoing", summary="获取出货检验列表")
@require_permission("quality.inspection.read")
async def get_outgoing_inspections(
    status: Optional[str] = Query(None, description="状态"),
    customer_id: Optional[int] = Query(None, description="客户ID"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取出货检验列表"""
    from app.models.quality import OutgoingInspection

    query = db.query(OutgoingInspection)

    if status:
        query = query.filter(OutgoingInspection.status == status)
    if customer_id:
        query = query.filter(OutgoingInspection.customer_id == customer_id)

    total = query.count()
    inspections = query.order_by(OutgoingInspection.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    return {
        "items": [OutgoingInspectionResponse.model_validate(i) for i in inspections],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


# ========== 质量追溯相关 ==========

@router.post("/trace", summary="创建质量追溯记录")
@require_permission("quality.trace.create")
async def create_quality_trace(
    data: QualityTraceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建质量追溯记录"""
    service = QualityTraceService(db)
    trace = service.create_trace(
        product_id=data.product_id,
        batch_no=data.batch_no,
        serial_no=data.serial_no,
    )
    return {"id": trace.id, "message": "质量追溯记录创建成功"}


@router.get("/trace/batch/{batch_no}", summary="根据批号追溯")
@require_permission("quality.trace.read")
async def get_trace_by_batch(
    batch_no: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """根据批号查询质量追溯记录"""
    service = QualityTraceService(db)
    traces = service.get_trace_by_batch(batch_no)
    return {
        "batch_no": batch_no,
        "traces": [QualityTraceResponse.model_validate(t) for t in traces],
    }


@router.get("/trace/serial/{serial_no}", summary="根据序列号追溯")
@require_permission("quality.trace.read")
async def get_trace_by_serial(
    serial_no: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """根据序列号查询质量追溯记录"""
    service = QualityTraceService(db)
    trace = service.get_trace_by_serial(serial_no)
    if not trace:
        raise HTTPException(status_code=404, detail="未找到追溯记录")
    return QualityTraceResponse.model_validate(trace)


@router.get("/trace/product/{product_id}/history", summary="产品质量历史")
@require_permission("quality.trace.read")
async def get_product_quality_history(
    product_id: int,
    limit: int = Query(50, ge=1, le=200, description="返回数量限制"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取产品质量历史"""
    service = QualityTraceService(db)
    traces = service.get_product_quality_history(product_id, limit)
    return {
        "product_id": product_id,
        "history": [QualityTraceResponse.model_validate(t) for t in traces],
    }
