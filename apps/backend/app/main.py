"""
ERP系统后端主入口

@description FastAPI应用的初始化和配置

@features
- 自动API文档生成
- CORS跨域配置
- 全局异常处理
- 请求日志记录
- 速率限制
"""

import time
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.exceptions import APIException
from app.core.docs import configure_openapi
# from app.core.rate_limit import limiter, rate_limit_exceeded_handler  # 暂时禁用
from app.api.v1.api import api_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    应用生命周期管理

    Args:
        app: FastAPI应用实例

    Yields:
        None
    """
    # 启动时执行
    print("ERP系统后端启动中...")
    print(f"API地址: http://{settings.API_HOST}:{settings.API_PORT}")
    print(f"API文档: http://{settings.API_HOST}:{settings.API_PORT}/docs")

    yield

    # 关闭时执行
    print("ERP系统后端已关闭")


def create_app() -> FastAPI:
    """
    创建并配置FastAPI应用

    Returns:
        FastAPI: 配置好的应用实例
    """
    app = FastAPI(
        title="ERP系统 API",
        description="企业资源计划系统后端API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # 暂时禁用速率限制
    # app.state.limiter = limiter
    # app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

    # CORS配置
    # 开发环境下如果未配置CORS_ORIGINS，使用安全的默认值
    cors_origins = settings.cors_origins_list
    if settings.DEBUG and not cors_origins:
        cors_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
        print("警告: DEBUG模式下使用默认CORS配置。生产环境必须通过环境变量设置CORS_ORIGINS。")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 请求日志中间件（暂时禁用以调试）
    # @app.middleware("http")
    # async def log_requests(request: Request, call_next):
    #     """记录所有API请求"""
    #     start_time = time.time()
    #
    #     # 记录请求
    #     logger.info(
    #         "API Request",
    #         extra={
    #             "method": request.method,
    #             "url": str(request.url),
    #             "path": request.url.path,
    #             "client_ip": request.client.host if request.client else "unknown",
    #             "user_agent": request.headers.get("user-agent", "unknown"),
    #         }
    #     )
    #
    #     # 处理请求
    #     response = await call_next(request)
    #
    #     # 计算处理时间
    #     process_time = time.time() - start_time
    #
    #     # 记录响应
    #     logger.info(
    #         "API Response",
    #         extra={
    #             "method": request.method,
    #             "path": request.url.path,
    #             "status_code": response.status_code,
    #             "process_time_ms": round(process_time * 1000, 2),
    #         }
    #     )
    #
    #     # 添加处理时间到响应头
    #     response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
    #
    #     return response

    # 注册API路由
    print(f"[DEBUG] Including API router with {len(api_router.routes)} routes")
    try:
        app.include_router(api_router, prefix="/api")
        print(f"[DEBUG] API router included successfully")
        print(f"[DEBUG] Total routes after inclusion: {len(app.routes)}")
    except Exception as e:
        print(f"[DEBUG] Error including API router: {e}")
        import traceback
        traceback.print_exc()

    # 配置OpenAPI文档
    configure_openapi(app)

    # 全局异常处理
    @app.exception_handler(APIException)
    async def api_exception_handler(request, exc: APIException):
        """API异常处理器"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "data": None,
                "message": exc.message,
                "errors": exc.errors,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc: Exception):
        """通用异常处理器"""
        import traceback
        print(f"[ERROR] Exception: {type(exc).__name__}: {exc}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "message": "服务器内部错误",
                "errors": {"detail": str(exc)} if settings.DEBUG else None,
            },
        )

    # 健康检查
    @app.get("/health")
    async def health_check():
        """健康检查端点"""
        return {"status": "ok", "version": "1.0.0"}

    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    )
