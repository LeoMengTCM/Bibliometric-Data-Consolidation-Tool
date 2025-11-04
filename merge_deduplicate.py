#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WOS和Scopus文献数据合并去重工具

策略：
1. WOS记录优先保留（WOS数据更完整）
2. Scopus记录用于补充WOS没有的信息
3. 删除Scopus中与WOS重复的记录
4. 保留Scopus中独有的记录

作者：Meng Linghan
开发工具：Claude Code
日期：2025-11-04
版本：v2.1（优化版）

更新日志：
- 添加logging模块支持
- 改进错误处理和文件验证
- 添加进度显示
"""

import re
import os
import logging
from typing import List, Dict, Set, Tuple
from collections import defaultdict

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class WOSRecordParser:
    """WOS格式记录解析器"""

    @staticmethod
    def parse_wos_file(file_path: str) -> List[Dict]:
        """
        解析WOS格式文本文件

        Returns:
            List[Dict]: 记录列表，每条记录是一个字典
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 按ER分割记录（ER是记录结束标记）
        record_texts = re.split(r'\nER\s*\n', content)

        records = []
        for record_text in record_texts:
            if not record_text.strip() or record_text.strip().startswith('EF'):
                continue

            # 解析单条记录
            record = WOSRecordParser.parse_single_record(record_text)
            if record:
                records.append(record)

        return records

    @staticmethod
    def parse_single_record(record_text: str) -> Dict:
        """
        解析单条WOS记录

        格式：
        PT J
        AU Author1
           Author2
        TI Title here
        ...
        """
        record = {}
        current_field = None
        current_value = []

        lines = record_text.split('\n')

        for line in lines:
            # 跳过文件头
            if line.startswith('FN ') or line.startswith('VR '):
                continue

            # 检查是否是新字段（两个字母标签）
            field_match = re.match(r'^([A-Z][A-Z0-9])\s+(.*)$', line)

            if field_match:
                # 保存前一个字段
                if current_field:
                    record[current_field] = '\n'.join(current_value)

                # 开始新字段
                current_field = field_match.group(1)
                current_value = [field_match.group(2)]

            elif line.startswith('   ') and current_field:
                # 续行（3个空格开头）
                current_value.append(line.strip())

            elif line.strip() == '':
                # 空行，保存当前字段
                if current_field:
                    record[current_field] = '\n'.join(current_value)
                    current_field = None
                    current_value = []

        # 保存最后一个字段
        if current_field:
            record[current_field] = '\n'.join(current_value)

        return record


class RecordMatcher:
    """记录匹配器（用于识别重复）"""

    @staticmethod
    def normalize_title(title: str) -> str:
        """标准化标题（用于匹配）"""
        # 转小写
        title = title.lower()
        # 移除标点
        title = re.sub(r'[^\w\s]', '', title)
        # 移除多余空格
        title = re.sub(r'\s+', ' ', title).strip()
        return title

    @staticmethod
    def get_first_author(record: Dict) -> str:
        """获取第一作者"""
        au = record.get('AU', '')
        if au:
            first_author = au.split('\n')[0].strip()
            return first_author.lower()
        return ''

    @staticmethod
    def is_duplicate(record1: Dict, record2: Dict) -> bool:
        """
        判断两条记录是否重复

        策略：
        1. DOI匹配（最准确）
        2. 标题 + 年份 + 第一作者
        """
        # 策略1：DOI匹配
        doi1 = record1.get('DI', '').strip().lower()
        doi2 = record2.get('DI', '').strip().lower()
        if doi1 and doi2 and doi1 == doi2:
            return True

        # 策略2：标题 + 年份 + 第一作者
        title1 = RecordMatcher.normalize_title(record1.get('TI', ''))
        title2 = RecordMatcher.normalize_title(record2.get('TI', ''))

        if not title1 or not title2:
            return False

        # 标题相似度检查
        title_similar = (
            title1 == title2 or
            (len(title1) > 20 and len(title2) > 20 and
             (title1 in title2 or title2 in title1))
        )

        if not title_similar:
            return False

        # 年份匹配
        year1 = record1.get('PY', '')
        year2 = record2.get('PY', '')
        if year1 != year2:
            return False

        # 第一作者匹配（如果有）
        author1 = RecordMatcher.get_first_author(record1)
        author2 = RecordMatcher.get_first_author(record2)

        if author1 and author2:
            return author1 == author2
        else:
            # 没有作者信息，仅凭标题+年份判断
            return True


