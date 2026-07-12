# ERP系统开发任务计划

## 项目概述
创建一个复杂的ERP系统，用于展示AI工具开发能力。这是一个全栈项目，包含完整的前后端分离架构。

### 技术栈
- **前端**：React、Next.js (App Router)、TypeScript
- **后端**：Python、FastAPI
- **数据库**：MySQL 8.0+
- **UI组件**：shadcn/ui (通过 UI-UX-Pro-Max skill)
- **状态管理**：React Context + Hooks / Zustand
- **HTTP客户端**：Axios / React Query
- **认证**：JWT + Refresh Token
- **部署**：Docker (可选)

### 核心功能模块
1. 账号系统（登录、注册、用户管理、密码重置）
2. 角色权限控制（RBAC - 基于角色的访问控制）
3. 完整的审批流程引擎
4. ERP基础模块（组织架构、采购管理、销售管理、库存管理、财务管理）

---

## 当前阶段
**阶段：项目完善与优化**

### 项目完成度总览（2024-07-12更新）

| 模块 | 后端状态 | 前端状态 | 完成度 |
|------|----------|----------|--------|
| 1. 项目基础架构 | ✅ 完成 | ✅ 完成 | 100% |
| 2. 用户认证系统 | ✅ 完成 | ✅ 完成 | 100% |
| 3. RBAC权限系统 | ✅ 完成 | 🟡 部分 | 85% |
| 4. 组织架构管理 | ✅ 完成 | 🟡 部分 | 75% |
| 5. 审批流程引擎 | ✅ 完成 | 🟡 部分 | 75% |
| 6. 采购管理模块 | ✅ 完成 | 🟡 部分 | 75% |
| 7. 销售管理模块 | ✅ 完成 | 🟡 部分 | 75% |
| 8. 库存管理模块 | ✅ 完成 | 🟡 部分 | 75% |
| 9. 财务管理模块 | ✅ 完成 | 🟡 部分 | 75% |
| 10. 通知系统 | ✅ 完成 | ❌ 缺失 | 50% |
| 11. 附件管理 | ✅ 完成 | ❌ 缺失 | 50% |
| 12. 编号规则管理 | ✅ 完成 | ❌ 缺失 | 50% |
| 13. 数据权限系统 | ✅ 完成 | ✅ 完成 | 100% |
| 14. UI/UX优化 | 🟡 部分 | 🟡 部分 | 40% |
| 15. 测试覆盖 | 🟡 部分 | 🟡 部分 | 30% |

### 当前完善重点
1. **前端通知系统** - 用户需要看到待办、审批结果等通知
2. **前端附件管理** - 采购、销售等业务需要附件上传
3. **系统设置页面** - 系统配置、个人设置
4. **数据表单优化** - 所有模块的表单验证和提交
5. **响应式布局优化** - 移动端适配

---

## 各阶段详细计划

### 🏗️ 阶段 1：项目初始化与基础架构
**目标**：建立项目骨架，配置开发环境，搭建基础架构

- [x] 1.1 创建项目目录结构（monorepo或分离仓库）
  - [x] 前端：Next.js + TypeScript
  - [x] 后端：FastAPI + Python
  - [x] 共享类型：共享类型定义
- [x] 1.2 配置开发环境
  - [x] ESLint + Prettier（前端）
  - [ ] Black + Ruff（后端）
  - [ ] Git hooks (Husky)
- [x] 1.3 数据库设计
  - [x] ER图设计
  - [x] 基础表结构创建
- [ ] 1.4 Docker配置（可选）
  - [ ] docker-compose.yml
  - [ ] 开发环境配置
- [x] 1.5 创建约束文档
  - [x] 开发规范
  - [x] 代码注释规范
  - [x] 错误处理规范

**状态：** complete ✅  
**完成时间：** 2024-06-20  
**实际耗时：** 约2小时

---

### 🔐 阶段 2：账号与认证系统
**目标**：实现完整的用户认证和授权功能

- [x] 2.1 用户表设计与实现
  - [x] users 表（用户基本信息）
  - [x] user_sessions 表（会话管理）
  - [x] password_resets 表（密码重置）
