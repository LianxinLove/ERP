"""
自定义异常模块

@description 定义应用中使用的自定义异常类

@features
- 统一的异常格式
- 详细的错误信息
- 多语言支持准备
"""

from typing import Any, Dict, Optional


class APIException(Exception):
    """
    API基础异常类

    所有API异常的基类，提供统一的异常格式
    """

    status_code: int = 500
    message: str = "服务器错误"
    errors: Optional[Dict[str, Any]] = None

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        errors: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        初始化API异常

        Args:
            message: 错误消息
            status_code: HTTP状态码
            errors: 详细错误信息
        """
        self.message = message
        self.status_code = status_code
        self.errors = errors
        super().__init__(message)


class BadRequestError(APIException):
    """400 Bad Request - 请求参数错误"""

    def __init__(self, message: str = "请求参数错误", errors: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, status_code=400, errors=errors)


class UnauthorizedError(APIException):
    """401 Unauthorized - 未授权"""

    def __init__(self, message: str = "未授权访问", errors: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, status_code=401, errors=errors)


class ForbiddenError(APIException):
    """403 Forbidden - 禁止访问"""

    def __init__(self, message: str = "没有权限执行此操作", errors: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, status_code=403, errors=errors)


class NotFoundError(APIException):
    """404 Not Found - 资源不存在"""

    def __init__(self, message: str = "请求的资源不存在", errors: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, status_code=404, errors=errors)


class ConflictError(APIException):
    """409 Conflict - 资源冲突"""

    def __init__(self, message: str = "资源冲突", errors: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, status_code=409, errors=errors)


class ValidationError(APIException):
    """422 Unprocessable Entity - 数据验证错误"""

    def __init__(self, message: str = "数据验证失败", errors: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, status_code=422, errors=errors)
