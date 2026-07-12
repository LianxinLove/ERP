"""
报表分析服务层

@description 报表分析模块的业务逻辑
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, text

from app.models.report import (
    Report,
    ReportColumn,
    ReportParameter,
    ReportFavorite,
    Dashboard,
    DashboardWidget,
    FinancialReport,
    FinancialReportLine,
    ReportType,
    ReportCategory,
    FinancialReportType,
)


class ReportService:
    """报表服务"""

    def __init__(self, db: Session):
        self.db = db

    def create_report(
        self,
        code: str,
        name: str,
        category: ReportCategory,
        report_type: ReportType = ReportType.LIST,
        **kwargs
    ) -> Report:
        """创建报表"""
        report = Report(
            code=code,
            name=name,
            category=category,
            type=report_type,
            **kwargs
        )
        self.db.add(report)
        self.db.flush()
        return report

    def add_column(
        self,
        report_id: int,
        name: str,
        label: str,
        data_type: str,
        **kwargs
    ) -> ReportColumn:
        """添加报表列"""
        column = ReportColumn(
            report_id=report_id,
            name=name,
            label=label,
            data_type=data_type,
            **kwargs
        )
        self.db.add(column)
        self.db.flush()
        return column

    def add_parameter(
        self,
        report_id: int,
        name: str,
        label: str,
        data_type: str,
        **kwargs
    ) -> ReportParameter:
        """添加报表参数"""
        parameter = ReportParameter(
            report_id=report_id,
            name=name,
            label=label,
            data_type=data_type,
            **kwargs
        )
        self.db.add(parameter)
        self.db.flush()
        return parameter

    def execute_report(
        self,
        report_id: int,
        parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        执行报表查询

        Args:
            report_id: 报表ID
            parameters: 查询参数

        Returns:
            查询结果
        """
        report = self.db.query(Report).get(report_id)
        if not report or not report.sql_query:
            return []

        # 替换参数
        sql = report.sql_query
        if parameters:
            for key, value in parameters.items():
                placeholder = f":{key}"
                sql = sql.replace(placeholder, f"'{value}'")

        # 执行查询
        try:
            result = self.db.execute(text(sql))
            columns = result.keys()
            rows = result.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            print(f"报表执行错误: {e}")
            return []

    def get_favorite_reports(self, user_id: int) -> List[Report]:
        """获取用户收藏的报表"""
        favorite_ids = self.db.query(ReportFavorite.report_id).filter(
            ReportFavorite.user_id == user_id
        ).all()
        favorite_ids = [fid[0] for fid in favorite_ids]

        return self.db.query(Report).filter(
            and_(
                Report.id.in_(favorite_ids),
                Report.status == "active"
            )
        ).all()

    def add_favorite(self, report_id: int, user_id: int) -> ReportFavorite:
        """收藏报表"""
        favorite = ReportFavorite(
            report_id=report_id,
            user_id=user_id
        )
        self.db.add(favorite)
        self.db.flush()
        return favorite


