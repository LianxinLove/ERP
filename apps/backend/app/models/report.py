"""
报表分析数据模型

@description 报表分析模块，包含报表设计器、业务看板、标准报表、财务报表

@models
- Report: 报表定义
- ReportColumn: 报表列定义
- ReportParameter: 报表参数
- ReportFavorite: 报表收藏
- Dashboard: 业务看板
- DashboardWidget: 看板组件
- FinancialReport: 财务报表
- FinancialReportLine: 财务报表行
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, Boolean, JSON, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class ReportType(str, enum.Enum):
    """报表类型"""
    LIST = "list"  # 列表报表
    SUMMARY = "summary"  # 汇总报表
    CROSS_TAB = "cross_tab"  # 交叉表
    CHART = "chart"  # 图表
    FINANCIAL = "financial"  # 财务报表


class ReportCategory(str, enum.Enum):
    """报表分类"""
    INVENTORY = "inventory"  # 库存报表
    SALES = "sales"  # 销售报表
    PURCHASE = "purchase"  # 采购报表
    FINANCE = "finance"  # 财务报表
    PRODUCTION = "production"  # 生产报表
    QUALITY = "quality"  # 质量报表
    CUSTOM = "custom"  # 自定义报表


class ReportStatus(str, enum.Enum):
    """报表状态"""
    DRAFT = "draft"  # 草稿
    ACTIVE = "active"  # 启用
    ARCHIVED = "archived"  # 归档


class Report(Base):
    """
    报表定义表

    @description 自定义报表定义

    @attributes
    - id: 报表ID
    - code: 报表编码
    - name: 报表名称
    - description: 描述
    - category: 报表分类
    - type: 报表类型
    - data_source: 数据源（SQL或数据表）
    - sql_query: SQL查询语句
    - is_public: 是否公开
    - status: 状态
    - created_by: 创建人
    - updated_by: 更新人
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="报表编码"
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="报表名称"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, comment="描述"
    )
    category: Mapped[str] = mapped_column(
        SQLEnum(ReportCategory),
        nullable=False,
        index=True,
        comment="报表分类"
    )
    type: Mapped[str] = mapped_column(
        SQLEnum(ReportType),
        default=ReportType.LIST,
        nullable=False,
        comment="报表类型"
    )

    # 数据源
    data_source: Mapped[Optional[str]] = mapped_column(
        String(100), comment="数据源"
    )
    sql_query: Mapped[Optional[str]] = mapped_column(
        Text, comment="SQL查询语句"
    )

    is_public: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="是否公开"
    )
    status: Mapped[str] = mapped_column(
        SQLEnum(ReportStatus),
        default=ReportStatus.DRAFT,
        nullable=False,
        comment="状态"
    )

    created_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), comment="创建人"
    )
    updated_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), comment="更新人"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="更新时间"
    )

    # 关系
    columns = relationship("ReportColumn", back_populates="report", cascade="all, delete-orphan")
    parameters = relationship("ReportParameter", back_populates="report", cascade="all, delete-orphan")
    favorites = relationship("ReportFavorite", back_populates="report", cascade="all, delete-orphan")


class ReportColumn(Base):
    """
    报表列定义表

    @description 报表列配置

    @attributes
    - id: 列ID
    - report_id: 报表ID
    - name: 列名
    - label: 显示名称
    - data_type: 数据类型
    - width: 宽度
    - is_visible: 是否可见
    - is_sortable: 是否可排序
    - is_filterable: 是否可筛选
    - is_summarizable: 是否可汇总
    - format_string: 格式化字符串
    - align: 对齐方式
    - sequence: 序号
    - created_at: 创建时间
    """

    __tablename__ = "report_columns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    report_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("reports.id"), nullable=False, comment="报表ID"
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="列名"
    )
    label: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="显示名称"
    )
    data_type: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="数据类型"
    )
    width: Mapped[Optional[int]] = mapped_column(
        Integer, comment="宽度"
    )
    is_visible: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, comment="是否可见"
    )
    is_sortable: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, comment="是否可排序"
    )
    is_filterable: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, comment="是否可筛选"
    )
    is_summarizable: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="是否可汇总"
    )
    format_string: Mapped[Optional[str]] = mapped_column(
        String(50), comment="格式化字符串"
    )
    align: Mapped[str] = mapped_column(
        String(10), default="left", nullable=False, comment="对齐方式"
    )
    sequence: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="序号"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )

    # 关系
    report = relationship("Report", back_populates="columns")


class ReportParameter(Base):
    """
    报表参数表

    @description 报表参数定义

    @attributes
    - id: 参数ID
    - report_id: 报表ID
    - name: 参数名
    - label: 显示名称
    - data_type: 数据类型
    - default_value: 默认值
    - is_required: 是否必填
    - input_type: 输入类型
    - options: 选项（JSON）
    - sequence: 序号
    - created_at: 创建时间
    """

    __tablename__ = "report_parameters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    report_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("reports.id"), nullable=False, comment="报表ID"
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="参数名"
    )
    label: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="显示名称"
    )
    data_type: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="数据类型"
    )
    default_value: Mapped[Optional[str]] = mapped_column(
        String(200), comment="默认值"
    )
    is_required: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="是否必填"
    )
    input_type: Mapped[str] = mapped_column(
        String(20), default="text", nullable=False, comment="输入类型"
    )
    options: Mapped[Optional[str]] = None  # JSON - 选项

    sequence: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="序号"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )

    # 关系
    report = relationship("Report", back_populates="parameters")


