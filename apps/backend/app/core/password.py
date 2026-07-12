"""
密码验证模块

@description 提供密码强度验证功能

@features
- 密码强度检查
- 密码规则验证
- 密码强度评分
"""

import re
from enum import Enum


class PasswordStrength(Enum):
    """密码强度等级"""
    WEAK = "weak"
    MEDIUM = "medium"
    STRONG = "strong"
    VERY_STRONG = "very_strong"


class PasswordValidationError(Exception):
    """密码验证错误"""
    pass


def validate_password_strength(
    password: str,
    min_length: int = 8,
    max_length: int = 50,
    require_uppercase: bool = True,
    require_lowercase: bool = True,
    require_digit: bool = True,
    require_special: bool = True,
) -> tuple[bool, list[str]]:
    """
    验证密码强度

    Args:
        password: 要验证的密码
        min_length: 最小长度
        max_length: 最大长度
        require_uppercase: 是否要求大写字母
        require_lowercase: 是否要求小写字母
        require_digit: 是否要求数字
        require_special: 是否要求特殊字符

    Returns:
        tuple[bool, list[str]]: (是否通过验证, 错误信息列表)

    Example:
        is_valid, errors = validate_password_strength("MyPass123!")
        if not is_valid:
            print(errors)
    """
    errors = []

    # 检查长度
    if len(password) < min_length:
        errors.append(f"密码长度至少需要 {min_length} 个字符")
    if len(password) > max_length:
        errors.append(f"密码长度不能超过 {max_length} 个字符")

    # 检查大写字母
    if require_uppercase and not re.search(r'[A-Z]', password):
        errors.append("密码必须包含至少一个大写字母")

    # 检查小写字母
    if require_lowercase and not re.search(r'[a-z]', password):
        errors.append("密码必须包含至少一个小写字母")

    # 检查数字
    if require_digit and not re.search(r'\d', password):
        errors.append("密码必须包含至少一个数字")

    # 检查特殊字符
    special_chars = r'[!@#$%^&*(),.?":{}|<>_+\-=\[\]\\]'
    if require_special and not re.search(special_chars, password):
        errors.append("密码必须包含至少一个特殊字符")

    # 检查常见弱密码
    weak_passwords = {
        'password', '12345678', '123456789', 'qwerty123',
        'abc12345', 'password123', 'admin123', 'letmein',
        'welcome1', 'monkey123', 'password1'
    }
    if password.lower() in weak_passwords:
        errors.append("密码过于简单，请使用更复杂的密码")

    return len(errors) == 0, errors


def get_password_strength(password: str) -> PasswordStrength:
    """
    获取密码强度等级

    Args:
        password: 密码

    Returns:
        PasswordStrength: 密码强度等级
    """
    score = 0

    # 长度评分
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if len(password) >= 16:
        score += 1

    # 字符类型评分
    has_lower = bool(re.search(r'[a-z]', password))
    has_upper = bool(re.search(r'[A-Z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>_+\-=\[\]\\]', password))

    char_types = sum([has_lower, has_upper, has_digit, has_special])
    score += char_types

    # 复杂度评分
    if len(password) >= 8 and char_types >= 3:
        score += 1
    if len(password) >= 12 and char_types == 4:
        score += 1

    # 评定等级
    if score <= 3:
        return PasswordStrength.WEAK
    elif score <= 5:
        return PasswordStrength.MEDIUM
    elif score <= 7:
        return PasswordStrength.STRONG
    else:
        return PasswordStrength.VERY_STRONG


def generate_password_suggestions(length: int = 12) -> list[str]:
    """
    生成密码建议

    Args:
        length: 密码长度

    Returns:
        list[str]: 建议密码列表
    """
    import secrets
    import string

    suggestions = []
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*'

    for _ in range(3):
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        suggestions.append(password)

    return suggestions