class DashboardService:
    """业务看板服务"""

    def __init__(self, db: Session):
        self.db = db

    def create_dashboard(
        self,
        code: str,
        name: str,
        category: Optional[str] = None,
        **kwargs
    ) -> Dashboard:
        """创建看板"""
        dashboard = Dashboard(
            code=code,
            name=name,
            category=category,
            **kwargs
        )
        self.db.add(dashboard)
        self.db.flush()
        return dashboard

    def add_widget(
        self,
        dashboard_id: int,
        widget_type: str,
        title: str,
        position: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> DashboardWidget:
        """添加看板组件"""
        widget = DashboardWidget(
            dashboard_id=dashboard_id,
            widget_type=widget_type,
            title=title,
            position=position,
            **kwargs
        )
        self.db.add(widget)
        self.db.flush()
        return widget

    def get_dashboard_data(self, dashboard_id: int) -> Dict[str, Any]:
        """获取看板数据"""
        dashboard = self.db.query(Dashboard).get(dashboard_id)
        if not dashboard:
            return {}

        result = {
            "id": dashboard.id,
            "code": dashboard.code,
            "name": dashboard.name,
            "layout": dashboard.layout,
            "widgets": []
        }

        for widget in dashboard.widgets:
            widget_data = {
                "id": widget.id,
                "type": widget.widget_type,
                "title": widget.title,
                "position": widget.position,
                "config": widget.config
            }

            # 执行数据源查询
            if widget.data_source:
                try:
                    query_result = self.db.execute(text(widget.data_source))
                    columns = query_result.keys()
                    rows = query_result.fetchall()
                    widget_data["data"] = [dict(zip(columns, row)) for row in rows]
                except Exception as e:
                    widget_data["data"] = []
                    widget_data["error"] = str(e)

            result["widgets"].append(widget_data)

        return result


class FinancialReportService:
    """财务报表服务"""

    def __init__(self, db: Session):
        self.db = db

    def create_financial_report(
        self,
        code: str,
        name: str,
        report_type: FinancialReportType,
        period: str,
        start_date: date,
        end_date: date,
        **kwargs
    ) -> FinancialReport:
        """创建财务报表"""
        report = FinancialReport(
            code=code,
            name=name,
            report_type=report_type,
            period=period,
            start_date=start_date,
            end_date=end_date,
            **kwargs
        )
        self.db.add(report)
        self.db.flush()
        return report

    def generate_trial_balance(
        self,
        start_date: date,
        end_date: date,
        period: str
    ) -> FinancialReport:
        """生成科目余额表"""
        from app.models.finance import Account

        report = self.create_financial_report(
            code=f"TB_{period}",
            name=f"科目余额表 - {period}",
            report_type=FinancialReportType.TRIAL_BALANCE,
            period=period,
            start_date=start_date,
            end_date=end_date
        )

        # 获取所有科目
        accounts = self.db.query(Account).filter(
            Account.is_active == True
        ).order_by(Account.code).all()

        for account in accounts:
            # 这里应该计算期初、本期、期末余额
            # 暂时创建空行
            line = FinancialReportLine(
                report_id=report.id,
                line_no=account.code,
                account_id=account.id,
                item_code=account.code,
                item_name=account.name,
                line_type="detail",
                level=1,
                beginning_balance=Decimal("0.00"),
                current_debit=Decimal("0.00"),
                current_credit=Decimal("0.00"),
                ending_balance=Decimal("0.00")
            )
            self.db.add(line)

        self.db.flush()
        return report

    def generate_balance_sheet(
        self,
        start_date: date,
        end_date: date,
        period: str
    ) -> FinancialReport:
        """生成资产负债表"""
        report = self.create_financial_report(
            code=f"BS_{period}",
            name=f"资产负债表 - {period}",
            report_type=FinancialReportType.BALANCE_SHEET,
            period=period,
            start_date=start_date,
            end_date=end_date
        )

        # 资产部分
        asset_lines = [
            {"code": "A1", "name": "流动资产", "type": "header", "level": 1},
            {"code": "A11", "name": "货币资金", "type": "detail", "level": 2},
            {"code": "A12", "name": "应收账款", "type": "detail", "level": 2},
            {"code": "A13", "name": "存货", "type": "detail", "level": 2},
            {"code": "A2", "name": "非流动资产", "type": "header", "level": 1},
            {"code": "A21", "name": "固定资产", "type": "detail", "level": 2},
        ]

        # 负债部分
        liability_lines = [
            {"code": "L1", "name": "流动负债", "type": "header", "level": 1},
            {"code": "L11", "name": "应付账款", "type": "detail", "level": 2},
            {"code": "L12", "name": "预收账款", "type": "detail", "level": 2},
        ]

        # 所有者权益部分
        equity_lines = [
            {"code": "E1", "name": "实收资本", "type": "detail", "level": 1},
            {"code": "E2", "name": "未分配利润", "type": "detail", "level": 1},
        ]

        all_lines = asset_lines + liability_lines + equity_lines

        for line_data in all_lines:
            line = FinancialReportLine(
                report_id=report.id,
                line_no=line_data["code"],
                item_code=line_data["code"],
                item_name=line_data["name"],
                line_type=line_data["type"],
                level=line_data["level"],
                beginning_balance=Decimal("0.00"),
                ending_balance=Decimal("0.00")
            )
            self.db.add(line)

        self.db.flush()
        return report

    def generate_income_statement(
        self,
        start_date: date,
        end_date: date,
        period: str
    ) -> FinancialReport:
        """生成利润表"""
        report = self.create_financial_report(
            code=f"IS_{period}",
            name=f"利润表 - {period}",
            report_type=FinancialReportType.INCOME_STATEMENT,
            period=period,
            start_date=start_date,
            end_date=end_date
        )

        # 收入部分
        revenue_lines = [
            {"code": "R1", "name": "营业收入", "type": "detail", "level": 1},
        ]

        # 成本费用部分
        expense_lines = [
            {"code": "C1", "name": "营业成本", "type": "detail", "level": 1},
            {"code": "C2", "name": "销售费用", "type": "detail", "level": 1},
            {"code": "C3", "name": "管理费用", "type": "detail", "level": 1},
            {"code": "C4", "name": "财务费用", "type": "detail", "level": 1},
        ]

        all_lines = revenue_lines + expense_lines

        for line_data in all_lines:
            line = FinancialReportLine(
                report_id=report.id,
                line_no=line_data["code"],
                item_code=line_data["code"],
                item_name=line_data["name"],
                line_type=line_data["type"],
                level=line_data["level"],
                current_debit=Decimal("0.00"),
                current_credit=Decimal("0.00")
            )
            self.db.add(line)

        self.db.flush()
        return report


class InventoryReportService:
    """库存报表服务"""

    def __init__(self, db: Session):
        self.db = db

    def get_inventory_summary(self, warehouse_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取库存汇总"""
        from app.models.inventory import Inventory, Product

        query = self.db.query(
            Inventory.product_id,
            Product.code,
            Product.name,
            func.sum(Inventory.quantity).label("total_quantity"),
            func.sum(Inventory.quantity * Inventory.cost).label("total_value")
        ).join(Product, Inventory.product_id == Product.id)

        if warehouse_id:
            query = query.filter(Inventory.warehouse_id == warehouse_id)

        query = query.group_by(Inventory.product_id, Product.code, Product.name)

        result = query.all()
        return [
            {
                "product_id": row.product_id,
                "code": row.code,
                "name": row.name,
                "quantity": float(row.total_quantity or 0),
                "value": float(row.total_value or 0)
            }
            for row in result
        ]

    def get_inventory_turnover(
        self,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """获取库存周转分析"""
        # 这里需要计算周转率、周转天数等指标
        # 暂时返回空列表
        return []


class SalesReportService:
    """销售报表服务"""

    def __init__(self, db: Session):
        self.db = db

    def get_sales_summary(
        self,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """获取销售汇总"""
        from app.models.sales import SalesOrder

        orders = self.db.query(SalesOrder).filter(
            and_(
                SalesOrder.order_date >= start_date,
                SalesOrder.order_date <= end_date,
                SalesOrder.status != "cancelled"
            )
        ).all()

        total_amount = sum(float(order.total_amount or 0) for order in orders)
        paid_amount = sum(float(order.paid_amount or 0) for order in orders)

        return {
            "order_count": len(orders),
            "total_amount": total_amount,
            "paid_amount": paid_amount,
            "unpaid_amount": total_amount - paid_amount
        }

    def get_customer_ranking(
        self,
        start_date: date,
        end_date: date,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取客户排行"""
        from app.models.sales import SalesOrder, Customer

        result = self.db.query(
            Customer.id,
            Customer.code,
            Customer.name,
            func.sum(SalesOrder.total_amount).label("total_amount"),
            func.count(SalesOrder.id).label("order_count")
        ).join(SalesOrder, Customer.id == SalesOrder.customer_id).filter(
            and_(
                SalesOrder.order_date >= start_date,
                SalesOrder.order_date <= end_date,
                SalesOrder.status != "cancelled"
            )
        ).group_by(
            Customer.id, Customer.code, Customer.name
        ).order_by(
            func.sum(SalesOrder.total_amount).desc()
        ).limit(limit).all()

        return [
            {
                "customer_id": row.id,
                "code": row.code,
                "name": row.name,
                "total_amount": float(row.total_amount or 0),
                "order_count": row.order_count
            }
            for row in result
        ]


class PurchaseReportService:
    """采购报表服务"""

    def __init__(self, db: Session):
        self.db = db

    def get_purchase_summary(
        self,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """获取采购汇总"""
        from app.models.purchase import PurchaseOrder

        orders = self.db.query(PurchaseOrder).filter(
            and_(
                PurchaseOrder.order_date >= start_date,
                PurchaseOrder.order_date <= end_date,
                PurchaseOrder.status != "cancelled"
            )
        ).all()

        total_amount = sum(float(order.total_amount or 0) for order in orders)

        return {
            "order_count": len(orders),
            "total_amount": total_amount
        }

    def get_supplier_ranking(
        self,
        start_date: date,
        end_date: date,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取供应商排行"""
        from app.models.purchase import PurchaseOrder, Supplier

        result = self.db.query(
            Supplier.id,
            Supplier.code,
            Supplier.name,
            func.sum(PurchaseOrder.total_amount).label("total_amount"),
            func.count(PurchaseOrder.id).label("order_count")
        ).join(PurchaseOrder, Supplier.id == PurchaseOrder.supplier_id).filter(
            and_(
                PurchaseOrder.order_date >= start_date,
                PurchaseOrder.order_date <= end_date,
                PurchaseOrder.status != "cancelled"
            )
        ).group_by(
            Supplier.id, Supplier.code, Supplier.name
        ).order_by(
            func.sum(PurchaseOrder.total_amount).desc()
        ).limit(limit).all()

        return [
            {
                "supplier_id": row.id,
                "code": row.code,
                "name": row.name,
                "total_amount": float(row.total_amount or 0),
                "order_count": row.order_count
            }
            for row in result
        ]