class RecordMerger:
    """记录合并器（将Scopus信息补充到WOS）"""

    @staticmethod
    def merge_scopus_to_wos(wos_record: Dict, scopus_record: Dict) -> Dict:
        """
        将Scopus信息补充到WOS记录

        Args:
            wos_record: WOS记录（优先保留）
            scopus_record: Scopus记录（补充信息）

        Returns:
            Dict: 合并后的记录（以WOS为主）
        """
        merged = wos_record.copy()

        # 1. TC（被引次数）：取最大值
        tc_wos = int(wos_record.get('TC', '0') or '0')
        tc_scopus = int(scopus_record.get('TC', '0') or '0')
        if tc_scopus > tc_wos:
            merged['TC'] = str(tc_scopus)
            merged['Z9'] = str(tc_scopus)

        # 2. 补充缺失字段（从Scopus）
        supplement_fields = ['AB', 'LA', 'DT', 'PU', 'SN', 'J9', 'JI', 'PM', 'DI']
        for field in supplement_fields:
            if not merged.get(field) and scopus_record.get(field):
                merged[field] = scopus_record[field]

        return merged


class MergeDeduplicateTool:
    """合并去重工具主类"""

    def __init__(self, wos_file: str, scopus_file: str, output_file: str):
        """
        初始化合并去重工具

        Args:
            wos_file: WOS文件路径
            scopus_file: Scopus转换后的文件路径
            output_file: 输出文件路径

        Raises:
            FileNotFoundError: 输入文件不存在
        """
        # 文件验证
        if not os.path.exists(wos_file):
            raise FileNotFoundError(f"WOS文件不存在: {wos_file}")
        if not os.path.exists(scopus_file):
            raise FileNotFoundError(f"Scopus文件不存在: {scopus_file}")

        self.wos_file = wos_file
        self.scopus_file = scopus_file
        self.output_file = output_file

        self.parser = WOSRecordParser()
        self.matcher = RecordMatcher()
        self.merger = RecordMerger()

        self.wos_records = []
        self.scopus_records = []
        self.final_records = []

        self.stats = {
            'wos_count': 0,
            'scopus_count': 0,
            'scopus_duplicates': 0,
            'scopus_unique': 0,
            'final_count': 0,
            'duplicate_details': []
        }

        logger.info(f"初始化合并工具 - WOS: {wos_file}, Scopus: {scopus_file}")

    def run(self):
        """执行合并去重流程"""
        logger.info("=" * 60)
        logger.info("WOS + Scopus 文献合并去重工具 v2.1")
        logger.info("=" * 60)
        logger.info(f"WOS文件: {self.wos_file}")
        logger.info(f"Scopus文件: {self.scopus_file}")
        logger.info(f"输出文件: {self.output_file}")
        logger.info("")

        # 步骤1：读取文件
        logger.info("步骤 1/4: 读取文件...")
        self.wos_records = self.parser.parse_wos_file(self.wos_file)
        self.scopus_records = self.parser.parse_wos_file(self.scopus_file)

        self.stats['wos_count'] = len(self.wos_records)
        self.stats['scopus_count'] = len(self.scopus_records)

        logger.info(f"  读取WOS记录: {self.stats['wos_count']} 条")
        logger.info(f"  读取Scopus记录: {self.stats['scopus_count']} 条")
        logger.info("")

        # 步骤2：识别Scopus中与WOS重复的记录
        logger.info("步骤 2/4: 识别WOS-Scopus重复记录...")
        wos_scopus_pairs = self.find_wos_scopus_duplicates()

        self.stats['scopus_duplicates'] = len(wos_scopus_pairs)
        self.stats['scopus_unique'] = self.stats['scopus_count'] - self.stats['scopus_duplicates']

        logger.info(f"  发现WOS-Scopus重复: {self.stats['scopus_duplicates']} 条")
        logger.info(f"  Scopus独有记录: {self.stats['scopus_unique']} 条")
        logger.info("")

        # 步骤3：合并记录（WOS优先，Scopus补充）
        logger.info("步骤 3/4: 合并记录（WOS优先，Scopus补充信息）...")
        self.merge_records(wos_scopus_pairs)

        self.stats['final_count'] = len(self.final_records)
        logger.info(f"  最终记录数: {self.stats['final_count']} 条")
        logger.info(f"    - WOS记录（合并后）: {self.stats['wos_count']} 条")
        logger.info(f"    - Scopus独有记录: {self.stats['scopus_unique']} 条")
        logger.info("")

        # 步骤4：写入文件
        logger.info("步骤 4/4: 写入输出文件...")
        self.write_output()
        logger.info(f"  输出文件已保存: {self.output_file}")
        logger.info("")

        # 打印统计报告
        self.print_report()

    def find_wos_scopus_duplicates(self) -> List[Tuple[int, int]]:
        """
        查找WOS和Scopus之间的重复记录

        Returns:
            List[Tuple[int, int]]: (WOS索引, Scopus索引) 对列表
        """
        pairs = []
        scopus_matched = set()  # 已匹配的Scopus索引

        for wos_idx, wos_record in enumerate(self.wos_records):
            for scopus_idx, scopus_record in enumerate(self.scopus_records):
                if scopus_idx in scopus_matched:
                    continue

                if self.matcher.is_duplicate(wos_record, scopus_record):
                    pairs.append((wos_idx, scopus_idx))
                    scopus_matched.add(scopus_idx)

                    # 记录详情
                    title = wos_record.get('TI', 'N/A')[:60]
                    self.stats['duplicate_details'].append({
                        'title': title,
                        'wos_idx': wos_idx,
                        'scopus_idx': scopus_idx
                    })

                    break  # 找到匹配，继续下一个WOS记录

        return pairs

    def merge_records(self, wos_scopus_pairs: List[Tuple[int, int]]):
        """
        合并记录

        策略：
        1. 将WOS-Scopus对合并（Scopus补充WOS）
        2. 添加Scopus独有记录
        """
        scopus_used = set(scopus_idx for _, scopus_idx in wos_scopus_pairs)

        # 1. 处理WOS记录（合并Scopus信息）
        for wos_idx, wos_record in enumerate(self.wos_records):
            # 查找对应的Scopus记录
            scopus_record = None
            for wos_i, scopus_i in wos_scopus_pairs:
                if wos_i == wos_idx:
                    scopus_record = self.scopus_records[scopus_i]
                    break

            if scopus_record:
                # 合并
                merged = self.merger.merge_scopus_to_wos(wos_record, scopus_record)
                self.final_records.append(merged)
            else:
                # WOS独有
                self.final_records.append(wos_record)

        # 2. 添加Scopus独有记录
        for scopus_idx, scopus_record in enumerate(self.scopus_records):
            if scopus_idx not in scopus_used:
                self.final_records.append(scopus_record)

    def write_output(self):
        """写入合并后的WOS格式文件"""
        lines = []

        # 文件头（使用标准WOS格式，确保VOSviewer兼容性）
        lines.append("FN Clarivate Analytics Web of Science")
        lines.append("VR 1.0")

        # 写入每条记录
        for i, record in enumerate(self.final_records):
            # 在记录前添加空行（第一条除外）
            if i > 0:
                lines.append("")

            # PT - Publication Type
            lines.append(f"PT {record.get('PT', 'J')}")

            # 移除内部标记字段
            record_clean = {k: v for k, v in record.items() if not k.startswith('_')}

            # 所有其他字段（按常见顺序）
            field_order = [
                'AU', 'AF', 'TI', 'SO', 'LA', 'DT', 'DE', 'ID', 'AB',
                'C1', 'C3', 'RP', 'EM', 'RI', 'OI', 'CR', 'NR',
                'TC', 'Z9', 'U1', 'U2', 'PU', 'SN', 'EI', 'J9', 'JI',
                'PY', 'VL', 'IS', 'SI', 'BP', 'EP', 'AR', 'PG',
                'DI', 'WE', 'UT', 'PM', 'DA'
            ]

            for field in field_order:
                if field in record_clean and field != 'PT':
                    value = record_clean[field]
                    if '\n' in value:
                        # 多行字段
                        value_lines = value.split('\n')
                        lines.append(f"{field} {value_lines[0]}")
                        for line in value_lines[1:]:
                            lines.append(f"   {line}")
                    else:
                        # 单行字段
                        lines.append(f"{field} {value}")

            # ER - End of Record
            lines.append("ER")

        # 空行 + EF
        lines.append("")
        lines.append("EF")

        # 写入文件（包含UTF-8 BOM，与WOS格式完全一致）
        with open(self.output_file, 'w', encoding='utf-8-sig') as f:
            f.write('\n'.join(lines))

    def print_report(self):
        """打印去重报告"""
        logger.info("=" * 60)
        logger.info("合并去重报告")
        logger.info("=" * 60)
        logger.info(f"WOS原始记录数:          {self.stats['wos_count']} 条")
        logger.info(f"Scopus原始记录数:       {self.stats['scopus_count']} 条")
        logger.info(f"")
        logger.info(f"WOS-Scopus重复记录:     {self.stats['scopus_duplicates']} 条（已从Scopus删除）")
        logger.info(f"Scopus独有记录:         {self.stats['scopus_unique']} 条（已保留）")
        logger.info(f"")
        logger.info(f"最终记录数:             {self.stats['final_count']} 条")
        logger.info(f"  = WOS记录（含补充）:  {self.stats['wos_count']} 条")
        logger.info(f"  + Scopus独有:         {self.stats['scopus_unique']} 条")
        logger.info("")

        if self.stats['duplicate_details']:
            logger.info("WOS-Scopus重复记录详情（前10条）:")
            logger.info("-" * 60)
            for i, detail in enumerate(self.stats['duplicate_details'][:10], 1):
                logger.info(f"{i}. {detail['title']}...")
                logger.info(f"   WOS索引: {detail['wos_idx']}, Scopus索引: {detail['scopus_idx']}")

            if len(self.stats['duplicate_details']) > 10:
                logger.info(f"... 还有 {len(self.stats['duplicate_details']) - 10} 条重复记录")

        logger.info("=" * 60)
        logger.info("说明：")
        logger.info("- WOS记录优先保留（数据更完整）")
        logger.info("- Scopus信息用于补充WOS缺失字段")
        logger.info("- 被引次数（TC）取两者最大值")
        logger.info("- Scopus独有记录（无WOS对应）已全部保留")
        logger.info("=" * 60)
        logger.info("合并去重完成！")
        logger.info("=" * 60)

        # 保存详细报告
        report_file = self.output_file.replace('.txt', '_report.txt')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("WOS + Scopus 合并去重详细报告\n")
            f.write("=" * 60 + "\n\n")

            f.write(f"WOS原始记录数:          {self.stats['wos_count']} 条\n")
            f.write(f"Scopus原始记录数:       {self.stats['scopus_count']} 条\n\n")

            f.write(f"WOS-Scopus重复记录:     {self.stats['scopus_duplicates']} 条\n")
            f.write(f"Scopus独有记录:         {self.stats['scopus_unique']} 条\n\n")

            f.write(f"最终记录数:             {self.stats['final_count']} 条\n\n")

            if self.stats['duplicate_details']:
                f.write("WOS-Scopus重复记录详情:\n")
                f.write("-" * 60 + "\n")
                for i, detail in enumerate(self.stats['duplicate_details'], 1):
                    f.write(f"{i}. {detail['title']}...\n")
                    f.write(f"   WOS索引: {detail['wos_idx']}, Scopus索引: {detail['scopus_idx']}\n")

            f.write("\n" + "=" * 60 + "\n")
            f.write("合并策略说明:\n")
            f.write("- WOS记录优先保留（数据更完整）\n")
            f.write("- Scopus信息用于补充WOS缺失字段\n")
            f.write("- 被引次数（TC）取两者最大值\n")
            f.write("- Scopus独有记录（无WOS对应）已全部保留\n")

        logger.info(f"\n详细报告已保存: {report_file}")


