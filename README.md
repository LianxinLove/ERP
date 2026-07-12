# ERP 企业资源计划系统

> 一个现代化的企业资源计划管理系统，采用前后端分离架构，使用 AI 辅助开发完成。

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![Node.js](https://img.shields.io/badge/node.js-18+-green.svg)

## 项目简介

本项目是一个功能完善的企业资源计划（ERP）系统，旨在为中小企业提供一体化的业务管理解决方案。系统采用现代化的技术栈和清晰的架构设计，涵盖企业核心业务流程的管理。

### 核心特性

- **🔐 权限管理** - 基于 RBAC 的角色权限控制系统
- **👥 组织架构** - 部门、职位、员工管理
- **📋 审批流程** - 可视化工作流引擎
- **📦 库存管理** - 仓库、产品、库存流水管理
- **🛒 采购管理** - 供应商、采购申请、采购订单
- **💰 销售管理** - 客户、销售订单、销售退货
- **💳 财务管理** - 应收应付、收付款记录、科目管理
- **📢 通知系统** - 多渠道消息通知

## 技术栈

### 前端
| 技术 | 版本 | 说明 |
|------|------|------|
| Next.js | 14 | React 服务端渲染框架 |
| TypeScript | 5+ | 类型安全的 JavaScript 超集 |
| shadcn/ui | - | 现代化 UI 组件库 |
| Tailwind CSS | 3+ | 原子化 CSS 框架 |
| Zustand | 4+ | 轻量级状态管理 |
| React Query | 5+ | 服务端状态管理 |

### 后端
| 技术 | 版本 | 说明 |
|------|------|------|
| Python | 3.11+ | 编程语言 |
| FastAPI | 0.110+ | 现代化 Web 框架 |
| SQLAlchemy | 2.0+ | ORM 工具 |
| Pydantic | 2.0+ | 数据验证 |
| MySQL | 8.0+ | 关系型数据库 |

## 项目结构

```
erp-system/
├── apps/                    # 应用目录
│   ├── frontend/           # Next.js 前端应用
│   │   ├── src/            # 源代码
│   │   │   ├── app/        # 页面路由
│   │   │   ├── components/ # 组件
│   │   │   ├── lib/        # 工具函数
│   │   │   └── types/      # 类型定义
│   │   ├── public/         # 静态资源
│   │   └── package.json
│   └── backend/           # FastAPI 后端应用
│       ├── app/           # 应用代码
│       │   ├── api/       # API 路由
│       │   ├── core/      # 核心配置
│       │   ├── models/    # 数据模型
│       │   ├── schemas/   # 数据验证
│       │   └── services/  # 业务逻辑
│       ├── tests/         # 测试代码
│       └── pyproject.toml
├── docs/                  # 项目文档
├── nginx/                 # Nginx 配置
├── docker-compose.yml      # Docker 编排配置
└── README.md              # 项目说明
```

## 快速开始

### 前置要求

- Node.js 18+
- Python 3.11+
- MySQL 8.0+
- pnpm (推荐) 或 npm

### 安装依赖

```bash
# 前端依赖
cd apps/frontend
pnpm install

# 后端依赖
cd apps/backend
pip install -r requirements.txt
```

### 环境配置

#### 前端配置

复制 `.env.example` 创建 `.env` 文件：

```bash
cp apps/frontend/.env.example apps/frontend/.env
```

编辑 `.env` 文件配置必要的环境变量。

#### 后端配置

复制 `.env.example` 创建 `.env` 文件：

```bash
cp apps/backend/.env.example apps/backend/.env
```

编辑 `.env` 文件配置数据库连接等信息。

### 数据库初始化

```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE erp_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 运行数据库迁移
cd apps/backend
python -m alembic upgrade head

# 初始化权限数据
python scripts/init_rbac.py
```

### 启动开发服务器

```bash
# 启动后端 (终端 1)
cd apps/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 启动前端 (终端 2)
cd apps/frontend
pnpm dev
```

### 访问应用

- 前端应用: http://localhost:3000
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

## 功能模块

### 账号系统
- 用户注册/登录
- 密码重置
- 会话管理
- JWT 认证

### 权限管理
- 角色管理
- 权限管理
- 用户角色分配
- 数据权限控制

### 组织架构
- 部门管理（树形结构）
- 职位管理
- 员工管理

### 库存管理
- 仓库管理
- 产品管理
- 库存流水
- 库存调拨
- 序列号管理

### 采购管理
- 供应商管理
- 采购申请
- 采购订单
- 采购入库

### 销售管理
- 客户管理
- 销售订单
- 销售出库
- 退货管理

### 财务管理
- 科目管理
- 应收账款
- 应付账款
- 收付款记录
- 财务报表

### 工作流引擎
- 流程设计
- 审批节点
- 流程实例
- 待办任务

## 开发指南

### 代码规范

- Python: 遵循 PEP 8 规范
- TypeScript: 使用 ESLint + Prettier
- 提交信息: 遵循约定式提交规范

### 测试

```bash
# 后端测试
cd apps/backend
pytest tests/

# 前端类型检查
cd apps/frontend
pnpm type-check
```

### API 文档

后端使用 FastAPI 自动生成交互式 API 文档：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Docker 部署

使用 Docker Compose 快速部署：

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 项目文档

- [开发规范](./docs/CONSTRAINTS.md)
- [数据库设计](./docs/database-design.md)
- [部署指南](./docs/deployment.md)
- [用户手册](./docs/user-guide.md)

## 贡献指南

欢迎贡献代码、报告问题或提出改进建议！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系方式

- 项目地址: [GitHub](https://github.com/LianxinLove/ERP)
- 问题反馈: [Issues](https://github.com/LianxinLove/ERP/issues)

---

**开发开始日期：2024-06-20**  
**最后更新：2024-07-12**

使用 ❤️ 和 AI 辅助开发完成
