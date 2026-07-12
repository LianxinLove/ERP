# 权限系统初始化数据

## 预设权限列表

### 系统管理模块 (system)
| 权限名称 | 权限编码 | 说明 |
|---------|---------|------|
| 查看用户 | system.user.view | 查看用户列表和详情 |
| 创建用户 | system.user.create | 创建新用户 |
| 编辑用户 | system.user.edit | 编辑用户信息 |
| 删除用户 | system.user.delete | 删除用户 |
| 重置密码 | system.user.reset | 重置用户密码 |
| 查看角色 | system.role.view | 查看角色列表和详情 |
| 创建角色 | system.role.create | 创建新角色 |
| 编辑角色 | system.role.edit | 编辑角色信息和权限 |
| 删除角色 | system.role.delete | 删除角色 |
| 分配角色 | system.role.assign | 为用户分配角色 |
| 查看权限 | system.permission.view | 查看权限列表 |
| 系统配置 | system.config | 修改系统配置 |

### 组织架构模块 (org)
| 权限名称 | 权限编码 | 说明 |
|---------|---------|------|
| 查看部门 | org.department.view | 查看部门列表 |
| 创建部门 | org.department.create | 创建新部门 |
| 编辑部门 | org.department.edit | 编辑部门信息 |
| 删除部门 | org.department.delete | 删除部门 |
| 查看职位 | org.position.view | 查看职位列表 |
| 创建职位 | org.position.create | 创建新职位 |
| 编辑职位 | org.position.edit | 编辑职位信息 |
| 删除职位 | org.position.delete | 删除职位 |
| 查看员工 | org.employee.view | 查看员工档案 |
| 创建员工 | org.employee.create | 创建员工档案 |
| 编辑员工 | org.employee.edit | 编辑员工档案 |
| 删除员工 | org.employee.delete | 删除员工档案 |

### 采购管理模块 (purchase)
| 权限名称 | 权限编码 | 说明 |
|---------|---------|------|
| 查看供应商 | purchase.supplier.view | 查看供应商列表 |
| 创建供应商 | purchase.supplier.create | 创建新供应商 |
| 编辑供应商 | purchase.supplier.edit | 编辑供应商信息 |
| 删除供应商 | purchase.supplier.delete | 删除供应商 |
| 查看采购申请 | purchase.request.view | 查看采购申请 |
| 创建采购申请 | purchase.request.create | 创建采购申请 |
| 编辑采购申请 | purchase.request.edit | 编辑采购申请 |
| 删除采购申请 | purchase.request.delete | 删除采购申请 |
| 审批采购申请 | purchase.request.approve | 审批采购申请 |
| 查看采购订单 | purchase.order.view | 查看采购订单 |
| 创建采购订单 | purchase.order.create | 创建采购订单 |
| 编辑采购订单 | purchase.order.edit | 编辑采购订单 |
| 删除采购订单 | purchase.order.delete | 删除采购订单 |

### 销售管理模块 (sales)
| 权限名称 | 权限编码 | 说明 |
|---------|---------|------|
| 查看客户 | sales.customer.view | 查看客户列表 |
| 创建客户 | sales.customer.create | 创建新客户 |
| 编辑客户 | sales.customer.edit | 编辑客户信息 |
| 删除客户 | sales.customer.delete | 删除客户 |
| 查看销售订单 | sales.order.view | 查看销售订单 |
| 创建销售订单 | sales.order.create | 创建销售订单 |
| 编辑销售订单 | sales.order.edit | 编辑销售订单 |
| 删除销售订单 | sales.order.delete | 删除销售订单 |
| 审批销售订单 | sales.order.approve | 审批销售订单 |
| 查看销售退货 | sales.return.view | 查看销售退货 |
| 创建销售退货 | sales.return.create | 创建销售退货 |

### 库存管理模块 (inventory)
| 权限名称 | 权限编码 | 说明 |
|---------|---------|------|
| 查看仓库 | inventory.warehouse.view | 查看仓库列表 |
| 创建仓库 | inventory.warehouse.create | 创建新仓库 |
| 编辑仓库 | inventory.warehouse.edit | 编辑仓库信息 |
| 删除仓库 | inventory.warehouse.delete | 删除仓库 |
| 查看产品 | inventory.product.view | 查看产品列表 |
| 创建产品 | inventory.product.create | 创建新产品 |
| 编辑产品 | inventory.product.edit | 编辑产品信息 |
| 删除产品 | inventory.product.delete | 删除产品 |
| 查看库存 | inventory.stock.view | 查看库存信息 |
| 调整库存 | inventory.stock.adjust | 调整库存数量 |
| 库存盘点 | inventory.stock.check | 库存盘点 |
| 库存调拨 | inventory.stock.transfer | 库存调拨 |

### 财务管理模块 (finance)
| 权限名称 | 权限编码 | 说明 |
|---------|---------|------|
| 查看应收 | finance.receivable.view | 查看应收账款 |
| 创建应收 | finance.receivable.create | 创建应收记录 |
| 编辑应收 | finance.receivable.edit | 编辑应收记录 |
| 删除应收 | finance.receivable.delete | 删除应收记录 |
| 查看应付 | finance.payable.view | 查看应付账款 |
| 创建应付 | finance.payable.create | 创建应付记录 |
| 编辑应付 | finance.payable.edit | 编辑应付记录 |
| 删除应付 | finance.payable.delete | 删除应付记录 |
| 查看收付款 | finance.payment.view | 查看收付款记录 |
| 创建收付款 | finance.payment.create | 创建收付款记录 |

---

## 预设角色

### 超级管理员 (superadmin)
- 拥有所有权限
- 系统角色，不可删除

### 管理员 (admin)
- 除系统配置外的所有权限

### 采购专员 (purchase_staff)
- 采购相关所有权限

### 销售专员 (sales_staff)
- 销售相关所有权限

### 库管员 (warehouse_keeper)
- 库存管理相关所有权限

### 财务人员 (finance_staff)
- 财务管理相关所有权限

### 普通员工 (employee)
- 基础查看权限
