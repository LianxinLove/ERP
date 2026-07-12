"""
API 文档配置
@description Swagger UI 和 ReDoc 配置
"""

from typing import List
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.core.config import settings


# API 标签定义
API_TAGS: List[dict] = [
    {
        "name": "健康检查",
        "description": "系统健康状态检查接口",
    },
    {
        "name": "认证",
        "description": "用户认证相关接口，包括注册、登录、令牌刷新等",
    },
    {
        "name": "角色权限",
        "description": "基于 RBAC 的角色和权限管理接口",
    },
    {
        "name": "组织架构",
        "description": "部门、职位、员工档案管理接口",
    },
    {
        "name": "审批流程",
        "description": "工作流引擎相关接口，包括流程定义、实例管理、任务处理",
    },
    {
        "name": "采购管理",
        "description": "采购申请、采购订单、供应商管理接口",
    },
    {
        "name": "销售管理",
        "description": "销售订单、销售退货、客户管理接口",
    },
    {
        "name": "库存管理",
        "description": "仓库、产品、库存、调拨管理接口",
    },
    {
        "name": "财务管理",
        "description": "会计科目、应收应付、收付款管理接口",
    },
]


def configure_openapi(app: FastAPI) -> None:
    """配置 OpenAPI 文档"""

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=settings.PROJECT_NAME,
            version="1.0.0",
            description="""
# ERP 系统 API 文档

## 概述
这是一个完整的 ERP 系统后端 API，提供了以下核心功能：

### 认证与授权
- JWT 令牌认证（Access Token + Refresh Token）
- 基于 RBAC 的权限控制
- 会话管理

### 业务模块
- **组织架构**：部门管理、职位管理、员工档案
- **审批流程**：工作流引擎、流程定义、审批任务
- **采购管理**：供应商、采购申请、采购订单
- **销售管理**：客户、销售订单、销售退货
- **库存管理**：仓库、产品、库存、调拨
- **财务管理**：会计科目、应收应付、收付款

## 认证方式
API 使用 JWT Bearer Token 认证。在请求头中添加：
```
Authorization: Bearer <access_token>
```

## 错误响应
所有错误响应遵循以下格式：
```json
{
  "detail": "错误描述信息"
}
```

## 状态码
- `200` - 成功
- `201` - 创建成功
- `204` - 无内容（通常用于删除操作）
- `400` - 请求参数错误
- `401` - 未认证
- `403` - 权限不足
- `404` - 资源不存在
- `422` - 参数验证失败
- `500` - 服务器错误
            """,
            routes=app.routes,
            tags=API_TAGS,
        )

        # 添加服务器配置
        openapi_schema["servers"] = [
            {"url": "http://localhost:8000", "description": "本地开发服务器"},
            {"url": settings.API_BASE_URL, "description": "生产服务器"}
        ] if hasattr(settings, 'API_BASE_URL') else [
            {"url": "http://localhost:8000", "description": "本地开发服务器"}
        ]

        # 添加安全定义
        openapi_schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "使用 JWT 访问令牌进行认证"
            }
        }

        # 添加全局安全要求
        openapi_schema["security"] = [{"BearerAuth": []}]

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi


# 联系信息
CONTACT_INFO = {
    "name": "ERP System Support",
    "email": "support@erp-system.com",
}

# 许可证信息
LICENSE_INFO = {
    "name": "MIT License",
    "url": "https://opensource.org/licenses/MIT",
}
