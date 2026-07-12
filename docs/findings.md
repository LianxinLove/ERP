# 技术决策与发现

## 项目需求

### 功能需求
1. **账号系统**
   - 用户注册、登录、登出
   - 密码重置（忘记密码）
   - 用户信息管理
   - 会话管理（多设备登录控制）

2. **角色权限控制 (RBAC)**
   - 角色管理（创建、编辑、删除）
   - 权限管理（模块级、操作级）
   - 用户角色分配
   - 动态权限检查

3. **审批流程引擎**
   - 可配置的审批流程
   - 流程设计器（可视化）
   - 支持串行、并行、条件分支
   - 审批操作：通过、拒绝、退回、转办、加签

4. **ERP基础模块**
   - 组织架构（部门、职位、员工）
   - 采购管理（供应商、采购申请、采购订单）
   - 销售管理（客户、销售订单、销售退货）
   - 库存管理（仓库、产品、库存流水）
   - 财务管理（应收应付、收付款）

### 非功能需求
- 代码清晰简洁，高可维护性
- 完善的中文注释
- 错误边界控制
- 响应式设计
- 性能优化

---

## 技术决策

### 架构决策

| 决策 | 技术选型 | 理由 |
|------|---------|------|
| 前端框架 | Next.js 14 (App Router) | 最新架构，支持RSC，服务端渲染性能好 |
| 开发语言 | TypeScript | 类型安全，IDE支持好，减少运行时错误 |
| UI组件库 | shadcn/ui | 可复制粘贴的组件，完全可定制，基于Radix UI |
| 状态管理 | Zustand | 轻量级，TypeScript友好，API简洁 |
| 数据获取 | React Query | 服务端状态管理，自动缓存和重试 |
| 表单处理 | React Hook Form + Zod | 性能好，类型安全，验证强大 |
| 后端框架 | FastAPI | 现代Python框架，自动文档，类型提示 |
| 数据库ORM | SQLAlchemy | 成熟稳定，功能完整，Python生态标准 |
| 数据库迁移 | Alembic | SQLAlchemy官方迁移工具 |
| 数据验证 | Pydantic | 类型验证，与FastAPI深度集成 |
| 认证方式 | JWT (Access + Refresh) | 无状态，易于扩展，前后端分离友好 |
| 密码加密 | bcrypt | 业界标准，自适应哈希 |
| API文档 | Swagger (自动生成) | FastAPI自带，交互式文档 |
| 代码格式化 | Black (Python), Prettier (TS) | 统一代码风格 |
| 代码检查 | Ruff (Python), ESLint (TS) | 快速，准确 |

### 项目结构决策

**采用 Monorepo 结构**，使用 Turborepo 管理：

```
erp-system/
├── apps/
│   ├── frontend/          # Next.js 前端应用
│   │   ├── app/           # App Router页面
│   │   ├── components/    # 公共组件
│   │   ├── lib/           # 工具函数
│   │   ├── hooks/         # 自定义Hooks
│   │   ├── styles/        # 样式文件
│   │   └── public/        # 静态资源
│   │
│   └── backend/           # FastAPI 后端应用
│       ├── app/
│       │   ├── api/       # API路由
│       │   ├── models/    # 数据库模型
│       │   ├── schemas/   # Pydantic模式
│       │   ├── services/  # 业务逻辑
│       │   ├── core/      # 核心配置
│       │   └── utils/     # 工具函数
│       ├── alembic/       # 数据库迁移
│       └── tests/         # 测试文件
│
├── packages/               # 共享包
│   ├── types/             # 共享TypeScript类型
│   ├── ui/                # 共享UI组件
│   └── config/            # 共享配置
│
├── docs/                   # 项目文档
├── docker/                 # Docker配置
└── package.json           # 根package.json
```

### 数据库设计原则

1. **命名规范**
   - 表名：蛇形命名法 (snake_case)，复数形式
   - 字段名：蛇形命名法
   - 索引名：`idx_表名_字段名`
   - 外键名：`fk_表名_字段名`

2. **通用字段**
   - `id`: BIGINT UNSIGNED, 主键, 自增
   - `created_at`: DATETIME, 创建时间, NOT NULL
   - `updated_at`: DATETIME, 更新时间, NOT NULL
   - `created_by`: BIGINT, 创建人ID
   - `updated_by`: BIGINT, 更新人ID
   - `is_deleted`: BOOLEAN, 删除标记, 默认FALSE
   - `deleted_at`: DATETIME, 删除时间

3. **索引规范**
   - 主键自动创建索引
   - 外键创建索引
   - 常用查询条件创建索引
   - 联合索引考虑最左前缀原则