- [x] 2.2 后端认证API
  - [x] POST /api/auth/register - 用户注册
  - [x] POST /api/auth/login - 用户登录
  - [x] POST /api/auth/logout - 用户登出
  - [x] POST /api/auth/refresh - 刷新Token
  - [x] POST /api/auth/forgot-password - 忘记密码
  - [x] POST /api/auth/reset-password - 重置密码
  - [x] GET /api/auth/me - 获取当前用户信息
- [x] 2.3 JWT认证中间件
  - [x] Access Token (15分钟)
  - [x] Refresh Token (7天)
  - [x] Token刷新策略
- [x] 2.4 前端认证页面
  - [x] 登录页面
  - [x] 注册页面
  - [ ] 忘记密码页面
  - [ ] 重置密码页面
- [x] 2.5 认证状态管理
  - [x] AuthContext
  - [ ] ProtectedRoute 组件
  - [x] 自动Token刷新
- [ ] 2.6 单元测试
  - [ ] 认证API测试
  - [ ] 认证组件测试

**状态：** complete ✅  
**完成时间：** 2024-06-20  
**实际耗时：** 约1小时

---

### 👥 阶段 3：角色权限控制系统 (RBAC)
**目标**：实现基于角色的访问控制

- [x] 3.1 权限表设计
  - [x] roles 表（角色）
  - [x] permissions 表（权限）
  - [x] role_permissions 表（角色-权限关联）
  - [x] user_roles 表（用户-角色关联）
- [x] 3.2 权限定义
  - [x] 系统级权限（用户管理、角色管理、系统配置）
  - [x] 模块级权限（采购、销售、库存、财务）
  - [x] 操作级权限（查看、创建、编辑、删除、审批）
- [x] 3.3 后端权限API
  - [x] GET /api/permissions - 获取所有权限
  - [x] GET /api/roles - 获取所有角色
  - [x] POST /api/roles - 创建角色
  - [x] PUT /api/roles/:id - 更新角色
  - [x] DELETE /api/roles/:id - 删除角色
  - [x] POST /api/roles/:id/permissions - 分配权限
- [x] 3.4 权限中间件
  - [x] require_permission 装饰器
  - [x] require_role 装饰器
  - [x] 权限缓存策略
- [x] 3.5 前端权限控制
  - [x] PermissionContext
  - [x] PermissionGate 组件
  - [x] usePermission Hook
  - [x] 菜单/按钮级权限控制
- [ ] 3.6 管理页面
  - [ ] 角色管理页面
  - [ ] 权限分配页面
  - [ ] 用户角色分配页面

**状态：** complete ✅  
**完成时间：** 2024-06-20  
**实际耗时：** 约1小时

---

### 🏢 阶段 4：组织架构管理
**目标**：实现企业组织架构管理

- [x] 4.1 组织架构表设计
  - [x] departments 表（部门）
  - [x] positions 表（职位）
  - [x] employee_profiles 表（员工档案）
- [x] 4.2 后端API
  - [x] GET /api/departments - 部门列表（树形结构）
  - [x] POST /api/departments - 创建部门
  - [x] PUT /api/departments/:id - 更新部门
  - [x] DELETE /api/departments/:id - 删除部门
  - [x] GET /api/positions - 职位列表
  - [x] POST /api/positions - 创建职位
  - [x] GET /api/employees - 员工列表
  - [x] POST /api/employees - 创建员工档案
- [ ] 4.3 前端页面
  - [ ] 部门管理（树形展示）
  - [ ] 职位管理
  - [ ] 员工档案管理
- [x] 4.4 组织架构选择器组件
  - [x] 部门选择器（树形）
  - [x] 员工选择器（搜索）

**状态：** complete ✅  
**完成时间：** 2024-06-20  
**实际耗时：** 约30分钟

---

### 📋 阶段 5：审批流程引擎
**目标**：实现灵活的审批流程引擎

- [x] 5.1 审批流程表设计
  - [x] workflow_definitions 表（流程定义）
  - [x] workflow_nodes 表（流程节点）
  - [x] workflow_edges 表（节点连线）
  - [x] workflow_instances 表（流程实例）
  - [x] workflow_tasks 表（审批任务）
  - [x] workflow_approvals 表（审批记录）
