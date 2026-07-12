"""
数据库模型模块

@description SQLAlchemy ORM 模型定义
"""

from app.models.user import User, UserSession, PasswordReset
from app.models.rbac import Role, Permission, RolePermission, UserRole
from app.models.organization import Department, Position, EmployeeProfile
from app.models.workflow import (
    WorkflowDefinition,
    WorkflowNode,
    WorkflowEdge,
    WorkflowInstance,
    WorkflowTask,
    WorkflowApproval,
)
from app.models.purchase import (
    Supplier,
    PurchaseRequest,
    PurchaseRequestItem,
    PurchaseOrder,
    PurchaseOrderItem,
)
from app.models.sales import Customer, SalesOrder, SalesOrderItem, SalesReturn, SalesReturnItem
from app.models.inventory import (
    Warehouse,
    Product,
    Inventory,
    InventoryTransaction,
    InventoryTransfer,
    InventoryTransferItem,
)
from app.models.finance import (
    Account,
    PaymentMethod,
    Receivable,
    Payable,
    Payment,
)
from app.models.audit import AuditLog, AuditLogDetail, AuditActionType, AuditLogLevel
from app.models.attachment import Attachment, AttachmentCategory, AttachmentStorageType, AttachmentStatus
from app.models.notification import (
    Notification,
    NotificationTemplate,
    NotificationPreference,
    NotificationLog,
    NotificationType,
    NotificationChannel,
    NotificationPriority,
    NotificationStatus,
)
from app.models.number_rule import NumberRule, NumberSequence
from app.models.production import (
    BOM,
    BOMItem,
    BOMStatus,
    BOMItemType,
    ProductionOrder,
    ProductionOrderItem,
    ProductionOrderStatus,
    ProductionProcess,
    Routing,
    WorkOrder,
    WorkOrderStatus,
    WorkReport,
    WorkCenter,
)
from app.models.quality import (
    InspectionScheme,
    InspectionItem,
    InspectionStandard,
    SamplingPlan,
    IncomingInspection,
    IncomingInspectionItem,
    ProcessInspection,
    ProcessInspectionItem,
    OutgoingInspection,
    OutgoingInspectionItem,
    QualityTrace,
    InspectionType,
    InspectionMethod,
    InspectionResult,
    InspectionStatus,
    DefectLevel,
)
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
    ReportStatus,
    FinancialReportType,
)

__all__ = [
    # User
    "User",
    "UserSession",
    "PasswordReset",
    # RBAC
    "Role",
    "Permission",
    "RolePermission",
    "UserRole",
    # Organization
    "Department",
    "Position",
    "EmployeeProfile",
    # Workflow
    "WorkflowDefinition",
    "WorkflowNode",
    "WorkflowEdge",
    "WorkflowInstance",
    "WorkflowTask",
    "WorkflowApproval",
    # Purchase
    "Supplier",
    "PurchaseRequest",
    "PurchaseRequestItem",
    "PurchaseOrder",
    "PurchaseOrderItem",
    # Sales
    "Customer",
    "SalesOrder",
    "SalesOrderItem",
    "SalesReturn",
    "SalesReturnItem",
    # Inventory
    "Warehouse",
    "Product",
    "Inventory",
    "InventoryTransaction",
    "InventoryTransfer",
    "InventoryTransferItem",
    # Finance
    "Account",
    "PaymentMethod",
    "Receivable",
    "Payable",
    "Payment",
    # Audit
    "AuditLog",
    "AuditLogDetail",
    "AuditActionType",
    "AuditLogLevel",
    # Attachment
    "Attachment",
    "AttachmentCategory",
    "AttachmentStorageType",
    "AttachmentStatus",
    # Notification
    "Notification",
    "NotificationTemplate",
    "NotificationPreference",
    "NotificationLog",
    "NotificationType",
    "NotificationChannel",
    "NotificationPriority",
    "NotificationStatus",
    # Number Rule
    "NumberRule",
    "NumberSequence",
    # Production
    "BOM",
    "BOMItem",
    "BOMStatus",
    "BOMItemType",
    "ProductionOrder",
    "ProductionOrderItem",
    "ProductionOrderStatus",
    "ProductionProcess",
    "Routing",
    "WorkOrder",
    "WorkOrderStatus",
    "WorkReport",
    "WorkCenter",
    # Quality
    "InspectionScheme",
    "InspectionItem",
    "InspectionStandard",
    "SamplingPlan",
    "IncomingInspection",
    "IncomingInspectionItem",
    "ProcessInspection",
    "ProcessInspectionItem",
    "OutgoingInspection",
    "OutgoingInspectionItem",
    "QualityTrace",
    "InspectionType",
    "InspectionMethod",
    "InspectionResult",
    "InspectionStatus",
    "DefectLevel",
    # Report
    "Report",
    "ReportColumn",
    "ReportParameter",
    "ReportFavorite",
    "Dashboard",
    "DashboardWidget",
    "FinancialReport",
    "FinancialReportLine",
    "ReportType",
    "ReportCategory",
    "ReportStatus",
    "FinancialReportType",
]
