#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI Runner for MultiDatabase Workflow
"""

import sys
import os
import argparse
import logging

# Add src to sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from bibliometrics.pipeline.workflow import AIWorkflow

def main():
    """命令行工具"""
    parser = argparse.ArgumentParser(
        description='AI增强的一键式工作流',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本使用（启用AI补全）
  python3 scripts/run_workflow.py --data-dir "/path/to/data"

  # 筛选中文文献
  python3 scripts/run_workflow.py --data-dir "/path/to/data" --language Chinese

  # 禁用AI补全（仅格式转换和合并）
  python3 scripts/run_workflow.py --data-dir "/path/to/data" --no-ai

  # 禁用机构清洗
  python3 scripts/run_workflow.py --data-dir "/path/to/data" --no-cleaning

  # 过滤指定年份范围（如2015-2024）
  python3 scripts/run_workflow.py --data-dir "/path/to/data" --year-range 2015-2024
        """
    )

    parser.add_argument('--data-dir', required=True, help='数据目录（包含wos.txt和scopus.csv）')
    parser.add_argument('--language', default='English', help='目标语言（默认: English）')
    parser.add_argument('--no-ai', action='store_true', help='禁用AI补全')
    parser.add_argument('--no-cleaning', action='store_true', help='禁用机构清洗（默认启用）')
    parser.add_argument('--cleaning-config', default='config/institution_cleaning_rules.json',
                       help='机构清洗规则配置文件（默认: config/institution_cleaning_rules.json）')
    parser.add_argument('--year-range', help='年份范围过滤（格式: YYYY-YYYY，如2015-2024）')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='日志级别')

    args = parser.parse_args()

    # 设置日志级别
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    # 创建工作流
    workflow = AIWorkflow(
        data_dir=args.data_dir,
        language=args.language,
        enable_ai=not args.no_ai,
        enable_cleaning=not args.no_cleaning,
        cleaning_config=args.cleaning_config,
        year_range=args.year_range
    )

    # 运行工作流
    success = workflow.run()

    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