def main():
    """主函数"""
    import sys
    import argparse

    # 命令行参数解析
    parser = argparse.ArgumentParser(
        description='WOS和Scopus文献数据合并去重工具',
        epilog='示例: python3 merge_deduplicate.py wos.txt scopus_converted.txt merged.txt'
    )
    parser.add_argument('wos_file', nargs='?', default='wos.txt',
                       help='WOS文件路径（默认: wos.txt）')
    parser.add_argument('scopus_file', nargs='?', default='scopus_converted_to_wos.txt',
                       help='Scopus转换后的文件路径（默认: scopus_converted_to_wos.txt）')
    parser.add_argument('output_file', nargs='?', default='merged_deduplicated.txt',
                       help='输出文件路径（默认: merged_deduplicated.txt）')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='日志级别（默认: INFO）')

    args = parser.parse_args()

    # 设置日志级别
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    try:
        # 执行合并去重
        tool = MergeDeduplicateTool(args.wos_file, args.scopus_file, args.output_file)
        tool.run()
        return 0

    except FileNotFoundError as e:
        logger.error(f"文件错误: {e}")
        return 1
    except Exception as e:
        logger.error(f"发生未知错误: {e}")
        logger.exception("详细错误信息:")
        return 1


if __name__ == '__main__':
    main()
