#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动替换硬编码API密钥为环境变量
"""

import os
import re
from pathlib import Path

# 需要修改的文件列表
FILES_TO_MODIFY = [
    'enhanced_converter_batch_v2.py',
    'wos_standardizer_batch.py',
    'run_ai_workflow.py',
    'gemini_enricher_v2.py',
    'wos_standardizer.py',
    'enhanced_converter.py',
    'institution_enricher_v2.py',
    'gemini_config.py',
]

# 替换规则
REPLACEMENTS = [
    # API密钥替换
    (
        r"api_key\s*=\s*['\"]sk-leomeng1997['\"]",
        "api_key=os.getenv('GEMINI_API_KEY', 'YOUR_API_KEY')"
    ),
    # API URL替换
    (
        r"api_url\s*=\s*['\"]https://gptload\.drmeng\.top/proxy/bibliometrics/v1beta['\"]",
        "api_url=os.getenv('GEMINI_API_URL', 'https://your-api-gateway.com/proxy/bibliometrics/v1beta')"
    ),
]

def add_imports_if_missing(content):
    """添加必要的import（如果缺失）"""
    if 'import os' not in content:
        # 在文件开头添加 import os
        content = 'import os\n' + content
    return content

def replace_hardcoded_keys(file_path):
    """替换文件中的硬编码密钥"""
    print(f"处理: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # 添加必要的imports
        content = add_imports_if_missing(content)

        # 执行所有替换
        for pattern, replacement in REPLACEMENTS:
            content = re.sub(pattern, replacement, content)

        # 检查是否有修改
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ 已修改")
            return True
        else:
            print(f"  ⏭️  无需修改")
            return False

    except Exception as e:
        print(f"  ❌ 错误: {e}")
        return False

def main():
    """主函数"""
    print("🔧 自动替换硬编码API密钥")
    print("=" * 50)
    print()

    base_dir = Path(__file__).parent
    modified_count = 0

    for filename in FILES_TO_MODIFY:
        file_path = base_dir / filename
        if file_path.exists():
            if replace_hardcoded_keys(file_path):
                modified_count += 1
        else:
            print(f"⚠️  文件不存在: {filename}")

    print()
    print("=" * 50)
    print(f"✅ 完成! 共修改 {modified_count} 个文件")
    print()
    print("📋 下一步:")
    print("1. 创建 .env 文件: cp .env.example .env")
    print("2. 编辑 .env 填入真实的API密钥")
    print("3. 测试代码是否正常工作")
    print("4. 提交修改: git add . && git commit -m 'security: Remove hardcoded API keys'")
    print()

if __name__ == '__main__':
    main()
