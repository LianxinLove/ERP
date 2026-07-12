"""
输入验证和清理模块

@description 提供用户输入验证和清理功能，防止XSS等注入攻击
"""

import html
import re
from typing import Optional, Callable


def sanitize_string(text: Optional[str], allow_html: bool = False) -> Optional[str]:
    """
    清理字符串输入，防止XSS攻击

    Args:
        text: 需要清理的字符串
        allow_html: 是否允许HTML标签（默认不允许）

    Returns:
        清理后的字符串，如果输入为None则返回None
    """
    if text is None:
        return None

    if not isinstance(text, str):
        text = str(text)

    if not allow_html:
        # 转义HTML特殊字符
        text = html.escape(text)

    return text


def sanitize_email(email: Optional[str]) -> Optional[str]:
    """
    清理和验证邮箱地址

    Args:
        email: 邮箱地址

    Returns:
        清理后的邮箱地址
    """
    if not email:
        return None

    # 移除前后空格
    email = email.strip()

    # 简单的邮箱格式验证
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return None

    return email.lower()


def sanitize_code(code: Optional[str]) -> Optional[str]:
    """
    清理编码类型的输入（如客户编码、产品编码等）
    只允许字母、数字、下划线和连字符

    Args:
        code: 编码字符串

    Returns:
        清理后的编码
    """
    if not code:
        return None

    # 移除前后空格
    code = code.strip()

    # 只允许安全字符
    code = re.sub(r'[^a-zA-Z0-9_\-]', '', code)

    return code if code else None


def sanitize_filename(filename: Optional[str]) -> Optional[str]:
    """
    清理文件名，防止路径遍历攻击

    Args:
        filename: 文件名

    Returns:
        清理后的文件名
    """
    if not filename:
        return None

    # 移除路径遍历字符
    filename = filename.replace('..', '').replace('/', '').replace('\\', '')

    # 移除隐藏文件标记
    if filename.startswith('.'):
        filename = filename.lstrip('.')

    return filename if filename else None


def sanitize_url(url: Optional[str]) -> Optional[str]:
    """
    清理URL，防止javascript:等伪协议攻击

    Args:
        url: URL字符串

    Returns:
        清理后的URL，如果检测到危险协议则返回None
    """
    if not url:
        return None

    url = url.strip()

    # 检查危险协议
    dangerous_protocols = ['javascript:', 'data:', 'vbscript:', 'file:']
    url_lower = url.lower()
    for protocol in dangerous_protocols:
        if url_lower.startswith(protocol):
            return None

    # 只允许http和https协议
    if not url_lower.startswith(('http://', 'https://')):
        return None

    return url


def sanitize_sql_like(text: Optional[str]) -> Optional[str]:
    """
    清理用于SQL LIKE查询的字符串，转义特殊字符

    Args:
        text: 需要用于LIKE查询的字符串

    Returns:
        转义后的字符串
    """
    if not text:
        return None

    # 转义SQL LIKE通配符
    text = text.replace('\\', '\\\\')
    text = text.replace('%', '\\%')
    text = text.replace('_', '\\_')

    return text


class SanitizableMixin:
    """
    可清理的模型混合类

    为模型提供自动清理功能
    """

    def sanitize_fields(self, field_names: list[str]) -> None:
        """
        清理指定的字段

        Args:
            field_names: 需要清理的字段名称列表
        """
        for field_name in field_names:
            if hasattr(self, field_name):
                value = getattr(self, field_name)
                if isinstance(value, str):
                    setattr(self, field_name, sanitize_string(value))
            elif hasattr(self, f'get_{field_name}'):
                # 处理Pydantic模型
                getter = getattr(self, f'get_{field_name}')
                value = getter()
                if value:
                    setattr(self, field_name, sanitize_string(value))


# 常用的清理函数组合
def sanitize_user_input(data: dict, rules: dict[str, Callable]) -> dict:
    """
    批量清理用户输入

    Args:
        data: 用户输入数据字典
        rules: 清理规则字典，key为字段名，value为清理函数

    Returns:
        清理后的数据字典
    """
    result = {}
    for key, value in data.items():
        if key in rules and value is not None:
            result[key] = rules[key](value)
        else:
            result[key] = value
    return result
