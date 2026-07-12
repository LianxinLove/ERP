"""
速率限制配置模块

@description 使用 slowapi 实现 API 速率限制，防止暴力破解和 DoS 攻击
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse


# 创建速率限制器实例
limiter = Limiter(
    key_func=lambda: "0.0.0.0",  # 临时禁用 IP 获取，使用固定值
    default_limits=["200/hour"],  # 默认限制：每小时 200 次
    storage_uri="",  # 使用内存存储（生产环境建议使用 Redis）
    headers_enabled=True,  # 在响应头中包含速率限制信息
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    速率限制超出时的处理器

    Args:
        request: FastAPI 请求对象
        exc: 速率限制异常

    Returns:
        JSONResponse: 错误响应
    """
    return JSONResponse(
        status_code=429,
        content={
            "success": False,
            "data": None,
            "message": "请求过于频繁，请稍后再试",
            "errors": {
                "detail": f"速率限制: {exc.detail}",
                "retry_after": str(exc.retry_after) if hasattr(exc, 'retry_after') else None
            }
        },
    )


# 速率限制配置
RATE_LIMITS = {
    # 认证相关端点 - 严格限制
    "login": "5/minute",      # 登录：每分钟 5 次
    "register": "3/hour",     # 注册：每小时 3 次
    "forgot_password": "3/hour",  # 忘记密码：每小时 3 次
    "reset_password": "5/hour",   # 重置密码：每小时 5 次

    # 一般 API 端点 - 中等限制
    "default": "60/minute",   # 默认：每分钟 60 次

    # 批量操作 - 宽松限制
    "bulk": "10/minute",     # 批量操作：每分钟 10 次
}
