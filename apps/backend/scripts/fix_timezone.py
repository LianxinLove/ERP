"""
时区处理修复脚本

自动将 datetime.utcnow() 替换为 datetime.now(timezone.utc)
"""

import os
import re

def fix_timezone_in_file(file_path: str) -> int:
    """
    修复文件中的时区处理

    Args:
        file_path: 文件路径

    Returns:
        int: 替换的数量
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否已经导入了 timezone
    has_timezone_import = 'from datetime import timezone' in content or 'from datetime import' in content and 'timezone' in content

    # 替换 datetime.utcnow() 为 datetime.now(timezone.utc)
    pattern = r'datetime\.utcnow\(\)'
    replacement = 'datetime.now(timezone.utc)'

    matches = re.findall(pattern, content)
    count = len(matches)

    if count > 0:
        content = re.sub(pattern, replacement, content)

        # 如果没有 timezone 导入，需要添加
        if not has_timezone_import:
            # 检查 datetime 导入语句
            datetime_import = re.search(r'from datetime import (.+)', content)
            if datetime_import:
                current_imports = datetime_import.group(1)
                # 检查是否已经包含 timezone
                if 'timezone' not in current_imports:
                    # 添加 timezone 到导入列表
                    new_imports = f"{current_imports}, timezone"
                    content = content.replace(f"from datetime import {current_imports}", new_imports)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"[OK] {file_path}: replaced {count} occurrences")
        return count

    return 0


def main():
    """主函数"""
    # 需要修复的目录
    target_dirs = [
        'services',
        'models',
        'api',
    ]

    total_count = 0

    for dir_name in target_dirs:
        dir_path = os.path.join(os.path.dirname(__file__), '..', 'app', dir_name)

        if not os.path.exists(dir_path):
            continue

        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    count = fix_timezone_in_file(file_path)
                    total_count += count

    print(f"\nTotal replaced {total_count} datetime.utcnow() calls")


if __name__ == '__main__':
    main()