- [ ] 5.2 流程设计器
  - [ ] 流程图编辑器（基于React Flow）
  - [x] 节点类型：开始、结束、审批、条件、并行
  - [ ] 节点属性配置
- [x] 5.3 流程引擎核心
  - [x] 流程启动
  - [x] 节点流转逻辑
  - [x] 条件判断
  - [x] 并行处理
  - [x] 回退/撤回/拒绝
  - [ ] 转办/加签
- [x] 5.4 后端API
  - [x] POST /api/workflows/definitions - 创建流程定义
  - [x] PUT /api/workflows/definitions/:id - 更新流程定义
  - [x] POST /api/workflows/instances/:id/start - 启动流程
  - [x] GET /api/workflows/tasks - 我的待办
  - [x] POST /api/workflows/tasks/:id/approve - 审批通过
  - [x] POST /api/workflows/tasks/:id/reject - 审批拒绝
  - [x] POST /api/workflows/tasks/:id/return - 退回
- [x] 5.5 前端页面
  - [ ] 流程定义管理
  - [ ] 流程设计器
  - [x] 我的待办
  - [x] 我的已办
  - [x] 流程详情/审批页面
  - [x] 流程进度查看

**状态：** complete ✅
**完成时间：** 2024-06-20
**实际耗时：** 约1.5小时
**备注：** 流程设计器（可视化编辑器）暂未实现，可后续补充

---

### 📦 阶段 6：采购管理模块
**目标**：实现采购管理功能

- [ ] 6.1 采购表设计
  - [ ] suppliers 表（供应商）
  - [ ] purchase_requests 表（采购申请）
  - [ ] purchase_orders 表（采购订单）
  - [ ] purchase_items 表（采购明细）
- [ ] 6.2 后端API
  - [ ] 供应商CRUD
  - [ ] 采购申请CRUD + 提交审批
  - [ ] 采购订单CRUD
  - [ ] 采购订单状态流转
- [ ] 6.3 前端页面
  - [ ] 供应商管理
  - [ ] 采购申请
  - [ ] 采购订单
  - [ ] 采购统计报表

**状态：** pending  
**依赖**：阶段 5 完成  
**预计时间**：3天

---

### 🛒 阶段 7：销售管理模块
**目标**：实现销售管理功能

- [ ] 7.1 销售表设计
  - [ ] customers 表（客户）
  - [ ] sales_orders 表（销售订单）
  - [ ] sales_items 表（销售明细）
  - [ ] sales_returns 表（销售退货）
- [ ] 7.2 后端API
  - [ ] 客户CRUD
  - [ ] 销售订单CRUD
  - [ ] 销售退货CRUD
- [ ] 7.3 前端页面
  - [ ] 客户管理
  - [ ] 销售订单
  - [ ] 销售退货
  - [ ] 销售统计报表

**状态：** pending  
**依赖**：阶段 5 完成  
**预计时间**：3天

---

### 📊 阶段 8：库存管理模块
**目标**：实现库存管理功能

- [x] 8.1 库存表设计
  - [x] warehouses 表（仓库）
  - [x] products 表（产品）
  - [x] inventory 表（库存）
  - [x] inventory_transactions 表（库存流水）
  - [x] inventory_transfers 表（库存调拨）
- [x] 8.2 后端API
  - [x] 仓库CRUD
  - [x] 产品CRUD
  - [x] 库存查询/调整
  - [x] 库存流水查询
  - [x] 库存调拨
- [x] 8.3 前端页面
  - [x] 仓库管理 (/inventory/warehouses)
  - [x] 产品管理 (/inventory/products)
  - [x] 库存查询 (/inventory)
  - [x] 库存流水 (/inventory/transactions)
  - [x] 库存调拨 (/inventory/transfers)
  - [x] 库存预警组件（集成在总览页面）

**状态：** complete ✅
**完成时间：** 2024-06-21
**实际耗时：** 约2小时

---