class ReportFavorite(Base):
    """
    报表收藏表

    @description 用户收藏的报表

    @attributes
    - id: 收藏ID
    - report_id: 报表ID
    - user_id: 用户ID
    - folder: 文件夹
    - sequence: 排序
    - created_at: 创建时间
    """

    __tablename__ = "report_favorites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    report_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("reports.id"), nullable=False, comment="报表ID"
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, comment="用户ID"
    )
    folder: Mapped[Optional[str]] = mapped_column(
        String(50), comment="文件夹"
    )
    sequence: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="排序"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )

    # 关系
    report = relationship("Report", back_populates="favorites")


class Dashboard(Base):
    """
    业务看板表

    @description 业务看板定义

    @attributes
    - id: 看板ID
    - code: 看板编码
    - name: 看板名称
    - description: 描述
    - category: 分类
    - is_public: 是否公开
    - layout: 布局配置（JSON）
    - refresh_interval: 刷新间隔（秒）
    - created_by: 创建人
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "dashboards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="看板编码"
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="看板名称"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, comment="描述"
    )
    category: Mapped[Optional[str]] = mapped_column(
        String(50), comment="分类"
    )
    is_public: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="是否公开"
    )
    layout: Mapped[Optional[dict]] = mapped_column(
        JSON, comment="布局配置（JSON）"
    )
    refresh_interval: Mapped[Optional[int]] = mapped_column(
        Integer, comment="刷新间隔（秒）"
    )

    created_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), comment="创建人"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="更新时间"
    )

    # 关系
    widgets = relationship("DashboardWidget", back_populates="dashboard", cascade="all, delete-orphan")


class DashboardWidget(Base):
    """
    看板组件表

    @description 看板上的组件

    @attributes
    - id: 组件ID
    - dashboard_id: 看板ID
    - widget_type: 组件类型
    - title: 标题
    - data_source: 数据源
    - config: 配置（JSON）
    - position: 位置（行、列、大小）
    - sequence: 序号
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "dashboard_widgets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    dashboard_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dashboards.id"), nullable=False, comment="看板ID"
    )
    widget_type: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="组件类型"
    )
    title: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="标题"
    )
    data_source: Mapped[Optional[str]] = mapped_column(
        Text, comment="数据源"
    )
    config: Mapped[Optional[dict]] = mapped_column(
        JSON, comment="组件配置（JSON）"
    )
    position: Mapped[Optional[dict]] = mapped_column(
        JSON, comment="位置配置（JSON）"
    )
    sequence: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="序号"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="更新时间"
    )

    # 关系
    dashboard = relationship("Dashboard", back_populates="widgets")


class FinancialReportType(str, enum.Enum):
    """财务报表类型"""
    BALANCE_SHEET = "balance_sheet"  # 资产负债表
    INCOME_STATEMENT = "income_statement"  # 利润表
    CASH_FLOW = "cash_flow"  # 现金流量表
    TRIAL_BALANCE = "trial_balance"  # 科目余额表
    AGED_RECEIVABLE = "aged_receivable"  # 账龄分析表
    AGED_PAYABLE = "aged_payable"  # 应付账龄表


class FinancialReport(Base):
    """
    财务报表表

    @description 财务报表定义

    @attributes
    - id: 报表ID
    - code: 报表编码
    - name: 报表名称
    - report_type: 报表类型
    - period: 期间
    - start_date: 开始日期
    - end_date: 结束日期
    - status: 状态
    - generated_by: 生成人
    - generated_at: 生成时间
    - created_at: 创建时间
    """

    __tablename__ = "financial_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="报表编码"
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="报表名称"
    )
    report_type: Mapped[str] = mapped_column(
        SQLEnum(FinancialReportType),
        nullable=False,
        index=True,
        comment="报表类型"
    )
    period: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="期间"
    )
    start_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="开始日期"
    )
    end_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="结束日期"
    )
    status: Mapped[str] = mapped_column(
        String(20), default="draft", nullable=False, comment="状态"
    )
    generated_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), comment="生成人"
    )
    generated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, comment="生成时间"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )

    # 关系
    lines = relationship("FinancialReportLine", back_populates="report", cascade="all, delete-orphan")


class FinancialReportLine(Base):
    """
    财务报表行表

    @description 财务报表的行项目

    @attributes
    - id: 行ID
    - report_id: 报表ID
    - line_no: 行号
    - account_id: 科目ID
    - item_code: 项目编码
    - item_name: 项目名称
    - line_type: 行类型
    - level: 层级
    - parent_line_no: 父行号
    - beginning_balance: 期初余额
    - current_debit: 本期借方
    - current_credit: 本期贷方
    - ending_balance: 期末余额
    - sequence: 序号
    - created_at: 创建时间
    """

    __tablename__ = "financial_report_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    report_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("financial_reports.id"), nullable=False, comment="报表ID"
    )
    line_no: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="行号"
    )
    account_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("accounts.id"), comment="科目ID"
    )
    item_code: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="项目编码"
    )
    item_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="项目名称"
    )
    line_type: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="行类型"
    )
    level: Mapped[int] = mapped_column(
        Integer, default=1, nullable=False, comment="层级"
    )
    parent_line_no: Mapped[Optional[str]] = mapped_column(
        String(20), comment="父行号"
    )

    # 金额
    beginning_balance: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), comment="期初余额"
    )
    current_debit: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), comment="本期借方"
    )
    current_credit: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), comment="本期贷方"
    )
    ending_balance: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), comment="期末余额"
    )

    sequence: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="序号"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )

    # 关系
    report = relationship("FinancialReport", back_populates="lines")