### API设计规范

1. **RESTful风格**
   - GET：查询
   - POST：创建
   - PUT：完整更新
   - PATCH：部分更新
   - DELETE：删除

2. **响应格式**
```json
{
  "success": true,
  "data": {},
  "message": "操作成功",
  "errors": null
}
```

3. **错误响应**
```json
{
  "success": false,
  "data": null,
  "message": "错误描述",
  "errors": {
    "field": ["错误详情"]
  }
}
```

4. **分页响应**
```json
{
  "success": true,
  "data": {
    "items": [],
    "total": 100,
    "page": 1,
    "page_size": 10,
    "total_pages": 10
  }
}
```

### 前端代码规范

1. **组件命名**
   - 文件名：PascalCase (UserProfile.tsx)
   - 组件名：PascalCase
   - Hook名：camelCase，以use开头 (useUser)
   - 工具函数：camelCase

2. **文件组织**
```
components/
├── ui/                 # shadcn/ui基础组件
├── features/           # 功能组件
│   └── auth/
│       ├── LoginForm.tsx
│       └── RegisterForm.tsx
└── shared/             # 共享业务组件
    ├── DataTable.tsx
    └── SearchForm.tsx
```

3. **注释规范**
```typescript
/**
 * 用户登录表单组件
 * 
 * @description 提供用户登录功能，支持邮箱/手机号登录
 * 
 * @features
 * - 记住我功能
 * - 自动Token刷新
 * - 错误提示
 * 
 * @example
 * ```tsx
 * <LoginForm onSuccess={() => navigate('/dashboard')} />
 * ```
 */
```

4. **错误边界**
- 每个页面级组件包裹ErrorBoundary
- 使用React Query的错误处理
- Toast通知用户错误信息

### 后端代码规范

1. **目录组织**
```
app/
├── api/
│   ├── v1/
│   │   ├── endpoints/    # API端点
│   │   └── api.py        # 路由注册
│   └── deps.py           # 依赖注入
├── core/
│   ├── config.py         # 配置
│   ├── security.py       # 安全相关
│   └── database.py       # 数据库
├── models/               # SQLAlchemy模型
├── schemas/              # Pydantic模式
├── services/             # 业务逻辑
└── utils/                # 工具函数
```

2. **注释规范**
```python
class UserService:
    """
    用户服务层
    
    负责用户相关的业务逻辑处理，包括用户创建、更新、删除等操作。
    所有密码相关操作均在内部处理，不对上层暴露敏感信息。
    """
    
    def create_user(self, user_data: UserCreate) -> User:
        """
        创建新用户
        
        Args:
            user_data: 用户创建数据，包含用户名、邮箱、密码等信息
            
        Returns:
            User: 创建成功的用户对象（不含密码）
            
        Raises:
            DuplicateUserError: 当用户名或邮箱已存在时
            ValidationError: 当输入数据验证失败时
            
        Note:
            密码会自动使用bcrypt加密后存储
        """
```

3. **错误处理**
```python
# 使用自定义异常
from app.core.exceptions import BadRequestError, NotFoundError

# API中使用
raise BadRequestError("用户名已存在")
raise NotFoundError("用户不存在")
```

---

## 遇到的问题

| 问题 | 解决方案 |
|------|---------|
|      |         |
| FastAPI Literal类型验证空字符串返回422 | 将 `Optional[EnumType]` 改为 `Optional[str]`，在函数内手动验证空字符串 |

---

## API查询参数最佳实践（2024-06-21）

### 问题发现
当前端使用空字符串作为"无筛选"条件时（如 `?status=`），FastAPI 的 Literal 类型验证会返回 422 错误。

### 解决方案
对于可选的枚举类型查询参数，使用以下模式：

```python
# ❌ 错误写法 - 空字符串会触发验证错误
status: Annotated[Optional[StatusEnum], Query()] = None,

# ✅ 正确写法 - 手动验证空字符串
status: Annotated[Optional[str], Query()] = None,

# 在函数中验证和转换
def get_items(status: Optional[str] = None):
    validated_status = status if status and status.strip() else None
    return service.get_items(status=validated_status)
```

### 应用范围
此模式应用于所有使用枚举类型的可选查询参数：
- 状态筛选（status）
- 类型筛选（type）
- 其他可选的枚举参数

---

## 参考资源

- Next.js文档: https://nextjs.org/docs
- FastAPI文档: https://fastapi.tiangolo.com/
- shadcn/ui: https://ui.shadcn.com/
- SQLAlchemy: https://docs.sqlalchemy.org/
- React Query: https://tanstack.com/query/latest

---

*技术决策随项目进展持续更新*