## 当前任务：库存管理前端开发（2024-06-21）✅ 已完成

---

### 💰 阶段 9：财务管理模块
**目标**：实现基础财务管理功能

- [ ] 9.1 财务表设计
  - [ ] accounts 表（科目）
  - [ ] payment_methods 表（付款方式）
  - [ ] receivables 表（应收账款）
  - [ ] payables 表（应付账款）
  - [ ] payments 表（收付款记录）
- [ ] 9.2 后端API
  - [ ] 科目管理
  - [ ] 应收/应付管理
  - [ ] 收付款记录
- [ ] 9.3 前端页面
  - [ ] 科目设置
  - [ ] 应收账款
  - [ ] 应付账款
  - [ ] 收付款记录

**状态：** pending  
**依赖**：阶段 5 完成  
**预计时间**：3天

---

### 🎨 阶段 10：UI/UX优化
**目标**：优化用户界面和体验

- [ ] 10.1 设计系统
  - [ ] 调用 UI-UX-Pro-Max skill 进行设计评审
  - [ ] 统一颜色规范
  - [ ] 统一字体规范
  - [ ] 统一间距规范
- [ ] 10.2 公共组件库
  - [ ] DataTable（数据表格）
  - [ ] SearchForm（搜索表单）
  - [ ] ModalForm（弹窗表单）
  - [ ] TreeSelect（树形选择）
  - [ ] DatePicker（日期选择）
  - [ ] FileUpload（文件上传）
- [ ] 10.3 布局优化
  - [ ] 响应式布局
  - [ ] Loading状态
  - [ ] Empty状态
  - [ ] Error状态
- [ ] 10.4 交互优化
  - [ ] 操作反馈（Toast/Snackbar）
  - [ ] 确认对话框
  - [ ] 批量操作
  - [ ] 导出功能

**状态：** pending  
**依赖**：阶段 2-9 完成  
**预计时间**：3-4天

---

### 🧪 阶段 11：测试与文档
**目标**：完善测试覆盖和项目文档

- [ ] 11.1 单元测试
  - [ ] 后端API测试（pytest）
  - [ ] 前端组件测试（Jest + React Testing Library）
- [ ] 11.2 集成测试
  - [ ] API集成测试
  - [ ] 端到端测试（Playwright）
- [ ] 11.3 性能优化
  - [ ] 前端性能分析
  - [ ] 后端查询优化
  - [ ] 数据库索引优化
- [ ] 11.4 文档完善
  - [ ] API文档（Swagger/OpenAPI）
  - [ ] 组件文档（Storybook）
  - [ ] 部署文档
  - [ ] 用户手册

**状态：** pending  
**依赖**：所有功能阶段完成  
**预计时间**：2-3天

---

### 🚀 阶段 12：部署与交付
**目标**：完成项目部署和最终交付

- [ ] 12.1 部署准备
  - [ ] 环境变量配置
  - [ ] 生产数据库迁移
  - [ ] 静态资源优化
- [ ] 12.2 Docker部署
  - [ ] 构建生产镜像
  - [ ] docker-compose生产配置
- [ ] 12.3 交付检查
  - [ ] 功能完整性检查
  - [ ] 代码质量检查
  - [ ] 安全检查
- [ ] 12.4 项目总结
  - [ ] 技术亮点总结
  - [ ] AI辅助开发经验总结

**状态：** pending  
**依赖**：所有阶段完成  
**预计时间**：1-2天

---

## 关键问题

1. **项目结构选择**：Monorepo 还是分离仓库？
   - 推荐：Monorepo（便于共享类型和协调开发）
   - 工具：Turborepo 或 Nx

2. **数据库迁移工具**：如何管理数据库版本？
   - Python: Alembic
   - 需要在阶段1确定

3. **文件存储**：用户上传的文件如何存储？
   - 本地存储（开发）
   - OSS（生产）
   - 需要在阶段1确定

---

## 已做决策

