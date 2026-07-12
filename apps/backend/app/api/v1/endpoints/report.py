"""
报表分析API端点
"""

from datetime import datetime, date
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.core.permissions import require_permission
from app.models.user import User
from app.services.report import (
    ReportService,
    DashboardService,
    FinancialReportService,
    InventoryReportService,
    SalesReportService,
    PurchaseReportService,
)
from app.schemas.report import (
    ReportCreate,
    ReportResponse,
    ReportExecuteRequest,
    DashboardCreate,
    DashboardResponse,
    FinancialReportCreate,
    FinancialReportResponse,
)

router = APIRouter(prefix="/reports", tags=["报表分析"])


# ========== 自定义报表相关 ==========

@router.post("/", summary="创建报表")
@require_permission("report.create")
async def create_report(
    data: ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建自定义报表"""
    service = ReportService(db)
    report = service.create_report(
        code=data.code,
        name=data.name,
        category=data.category,
        report_type=data.report_type,
        description=data.description,
        is_public=data.is_public,
        created_by=current_user.id,
    )
    return {"id": report.id, "message": "报表创建成功"}


@router.post("/{report_id}/execute", summary="执行报表")
@require_permission("report.execute")
async def execute_report(
    report_id: int,
    data: ReportExecuteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """执行报表查询"""
    service = ReportService(db)
    result = service.execute_report(report_id, data.parameters)
    return {"data": result}


@router.get("/favorites", summary="获取收藏报表")
@require_permission("report.read")
async def get_favorite_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取用户收藏的报表"""
    service = ReportService(db)
    reports = service.get_favorite_reports(current_user.id)
    return {"items": [ReportResponse.model_validate(r) for r in reports]}


@router.post("/{report_id}/favorite", summary="收藏报表")
@require_permission("report.favorite")
async def favorite_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """收藏报表"""
    service = ReportService(db)
    favorite = service.add_favorite(report_id, current_user.id)
    return {"message": "报表已收藏"}


# ========== 业务看板相关 ==========

@router.post("/dashboards", summary="创建看板")
@require_permission("dashboard.create")
async def create_dashboard(
    code: str = Query(..., description="看板编码"),
    name: str = Query(..., description="看板名称"),
    category: Optional[str] = Query(None, description="分类"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建业务看板"""
    service = DashboardService(db)
    dashboard = service.create_dashboard(
        code=code,
        name=name,
        category=category,
        created_by=current_user.id,
    )
    return {"id": dashboard.id, "message": "看板创建成功"}


@router.get("/dashboards/{dashboard_id}/data", summary="获取看板数据")
@require_permission("dashboard.read")
async def get_dashboard_data(
    dashboard_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取看板数据"""
    service = DashboardService(db)
    data = service.get_dashboard_data(dashboard_id)
    return data


# ========== 财务报表相关 ==========

@router.post("/financial", summary="生成财务报表")
@require_permission("report.financial.create")
async def create_financial_report(
    data: FinancialReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """生成财务报表"""
    service = FinancialReportService(db)

    if data.report_type == "trial_balance":
        report = service.generate_trial_balance(
            start_date=data.start_date,
            end_date=data.end_date,
            period=data.period,
        )
    elif data.report_type == "balance_sheet":
        report = service.generate_balance_sheet(
            start_date=data.start_date,
            end_date=data.end_date,
            period=data.period,
        )
    elif data.report_type == "income_statement":
        report = service.generate_income_statement(
            start_date=data.start_date,
            end_date=data.end_date,
            period=data.period,
        )
    else:
        raise HTTPException(status_code=400, detail="不支持的报表类型")

    return FinancialReportResponse.model_validate(report)


@router.get("/financial/{report_id}", summary="获取财务报表")
@require_permission("report.financial.read")
async def get_financial_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取财务报表详情"""
    from app.models.report import FinancialReport

    report = db.query(FinancialReport).get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="报表不存在")

    return FinancialReportResponse.model_validate(report)


# ========== 库存报表相关 ==========

@router.get("/inventory/summary", summary="库存汇总报表")
@require_permission("report.inventory.read")
async def get_inventory_summary(
    warehouse_id: Optional[int] = Query(None, description="仓库ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取库存汇总报表"""
    service = InventoryReportService(db)
    data = service.get_inventory_summary(warehouse_id)
    return {"data": data}


@router.get("/inventory/turnover", summary="库存周转分析")
@require_permission("report.inventory.read")
async def get_inventory_turnover(
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取库存周转分析"""
    service = InventoryReportService(db)
    data = service.get_inventory_turnover(start_date, end_date)
    return {"data": data}


# ========== 销售报表相关 ==========

@router.get("/sales/summary", summary="销售汇总报表")
@require_permission("report.sales.read")
async def get_sales_summary(
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取销售汇总报表"""
    service = SalesReportService(db)
    data = service.get_sales_summary(start_date, end_date)
    return data


@router.get("/sales/customer-ranking", summary="客户排行报表")
@require_permission("report.sales.read")
async def get_customer_ranking(
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    limit: int = Query(10, ge=1, le=100, description="返回数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取客户排行"""
    service = SalesReportService(db)
    data = service.get_customer_ranking(start_date, end_date, limit)
    return {"data": data}


# ========== 采购报表相关 ==========

@router.get("/purchase/summary", summary="采购汇总报表")
@require_permission("report.purchase.read")
async def get_purchase_summary(
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取采购汇总报表"""
    service = PurchaseReportService(db)
    data = service.get_purchase_summary(start_date, end_date)
    return data


@router.get("/purchase/supplier-ranking", summary="供应商排行报表")
@require_permission("report.purchase.read")
async def get_supplier_ranking(
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    limit: int = Query(10, ge=1, le=100, description="返回数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取供应商排行"""
    service = PurchaseReportService(db)
    data = service.get_supplier_ranking(start_date, end_date, limit)
    return {"data": data}
