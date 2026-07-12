"""
API路由模块

@description 注册所有API路由

@features
- 版本化API
- 模块化路由注册
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, health, rbac, organization, workflow, purchase, sales, inventory, finance, data_permissions, audit, attachments, notifications, number_rules, invoice, batch, serial_number, unit

api_router = APIRouter()

# 健康检查
api_router.include_router(health.router, tags=["健康检查"])

# 认证相关
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])

# 角色权限
api_router.include_router(rbac.router, prefix="/rbac", tags=["角色权限"])

# 数据权限
api_router.include_router(data_permissions.router, prefix="/rbac", tags=["数据权限"])

# 审计日志
api_router.include_router(audit.router, prefix="/system", tags=["审计日志"])

# 附件管理
api_router.include_router(attachments.router, prefix="/system", tags=["附件管理"])

# 通知系统
api_router.include_router(notifications.router, prefix="/system", tags=["通知系统"])

# 编码规则
api_router.include_router(number_rules.router, prefix="/system", tags=["编码规则"])

# 组织架构
api_router.include_router(organization.router, prefix="/org", tags=["组织架构"])

# 审批流程
api_router.include_router(workflow.router, prefix="/workflows", tags=["审批流程"])

# 采购管理
api_router.include_router(purchase.router, prefix="/purchase", tags=["采购管理"])

# 销售管理
api_router.include_router(sales.router, prefix="/sales", tags=["销售管理"])

# 库存管理
api_router.include_router(inventory.router, prefix="/inventory", tags=["库存管理"])

# 财务管理
api_router.include_router(finance.router, prefix="/finance", tags=["财务管理"])

# 发票管理
api_router.include_router(invoice.router, prefix="/invoices", tags=["发票管理"])

# 批号管理
api_router.include_router(batch.router, prefix="/inventory", tags=["批号管理"])

# 序列号管理
api_router.include_router(serial_number.router, prefix="/inventory", tags=["序列号管理"])

# 多单位换算
api_router.include_router(unit.router, prefix="/inventory", tags=["多单位换算"])

# 用户管理
# api_router.include_router(users.router, prefix="/users", tags=["用户管理"])