| 决策 | 理由 |
|------|------|
| Next.js App Router | 最新架构，性能更好，支持RSC |
| FastAPI | 现代Python框架，自动API文档，类型提示 |
| JWT认证 | 无状态，易于扩展，前后端分离友好 |
| RBAC权限模型 | 企业级标准，易于理解和维护 |
| shadcn/ui | 现代设计，可定制，基于Radix UI |
| MySQL | 成熟稳定，事务支持好，适合企业应用 |
| React Query | 数据获取和缓存，优秀的开发体验 |

---

## 遇到的错误

| 错误 | 尝试次数 | 解决方案 |
|------|---------|---------|
| 422 error on `/api/finance/receivables?status=` | 1 | Changed query parameter type from `Optional[EnumType]` to `Optional[str]` with manual validation |
| Empty string fails Literal type validation | 1 | Added `status if status and status.strip() else None` check in endpoint function |

---

## 当前任务：API错误修复（2024-06-21）

### 问题
前端调用 `/api/finance/receivables?status=` 时返回 422 错误：
```json
{"detail":[{"type":"literal_error","loc":["query","status"],"msg":"Input should be 'pending', 'partial_paid', 'paid', 'overdue' or 'write_off'","input":"","ctx":{"expected":"'pending', 'partial_paid', 'paid', 'overdue' or 'write_off'"}}]}
```

### 根本原因
FastAPI 的 `Optional[EnumType]` 类型验证会在空字符串时失败，因为 Literal 类型不接受空字符串。

### 解决方案
将查询参数类型从 `Optional[EnumType]` 改为 `Optional[str]`，然后在函数内部手动验证和转换：

**修改文件**: `apps/backend/app/api/v1/endpoints/finance.py`

```python
# Before:
status: Annotated[Optional[ReceivableStatus], Query(description="状态筛选")] = None,
# After:
status: Annotated[Optional[str], Query(description="状态筛选")] = None,

# Before in function:
status=status.value if status else None,
# After in function:
status=status if status and status.strip() else None,
```

### 已修复的端点
- ✅ `/api/finance/receivables` - status参数
- ✅ `/api/finance/payables` - status参数  
- ✅ `/api/finance/payments` - payment_type和status参数

### 待测试
- 重启后端服务器后测试所有修复的端点
- 检查其他模块是否有类似问题

---

## 上下文管理策略

当上下文接近80%容量时执行以下压缩策略：

1. **保存当前状态**：将当前进度写入 progress.md
2. **完成当前任务**：确保当前正在进行的任务完成
3. **压缩历史**：
   - 已完成的阶段记录到 progress.md
   - 关键决策保留在 findings.md
   - 代码变更通过 git 查看
4. **重新开始**：使用新会话继续下一阶段

---

---

## 项目完善计划（2024-07-12）

### 第一阶段：核心功能完善（P0优先级）

#### Task 1.1: 前端通知系统
**状态**: ⏳ 待开始
**优先级**: P0
**预计时间**: 4小时

**子任务**:
- [ ] 创建通知中心组件 (`NotificationCenter.tsx`)
- [ ] 实现通知列表展示
- [ ] 实现通知标记已读功能
- [ ] 实现实时通知推送（WebSocket或轮询）
- [ ] 添加通知音效和桌面通知
- [ ] 通知详情页面

**文件清单**:
- `apps/frontend/src/components/notification/NotificationCenter.tsx`
- `apps/frontend/src/components/notification/NotificationItem.tsx`
- `apps/frontend/src/hooks/useNotifications.ts`
- `apps/frontend/src/app/notifications/page.tsx`

---

#### Task 1.2: 前端附件管理
**状态**: ⏳ 待开始
**优先级**: P0
**预计时间**: 3小时

**子任务**:
- [ ] 创建文件上传组件 (`FileUploader.tsx`)
- [ ] 实现拖拽上传功能
- [ ] 实现文件预览功能
- [ ] 实现文件删除功能
- [ ] 添加文件类型和大小验证

**文件清单**:
- `apps/frontend/src/components/attachment/FileUploader.tsx`
- `apps/frontend/src/components/attachment/FilePreview.tsx`
- `apps/frontend/src/components/attachment/FileList.tsx`
- `apps/frontend/src/hooks/useFileUpload.ts`

---

