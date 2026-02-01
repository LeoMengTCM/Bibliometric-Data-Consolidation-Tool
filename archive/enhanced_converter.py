import os
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版Scopus转WOS转换器（集成WOS标准化）

在原有转换基础上，增加AI驱动的WOS格式标准化：
1. 作者名去重音符号
2. 国家名WOS标准化
3. 期刊名WOS标准缩写

作者：Meng Linghan
开发工具：Claude Code
日期：2025-11-11
版本：v1.0
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional
from scopus_to_wos_converter import ScopusToWosConverter
from wos_standardizer import WOSStandardizer
from gemini_config import GeminiConfig

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class EnhancedConverter:
    """增强版转换器（集成WOS标准化）"""

    def __init__(self, input_file: str, output_file: str, enable_standardization: bool = True):
        self.input_file = input_file
        self.output_file = output_file
        self.enable_standardization = enable_standardization

        # 创建基础转换器
        self.converter = ScopusToWosConverter(input_file, output_file)

        # 创建WOS标准化器
        if enable_standardization:
            config = GeminiConfig.from_params(
                api_key=os.getenv('GEMINI_API_KEY', 'YOUR_API_KEY'),
                api_url=os.getenv('GEMINI_API_URL', 'https://your-api-gateway.com/proxy/bibliometrics/v1beta'),
                model='gemini-2.5-flash-lite'
            )
            self.standardizer = WOSStandardizer(config)
        else:
            self.standardizer = None

    def convert(self):
        """执行转换（带WOS标准化）"""
        logger.info("=" * 80)
        logger.info("增强版Scopus转WOS转换器")
        logger.info("=" * 80)
        logger.info(f"输入文件: {self.input_file}")
        logger.info(f"输出文件: {self.output_file}")
        logger.info(f"WOS标准化: {'启用' if self.enable_standardization else '禁用'}")
        logger.info("=" * 80)
        logger.info("")

        # 步骤1: 基础转换
        logger.info("步骤1: 执行基础格式转换...")
        self.converter.convert()

        if not self.enable_standardization:
            logger.info("✓ 转换完成（未启用WOS标准化）")
            return

        # 步骤2: WOS标准化
        logger.info("")
        logger.info("步骤2: 执行WOS格式标准化...")
        self._standardize_wos_file()

        # 保存数据库
        self.standardizer.db.save_database()

        # 打印统计
        self._print_statistics()

        logger.info("")
        logger.info("=" * 80)
        logger.info("✓ 增强版转换完成！")
        logger.info("=" * 80)

    def _standardize_wos_file(self):
        """标准化WOS文件"""
        # 读取转换后的文件
        with open(self.output_file, 'r', encoding='utf-8-sig') as f:
            content = f.read()

        # 解析记录
        records = self._parse_wos_file(content)
        logger.info(f"解析了 {len(records)} 条记录")

        # 标准化每条记录
        for i, record in enumerate(records, 1):
            if i % 10 == 0:
                logger.info(f"进度: {i}/{len(records)}")

            # 标准化AU字段（作者简写）
            if 'AU' in record:
                authors = [line.strip() for line in record['AU'].split('\n') if line.strip()]
                standardized = [self.standardizer.standardize_author(au) for au in authors]
                record['AU'] = '\n'.join(standardized)

            # 标准化AF字段（作者全名）
            if 'AF' in record:
                authors = [line.strip() for line in record['AF'].split('\n') if line.strip()]
                standardized = [self.standardizer.standardize_author(au) for au in authors]
                record['AF'] = '\n'.join(standardized)

            # 标准化C1字段中的国家
            if 'C1' in record:
                record['C1'] = self._standardize_c1_countries(record['C1'])

            # 标准化SO字段（期刊名）
            if 'SO' in record:
                record['SO'] = self.standardizer.standardize_journal(record['SO'])

        # 写回文件
        self._write_wos_file(records)

        logger.info(f"✓ WOS标准化完成")

    def _standardize_c1_countries(self, c1_text: str) -> str:
        """标准化C1字段中的国家名"""
        lines = c1_text.split('\n')
        standardized_lines = []

        for line in lines:
            # 提取国家（最后一个逗号后的部分，句号前）
            match = re.search(r',\s*([^,]+)\.$', line)
            if match:
                country = match.group(1).strip()
                wos_country = self.standardizer.standardize_country(country)
                line = line.replace(f', {country}.', f', {wos_country}.')

            standardized_lines.append(line)

        return '\n'.join(standardized_lines)

    def _parse_wos_file(self, content: str) -> List[Dict[str, str]]:
        """解析WOS文件"""
        records = []
        record_blocks = content.split('\n\nPT ')[1:]

        for block in record_blocks:
            block = 'PT ' + block
            record = self._parse_record(block)
            if record:
                records.append(record)

        return records

    def _parse_record(self, block: str) -> Dict[str, str]:
        """解析单条记录"""
        record = {}
        lines = block.split('\n')

        current_field = None
        current_value = []

        for line in lines:
            if line.strip() == 'ER':
                if current_field:
                    record[current_field] = '\n'.join(current_value)
                break

            if len(line) >= 3 and line[:2].isupper() and line[2] == ' ':
                if current_field:
                    record[current_field] = '\n'.join(current_value)
                current_field = line[:2]
                current_value = [line[3:]]
            elif line.startswith('   ') and current_field:
                current_value.append(line[3:])

        return record

    def _write_wos_file(self, records: List[Dict]):
        """写入WOS文件"""
        with open(self.output_file, 'w', encoding='utf-8-sig') as f:
            f.write('FN Clarivate Analytics Web of Science\n')
            f.write('VR 1.0\n')

            for record in records:
                f.write('\nPT J\n')

                field_order = ['AU', 'AF', 'TI', 'SO', 'LA', 'DT', 'DE', 'ID', 'AB',
                              'C1', 'C3', 'RP', 'CR', 'NR', 'TC', 'Z9', 'U1', 'U2',
                              'PU', 'SN', 'J9', 'JI', 'PY', 'VL', 'IS', 'AR', 'DI',
                              'WE', 'UT', 'PM', 'DA']

                for field in field_order:
                    if field in record:
                        value = record[field]
                        lines = value.split('\n')
                        f.write(f'{field} {lines[0]}\n')
                        for line in lines[1:]:
                            f.write(f'   {line}\n')

                f.write('ER\n')

            f.write('\nEF\n')

    def _print_statistics(self):
        """打印统计信息"""
        stats = self.standardizer.get_statistics()

        print("\n" + "=" * 80)
        print("WOS标准化统计")
        print("=" * 80)
        print()
        print("【作者名标准化】")
        print(f"  数据库命中: {stats['authors']['hits']}")
        print(f"  AI调用: {stats['authors']['misses']}")
        print(f"  命中率: {stats['authors']['hit_rate']}")
        print()
        print("【国家名标准化】")
        print(f"  数据库命中: {stats['countries']['hits']}")
        print(f"  AI调用: {stats['countries']['misses']}")
        print(f"  命中率: {stats['countries']['hit_rate']}")
        print()
        print("【期刊名标准化】")
        print(f"  数据库命中: {stats['journals']['hits']}")
        print(f"  AI调用: {stats['journals']['misses']}")
        print(f"  命中率: {stats['journals']['hit_rate']}")
        print("=" * 80)


def main():
    """命令行工具"""
    import argparse
    import re

    parser = argparse.ArgumentParser(
        description='增强版Scopus转WOS转换器（集成WOS标准化）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 启用WOS标准化（推荐）
  python3 enhanced_converter.py scopus.csv output.txt

  # 禁用WOS标准化（仅基础转换）
  python3 enhanced_converter.py scopus.csv output.txt --no-standardization

WOS标准化功能:
  - 作者名去重音符号（Pénault-Llorca → Penault-Llorca）
  - 国家名WOS标准化（China → Peoples R China）
  - 期刊名WOS标准缩写（Journal of XXX → J XXX）
  - 数据库记忆，越用越快
        """
    )

    parser.add_argument('input', help='输入Scopus CSV文件')
    parser.add_argument('output', help='输出WOS文本文件')
    parser.add_argument('--no-standardization', action='store_true',
                       help='禁用WOS标准化（仅基础转换）')

    args = parser.parse_args()

    # 创建转换器
    converter = EnhancedConverter(
        args.input,
        args.output,
        enable_standardization=not args.no_standardization
    )

    # 执行转换
    converter.convert()


if __name__ == '__main__':
    main()
