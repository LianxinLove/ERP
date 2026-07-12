"""
报表分析模块的数据模式定义
"""

from datetime import datetime, date
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ReportType(str, Enum):
    """报表类型"""
    LIST = "list"
    SUMMARY = "summary"
    CROSS_TAB = "cross_tab"
    CHART = "chart"
    FINANCIAL = "financial"


class ReportCategory(str, Enum):
    """报表分类"""
    INVENTORY = "inventory"
    SALES = "sales"
    PURCHASE = "purchase"
    FINANCE = "finance"
    PRODUCTION = "production"
    QUALITY = "quality"
    CUSTOM = "custom"


class ReportStatus(str, Enum):
    """报表状态"""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class FinancialReportType(str, Enum):
    """财务报表类型"""
    BALANCE_SHEET = "balance_sheet"
    INCOME_STATEMENT = "income_statement"
    CASH_FLOW = "cash_flow"
    TRIAL_BALANCE = "trial_balance"


# ========== 自定义报表相关 ==========

class ReportBase(BaseModel):
    """报表基础信息"""
    code: str = Field(..., description="报表编码")
    name: str = Field(..., description="报表名称")
    category: ReportCategory = Field(..., description="报表分类")
    report_type: ReportType = Field(default=ReportType.LIST, description="报表类型")


class ReportCreate(ReportBase):
    """创建报表请求"""
    description: Optional[str] = Field(None, description="描述")
    is_public: bool = Field(default=False, description="是否公开")


class ReportResponse(ReportBase):
    """报表响应"""
    id: int
    description: Optional[str] = None
    data_source: Optional[str] = None
    sql_query: Optional[str] = None
    is_public: bool
    status: ReportStatus
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReportExecuteRequest(BaseModel):
    """执行报表请求"""
    parameters: Optional[Dict[str, Any]] = Field(None, description="查询参数")


# ========== 业务看板相关 ==========

class DashboardBase(BaseModel):
    """看板基础信息"""
    code: str = Field(..., description="看板编码")
    name: str = Field(..., description="看板名称")


class DashboardCreate(DashboardBase):
    """创建看板请求"""
    category: Optional[str] = Field(None, description="分类")


class DashboardResponse(DashboardBase):
    """看板响应"""
    id: int
    category: Optional[str] = None
    description: Optional[str] = None
    is_public: bool
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== 财务报表相关 ==========

class FinancialReportBase(BaseModel):
    """财务报表基础信息"""
    code: str = Field(..., description="报表编码")
    name: str = Field(..., description="报表名称")
    report_type: FinancialReportType = Field(..., description="报表类型")
    period: str = Field(..., description="期间")
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")


class FinancialReportCreate(FinancialReportBase):
    """创建财务报表请求"""
    pass


class FinancialReportLineResponse(BaseModel):
    """财务报表行响应"""
    id: int
    line_no: str
    account_id: Optional[int] = None
    item_code: str
    item_name: str
    line_type: str
    level: int
    parent_line_no: Optional[str] = None
    beginning_balance: Optional[float] = None
    current_debit: Optional[float] = None
    current_credit: Optional[float] = None
    ending_balance: Optional[float] = None

    class Config:
        from_attributes = True


class FinancialReportResponse(FinancialReportBase):
    """财务报表响应"""
    id: int
    status: str
    generated_by: Optional[int] = None
    generated_at: Optional[datetime] = None
    created_at: datetime
    lines: list[FinancialReportLineResponse] = []

    class Config:
        from_attributes = True