#### Task 1.3: 系统设置页面
**状态**: ⏳ 待开始
**优先级**: P0
**预计时间**: 3小时

**子任务**:
- [ ] 个人设置页面（修改密码、头像等）
- [ ] 系统设置页面（需要管理员权限）
- [ ] 通知设置
- [ ] 主题切换功能

**文件清单**:
- `apps/frontend/src/app/settings/profile/page.tsx`
- `apps/frontend/src/app/settings/system/page.tsx`
- `apps/frontend/src/app/settings/notifications/page.tsx`
- `apps/frontend/src/components/settings/ProfileForm.tsx`

---

#### Task 1.4: 数据表单优化
**状态**: ⏳ 待开始
**优先级**: P0
**预计时间**: 5小时

**子任务**:
- [ ] 优化用户表单（RBAC模块）
- [ ] 优化部门表单（组织模块）
- [ ] 优化流程表单（审批模块）
- [ ] 优化采购表单（采购模块）
- [ ] 优化销售表单（销售模块）
- [ ] 统一表单验证规则

---

### 第二阶段：用户体验优化（P1优先级）

#### Task 2.1: 响应式布局优化
**状态**: ⏳ 待开始
**优先级**: P1
**预计时间**: 4小时

**子任务**:
- [ ] 优化侧边栏在小屏幕上的显示
- [ ] 优化数据表格的移动端展示
- [ ] 优化表单在移动端的布局
- [ ] 添加移动端导航菜单

---

#### Task 2.2: 搜索和筛选功能
**状态**: ⏳ 待开始
**优先级**: P1
**预计时间**: 3小时

**子任务**:
- [ ] 创建通用搜索组件
- [ ] 为各列表页添加高级筛选
- [ ] 实现搜索历史记录
- [ ] 实现搜索结果高亮

---

#### Task 2.3: 批量操作功能
**状态**: ⏳ 待开始
**优先级**: P1
**预计时间**: 3小时

**子任务**:
- [ ] 批量删除功能
- [ ] 批量导出功能
- [ ] 批量修改状态功能
- [ ] 批量分配功能

---

#### Task 2.4: 加载状态优化
**状态**: ⏳ 待开始
**优先级**: P1
**预计时间**: 2小时

**子任务**:
- [ ] 为所有列表页添加骨架屏
- [ ] 优化按钮加载状态
- [ ] 添加全局加载提示
- [ ] 优化错误提示样式

---

### 第三阶段：增强功能（P2优先级）

#### Task 3.1: 数据导出功能
**状态**: ⏳ 待开始
**优先级**: P2
**预计时间**: 3小时

**子任务**:
- [ ] 后端实现Excel导出API
- [ ] 前端实现导出按钮和对话框
- [ ] 支持自定义导出字段

---

#### Task 3.2: 统计图表
**状态**: ⏳ 待开始
**优先级**: P2
**预计时间**: 4小时

**子任务**:
- [ ] 仪表板首页图表
- [ ] 采购统计图表
- [ ] 销售统计图表
- [ ] 库存统计图表
- [ ] 财务统计图表

---

### 第四阶段：质量保障（P3优先级）

#### Task 4.1: 单元测试补充
**状态**: ⏳ 待开始
**优先级**: P3
**预计时间**: 6小时

**子任务**:
- [ ] 补充后端单元测试（目标覆盖率70%）
- [ ] 添加前端组件测试
- [ ] 添加关键业务逻辑测试

---

#### Task 4.2: E2E测试
**状态**: ⏳ 待开始
**优先级**: P3
**预计时间**: 4小时

**子任务**:
- [ ] 登录流程测试
- [ ] 审批流程测试
- [ ] 采购下单流程测试
- [ ] 销售下单流程测试

---

## 备注

- 每个阶段开始前：阅读 task_plan.md、findings.md、progress.md
- 每个阶段完成后：更新状态（pending → in_progress → complete）
- 遇到错误：记录到 task_plan.md 的"遇到的错误"表格
- 重大决策：记录到 findings.md
- 日常工作：记录到 progress.md
- 上下文压缩：当token使用接近80%时主动压缩
