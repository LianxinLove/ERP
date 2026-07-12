# ERP 系统开发者指南

## 目录
- [技术架构](#技术架构)
- [开发环境搭建](#开发环境搭建)
- [代码规范](#代码规范)
- [测试指南](#测试指南)
- [部署指南](#部署指南)

---

## 技术架构

### 技术栈

**前端**
- Next.js 14 - React 框架
- TypeScript - 类型安全
- Tailwind CSS - 样式框架
- shadcn/ui - UI 组件库
- React Query - 数据获取
- Zustand - 状态管理

**后端**
- Python 3.11+
- FastAPI - Web 框架
- SQLAlchemy - ORM
- MySQL - 数据库
- Pydantic - 数据验证

### 项目结构

```
erp-system/
├── apps/
│   ├── backend/          # 后端应用
│   │   ├── app/
│   │   │   ├── api/      # API 路由
│   │   │   ├── core/     # 核心配置
│   │   │   ├── models/   # 数据模型
│   │   │   ├── schemas/  # Pydantic 模型
│   │   │   ├── services/ # 业务逻辑
│   │   │   └── main.py   # 应用入口
│   │   └── tests/        # 测试文件
│   └── frontend/         # 前端应用
│       └── src/
│           ├── app/      # 页面路由
│           ├── api/      # API 调用
│           ├── components/  # 组件
│           └── lib/      # 工具函数
├── packages/
│   └── types/           # 共享类型定义
└── docs/                 # 项目文档
```

---

## 开发环境搭建

### 前置要求

- Node.js 18+
- Python 3.11+
- pnpm 8+
- MySQL 8.0+

### 后端环境

```bash
# 进入后端目录
cd apps/backend

# 安装依赖
pip install -e .

# 复制环境变量
cp .env.example .env

# 编辑 .env 文件，配置数据库等信息
# vim .env

# 初始化数据库
python -m app.core.init_db

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端环境

```bash
# 安装依赖
pnpm install

# 复制环境变量
cp apps/frontend/.env.example apps/frontend/.env.local

# 启动开发服务器
pnpm dev
```

---

## 代码规范

### Python 代码规范

遵循 PEP 8 规范，使用以下工具进行代码检查：

```bash
# 代码格式化
black app/
isort app/

# 代码检查
flake8 app/
mypy app/
```

### TypeScript 代码规范

```bash
# 类型检查
pnpm type-check

# 代码检查
pnpm lint

# 代码格式化
pnpm format
```

### 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 类名 | PascalCase | `class UserService` |
| 函数名 | snake_case | `def get_user()` |
| 变量名 | snake_case | `user_id = 1` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRIES = 3` |
| React 组件 | PascalCase | `function DataTable()` |

### 注释规范

**Python 文档字符串**
```python
def create_user(data: UserCreate) -> User:
    """
    创建用户

    Args:
        data: 用户创建数据

    Returns:
        User: 创建的用户对象

    Raises:
        BadRequestError: 用户名已存在
    """
    pass
```

**TypeScript JSDoc**
```typescript
/**
 * 获取用户列表
 * @description 分页获取用户列表
 * @param params 查询参数
 * @returns 用户列表
 */
async function getUsers(params: GetUsersParams): Promise<User[]> {
  // ...
}
```

---

## 测试指南

### 运行测试

**后端测试**
```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_auth.py

# 查看覆盖率
pytest --cov=app tests/
```

**前端测试**
```bash
# 运行测试
pnpm test

# 覆盖率报告
pnpm test:coverage
```

### 编写测试

**后端测试示例**
```python
class TestUserService:
    """用户服务测试"""

    async def test_create_user_success(self, db_session):
        """测试成功创建用户"""
        service = UserService(db_session)
        user = await service.create_user(UserCreate(
            username="test",
            email="test@example.com",
            password="Test123!"
        ))
        assert user.id is not None
        assert user.username == "test"
```

---

## API 开发指南

### 创建新端点

1. 在 `app/api/v1/endpoints/` 创建新文件
2. 定义路由和处理函数
3. 在 `app/api/v1/api.py` 中注册路由

```python
# app/api/v1/endpoints/example.py
from fastapi import APIRouter, Depends
from app.api.deps import get_current_user, get_db

router = APIRouter()

@router.get("/example")
async def get_example(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    return {"message": "Hello"}
```

### 添加权限控制

```python
from app.core.permissions import require_permission

@router.post("/admin")
@require_permission("admin:create")
async def admin_only():
    return {"message": "Admin only"}
```

---

## 数据库迁移

### 创建迁移

```bash
# 使用 Alembic 创建迁移
alembic revision --autogenerate -m "add new column"
```

### 执行迁移

```bash
# 升级到最新版本
alembic upgrade head

# 回退一个版本
alembic downgrade -1
```

---

## 性能优化

### 后端优化

1. 使用数据库索引
2. 实现 Redis 缓存
3. 异步处理耗时任务
4. 使用连接池

### 前端优化

1. 使用 React Query 缓存
2. 实现虚拟滚动
3. 代码分割和懒加载
4. 图片优化

---

## 贡献指南

1. Fork 项目仓库
2. 创建功能分支
3. 编写代码和测试
4. 提交 Pull Request

### Commit 规范

```
feat: 添加新功能
fix: 修复问题
docs: 文档更新
style: 代码格式调整
refactor: 代码重构
test: 测试相关
chore: 构建/工具相关
```

---

## 常见问题

**Q: 如何添加新的数据模型？**
A: 在 `app/models/` 下创建模型文件，定义 SQLAlchemy 模型类。

**Q: 如何添加新的前端页面？**
A: 在 `apps/frontend/src/app/` 下创建页面目录和 `page.tsx` 文件。

**Q: 如何共享类型定义？**
A: 在 `packages/types/src/` 下添加类型文件，前后端通过该包共享类型。

---

*最后更新时间：2024-06-20*
