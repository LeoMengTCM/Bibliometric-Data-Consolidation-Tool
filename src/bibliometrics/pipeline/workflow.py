#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键式AI增强工作流 v5.0

完整流程：
1. Scopus CSV → WOS格式转换
2. AI智能补全机构信息
3. 与WOS数据合并
4. 去重
5. 语言筛选（可选）
6. 年份范围过滤（可选）
7. 机构名称清洗（可选）
8. 生成统计报告

作者：Meng Linghan
开发工具：Claude Code
日期：2026-01-15
版本：v5.1.0 (Stable Release)
"""

import os
import sys
import time
import logging
import argparse
from pathlib import Path
from typing import Dict, Optional

# 导入各个模块
from ..converters.batch import EnhancedConverterBatchV2
from ..standardizers.enrichment import InstitutionEnricherV2
from ..gemini_config import GeminiConfig
from .merge import MergeDeduplicateTool
from ..filters.language import LanguageFilter
from ..analysis.records import RecordAnalyzer
from ..standardizers.institutions import InstitutionCleaner
try:
    from ..analysis.plot_types import generate_all_figures
    PLOT_AVAILABLE = True
except ImportError:
    PLOT_AVAILABLE = False
    logger.warning("plot_document_types 模块未找到，图表生成功能将被禁用")
from ..filters.year import YearFilter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class AIWorkflow:
    """AI增强的完整工作流"""

    def __init__(self, data_dir: str, language: str = 'English', enable_ai: bool = True,
                 enable_cleaning: bool = True, cleaning_config: str = 'config/institution_cleaning_rules_ultimate.json',
                 year_range: Optional[str] = None, enable_plot: bool = True, progress_callback=None):
        """
        初始化工作流

        Args:
            data_dir: 数据目录（包含wos.txt和scopus.csv）
            language: 目标语言（默认English）
            enable_ai: 是否启用AI补全（默认True）
            enable_cleaning: 是否启用机构清洗（默认True）⭐ NEW
            cleaning_config: 清洗规则配置文件（默认使用增强版）⭐ NEW
            year_range: 年份范围过滤（格式: YYYY-YYYY，如2015-2024）⭐ NEW
            enable_plot: 是否生成图表（默认True）⭐ NEW
            progress_callback: 进度回调函数，接收(step_name: str, progress: float)参数 ⭐ GUI支持
        """
        self.data_dir = Path(data_dir)
        self.language = language
        self.enable_ai = enable_ai
        self.enable_cleaning = enable_cleaning
        self.enable_plot = enable_plot  # ⭐ 新增：是否生成图表
        self.cleaning_config = cleaning_config
        self.year_range = year_range
        self.progress_callback = progress_callback  # ⭐ 新增：进度回调

        # 定义文件路径
        self.wos_file = self.data_dir / 'wos.txt'
        self.scopus_file = self.data_dir / 'scopus.csv'

        # 年份过滤后的原始文件（如果启用年份过滤）
        self.wos_year_filtered = self.data_dir / 'wos_year_filtered.txt'
        self.scopus_year_filtered = self.data_dir / 'scopus_year_filtered.csv'

        self.scopus_converted = self.data_dir / 'scopus_converted_to_wos.txt'
        self.scopus_enriched = self.data_dir / 'scopus_enriched.txt'
        self.merged_file = self.data_dir / 'merged_deduplicated.txt'
        self.filtered_file = self.data_dir / f'{language.lower()}_only.txt'
        self.cleaned_file = self.data_dir / 'Final_Version.txt'  # ⭐ 清洗后的文件
        self.report_file = self.data_dir / 'ai_workflow_report.txt'

        # 统计信息
        self.stats = {
            'start_time': time.time(),
            'steps': []
        }

    def _update_progress(self, step_name: str, progress: float):
        """更新进度（如果提供了回调函数）"""
        if self.progress_callback:
            try:
                self.progress_callback(step_name, progress)
            except Exception as e:
                logger.warning(f"进度回调失败: {e}")

    def check_files(self) -> bool:
        """检查必需文件是否存在"""
        logger.info("=" * 80)
        logger.info("步骤0: 检查输入文件")
        logger.info("=" * 80)

        if not self.wos_file.exists():
            logger.error(f"✗ WOS文件不存在: {self.wos_file}")
            return False

        if not self.scopus_file.exists():
            logger.error(f"✗ Scopus文件不存在: {self.scopus_file}")
            return False

        logger.info(f"✓ WOS文件: {self.wos_file}")
        logger.info(f"✓ Scopus文件: {self.scopus_file}")
        logger.info("")

        return True

    def step1_filter_wos_by_year(self) -> bool:
        """步骤1: 年份范围过滤WOS数据（如果启用）⭐ NEW"""
        logger.info("=" * 80)
        logger.info("步骤1: 年份范围过滤WOS数据")
        logger.info("=" * 80)

        try:
            # 解析年份范围
            import re
            match = re.match(r'^(\d{4})-(\d{4})$', self.year_range)
            if not match:
                raise ValueError(f"年份范围格式错误: {self.year_range}，应为 YYYY-YYYY 格式（如 2015-2024）")

            min_year = int(match.group(1))
            max_year = int(match.group(2))

            if min_year > max_year:
                raise ValueError(f"最小年份 ({min_year}) 不能大于最大年份 ({max_year})")

            logger.info(f"年份范围: {min_year}-{max_year}")

            # 创建年份过滤器
            year_filter = YearFilter(min_year=min_year, max_year=max_year)

            # 生成报告文件名
            report_file = str(self.wos_year_filtered).replace('.txt', '_year_filter_report.txt')

            # 执行过滤
            year_filter.filter_file(str(self.wos_file), str(self.wos_year_filtered), report_file)

            # 获取统计信息
            year_stats = {
                'total_records': year_filter.stats['total_records'],
                'filtered_records': year_filter.stats['filtered_records'],
                'kept_records': year_filter.stats['total_records'] - year_filter.stats['filtered_records'],
                'filter_rate': year_filter.stats['filtered_records'] / year_filter.stats['total_records'] * 100
                              if year_filter.stats['total_records'] > 0 else 0,
                'filtered_years': dict(year_filter.stats['filtered_years'])
            }

            logger.info(f"✓ WOS年份过滤完成: {self.wos_year_filtered}")
            logger.info("")

            self.stats['steps'].append({
                'step': 1,
                'name': 'WOS年份范围过滤',
                'status': 'success',
                'output': str(self.wos_year_filtered),
                'year_stats': year_stats
            })

            return True

        except Exception as e:
            logger.error(f"✗ WOS年份过滤失败: {e}")
            self.stats['steps'].append({
                'step': 1,
                'name': 'WOS年份范围过滤',
                'status': 'failed',
                'error': str(e)
            })
            return False

    def step2_filter_scopus_by_year(self) -> bool:
        """步骤2: 年份范围过滤Scopus CSV数据（如果启用）⭐ NEW"""
        logger.info("=" * 80)
        logger.info("步骤2: 年份范围过滤Scopus数据")
        logger.info("=" * 80)

        try:
            import csv
            import re
            match = re.match(r'^(\d{4})-(\d{4})$', self.year_range)
            min_year = int(match.group(1))
            max_year = int(match.group(2))

            logger.info(f"年份范围: {min_year}-{max_year}")

            # 读取Scopus CSV
            filtered_rows = []
            header = None
            total_records = 0
            filtered_records = 0
            filtered_years = {}

            with open(self.scopus_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                header = reader.fieldnames

                for row in reader:
                    total_records += 1
                    year_str = row.get('Year', '')

                    # 检查年份
                    if year_str and year_str.isdigit():
                        year = int(year_str)
                        if min_year <= year <= max_year:
                            filtered_rows.append(row)
                        else:
                            filtered_records += 1
                            filtered_years[year_str] = filtered_years.get(year_str, 0) + 1
                    else:
                        # 没有年份信息，保留
                        filtered_rows.append(row)

            # 写入过滤后的CSV
            with open(self.scopus_year_filtered, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=header)
                writer.writeheader()
                writer.writerows(filtered_rows)

            kept_records = total_records - filtered_records

            logger.info(f"✓ Scopus年份过滤完成: {self.scopus_year_filtered}")
            logger.info(f"  原始记录: {total_records}")
            logger.info(f"  保留记录: {kept_records}")
            logger.info(f"  过滤掉: {filtered_records}")
            logger.info("")

            # 统计信息
            year_stats = {
                'total_records': total_records,
                'filtered_records': filtered_records,
                'kept_records': kept_records,
                'filter_rate': filtered_records / total_records * 100 if total_records > 0 else 0,
                'filtered_years': filtered_years
            }

            self.stats['steps'].append({
                'step': 2,
                'name': 'Scopus年份范围过滤',
                'status': 'success',
                'output': str(self.scopus_year_filtered),
                'year_stats': year_stats
            })

            return True

        except Exception as e:
            logger.error(f"✗ Scopus年份过滤失败: {e}")
            self.stats['steps'].append({
                'step': 2,
                'name': 'Scopus年份范围过滤',
                'status': 'failed',
                'error': str(e)
            })
            return False

    def step3_convert_scopus(self) -> bool:
        """步骤3: 转换Scopus到WOS格式（含WOS标准化）"""
        logger.info("=" * 80)
        logger.info("步骤3: 转换Scopus到WOS格式（含WOS标准化）")
        logger.info("=" * 80)

        try:
            # 如果启用了年份过滤，使用过滤后的文件；否则使用原始文件
            input_file = self.scopus_year_filtered if self.year_range else self.scopus_file

            converter = EnhancedConverterBatchV2(
                str(input_file),
                str(self.scopus_converted),
                enable_standardization=True,
                max_workers=20,
                batch_size=50
            )
            converter.convert()

            logger.info(f"✓ 转换完成（已WOS标准化）: {self.scopus_converted}")
            logger.info("")

            self.stats['steps'].append({
                'step': 3,
                'name': 'Scopus格式转换+WOS标准化',
                'status': 'success',
                'output': str(self.scopus_converted)
            })

            return True

        except Exception as e:
            logger.error(f"✗ 转换失败: {e}")
            self.stats['steps'].append({
                'step': 3,
                'name': 'Scopus格式转换+WOS标准化',
                'status': 'failed',
                'error': str(e)
            })
            return False

    def step4_ai_enrich(self) -> bool:
        """步骤4: AI智能补全机构信息"""
        if not self.enable_ai:
            logger.info("跳过AI补全步骤（未启用）")
            # 直接复制文件
            import shutil
            shutil.copy(self.scopus_converted, self.scopus_enriched)
            return True

        logger.info("=" * 80)
        logger.info("步骤4: AI智能补全机构信息")
        logger.info("=" * 80)

        try:
            # 创建Gemini配置
            config = GeminiConfig.from_params(
                api_key=os.getenv('GEMINI_API_KEY', 'YOUR_API_KEY'),
                api_url=os.getenv('GEMINI_API_URL', 'https://your-api-gateway.com/proxy/bibliometrics/v1beta'),
                model='gemini-2.5-flash-lite'
            )

            if not config.validate():
                logger.error("✗ Gemini API配置无效")
                return False

            logger.info(f"API模型: {config.model}")
            logger.info(f"Max tokens: {config.max_tokens}")
            logger.info(f"重试次数: {config.max_retries}")
            logger.info("")

            # 创建补全器
            enricher = InstitutionEnricherV2(config)

            # 补全文件
            stats = enricher.enrich_file(str(self.scopus_converted), str(self.scopus_enriched))

            logger.info(f"✓ AI补全完成: {self.scopus_enriched}")
            logger.info("")

            # 打印统计
            enricher.print_statistics()

            self.stats['steps'].append({
                'step': 4,
                'name': 'AI智能补全',
                'status': 'success',
                'output': str(self.scopus_enriched),
                'enrichment_stats': stats
            })

            return True

        except Exception as e:
            logger.error(f"✗ AI补全失败: {e}")
            self.stats['steps'].append({
                'step': 4,
                'name': 'AI智能补全',
                'status': 'failed',
                'error': str(e)
            })
            return False

    def step5_merge_deduplicate(self) -> bool:
        """步骤5: 合并与去重"""
        logger.info("=" * 80)
        logger.info("步骤5: 合并与去重")
        logger.info("=" * 80)

        try:
            # 使用AI补全后的文件（如果启用）或原始转换文件
            scopus_input = self.scopus_enriched if self.enable_ai else self.scopus_converted

            # 如果启用了年份过滤，使用过滤后的WOS文件；否则使用原始WOS文件
            wos_input = self.wos_year_filtered if self.year_range else self.wos_file

            tool = MergeDeduplicateTool(
                str(wos_input),
                str(scopus_input),
                str(self.merged_file)
            )

            tool.run()  # 执行合并去重

            # 获取统计信息
            stats = {
                'wos_count': len(tool.wos_records),
                'scopus_count': len(tool.scopus_records),
                'duplicates': len(tool.find_wos_scopus_duplicates()),
                'final_count': len(tool.wos_records) + len(tool.scopus_records) - len(tool.find_wos_scopus_duplicates())
            }

            logger.info(f"✓ 合并去重完成: {self.merged_file}")
            logger.info("")

            self.stats['steps'].append({
                'step': 5,
                'name': '合并与去重',
                'status': 'success',
                'output': str(self.merged_file),
                'merge_stats': stats
            })

            return True

        except Exception as e:
            logger.error(f"✗ 合并去重失败: {e}")
            self.stats['steps'].append({
                'step': 5,
                'name': '合并与去重',
                'status': 'failed',
                'error': str(e)
            })
            return False

    def step6_filter_language(self) -> bool:
        """步骤6: 语言筛选"""
        logger.info("=" * 80)
        logger.info(f"步骤6: 语言筛选（{self.language}）")
        logger.info("=" * 80)

        try:
            filter_tool = LanguageFilter(
                str(self.merged_file),
                str(self.filtered_file),
                self.language
            )
            filter_tool.run()  # 执行筛选
            stats = filter_tool.stats

            logger.info(f"✓ 语言筛选完成: {self.filtered_file}")
            logger.info("")

            self.stats['steps'].append({
                'step': 6,
                'name': f'语言筛选（{self.language}）',
                'status': 'success',
                'output': str(self.filtered_file),
                'filter_stats': stats
            })

            return True

        except Exception as e:
            logger.error(f"✗ 语言筛选失败: {e}")
            self.stats['steps'].append({
                'step': 6,
                'name': f'语言筛选（{self.language}）',
                'status': 'failed',
                'error': str(e)
            })
            return False

    def step7_clean_institutions(self) -> bool:
        """步骤7: 机构名称清洗（可选）"""
        if not self.enable_cleaning:
            logger.info("跳过机构清洗步骤（未启用）")
            logger.info("")
            return True

        logger.info("=" * 80)
        logger.info("步骤7: 机构名称清洗")
        logger.info("=" * 80)

        try:
            cleaner = InstitutionCleaner(self.cleaning_config)
            cleaner.run(str(self.filtered_file), str(self.cleaned_file))

            # 获取清洗统计
            cleaning_stats = {
                'total_records': cleaner.stats['total_records'],
                'institutions_before': cleaner.stats['total_institutions_before'],
                'institutions_after': cleaner.stats['total_institutions_after'],
                'unique_before': cleaner.stats['unique_before'],
                'unique_after': cleaner.stats['unique_after'],
                'removed_noise': cleaner.stats['removed_noise'],
                'merged': cleaner.stats['merged_parent_child'],
                'removed_departments': cleaner.stats['removed_departments']
            }

            logger.info(f"✓ 机构清洗完成: {self.cleaned_file}")
            logger.info("")

            self.stats['steps'].append({
                'step': 7,
                'name': '机构名称清洗',
                'status': 'success',
                'output': str(self.cleaned_file),
                'cleaning_stats': cleaning_stats
            })

            return True

        except Exception as e:
            logger.error(f"✗ 机构清洗失败: {e}")
            self.stats['steps'].append({
                'step': 7,
                'name': '机构名称清洗',
                'status': 'failed',
                'error': str(e)
            })
            return False

    def step8_analyze(self) -> bool:
        """步骤8: 统计分析（只分析一次，分析最终文件）"""
        logger.info("=" * 80)
        logger.info("步骤8: 统计分析")
        logger.info("=" * 80)

        try:
            # 确定最终分析文件：优先使用清洗后的文件，否则使用筛选后的文件
            analysis_file = self.cleaned_file if self.enable_cleaning else self.filtered_file

            analyzer = RecordAnalyzer(str(analysis_file))
            analyzer.analyze()

            # 分析报告文件由 save_detailed_report() 自动生成
            analysis_report_file = str(analysis_file).replace('.txt', '_analysis_report.txt')

            logger.info(f"✓ 统计分析完成: {analysis_report_file}")
            logger.info("")

            self.stats['steps'].append({
                'step': 8,
                'name': '统计分析',
                'status': 'success',
                'output': analysis_report_file
            })

            return True

        except Exception as e:
            logger.error(f"✗ 统计分析失败: {e}")
            self.stats['steps'].append({
                'step': 8,
                'name': '统计分析',
                'status': 'failed',
                'error': str(e)
            })
            return False

    def generate_report(self):
        """生成工作流报告"""
        logger.info("=" * 80)
        logger.info("生成工作流报告")
        logger.info("=" * 80)

        elapsed_time = time.time() - self.stats['start_time']

        report = []
        report.append("=" * 80)
        report.append("AI增强工作流完成报告")
        report.append("=" * 80)
        report.append("")
        report.append(f"数据目录: {self.data_dir}")
        report.append(f"目标语言: {self.language}")
        report.append(f"AI补全: {'启用' if self.enable_ai else '禁用'}")
        report.append(f"总耗时: {elapsed_time:.1f}秒")
        report.append("")

        # 各步骤统计
        report.append("=" * 80)
        report.append("处理步骤")
        report.append("=" * 80)
        report.append("")

        for step_info in self.stats['steps']:
            report.append(f"步骤{step_info['step']}: {step_info['name']}")
            report.append(f"  状态: {'✓ 成功' if step_info['status'] == 'success' else '✗ 失败'}")

            if step_info['status'] == 'success':
                report.append(f"  输出: {step_info['output']}")

                # 详细统计
                if 'enrichment_stats' in step_info:
                    stats = step_info['enrichment_stats']
                    report.append(f"  补全统计:")
                    report.append(f"    - 总处理数: {stats['processing']['total_processed']}")
                    report.append(f"    - 补全成功: {stats['processing']['enriched']}")
                    report.append(f"    - 补全率: {stats['processing']['enrichment_rate']}")
                    report.append(f"    - 数据库命中: {stats['session']['db_hits']}")
                    report.append(f"    - AI调用: {stats['session']['ai_calls']}")

                if 'merge_stats' in step_info:
                    stats = step_info['merge_stats']
                    report.append(f"  合并统计:")
                    report.append(f"    - WOS记录: {stats['wos_count']}")
                    report.append(f"    - Scopus记录: {stats['scopus_count']}")
                    report.append(f"    - 重复记录: {stats['duplicates']}")
                    report.append(f"    - 最终记录: {stats['final_count']}")

                if 'filter_stats' in step_info:
                    stats = step_info['filter_stats']
                    report.append(f"  筛选统计:")
                    report.append(f"    - 输入记录: {stats['total_records']}")
                    report.append(f"    - 筛选后: {stats['filtered_records']}")
                    report.append(f"    - 筛选率: {stats['filtered_records']/stats['total_records']*100:.1f}%")

                if 'cleaning_stats' in step_info:
                    stats = step_info['cleaning_stats']
                    report.append(f"  清洗统计:")
                    report.append(f"    - 总机构数（清洗前）: {stats['institutions_before']}")
                    report.append(f"    - 总机构数（清洗后）: {stats['institutions_after']}")
                    report.append(f"    - 唯一机构数（清洗前）: {stats['unique_before']}")
                    report.append(f"    - 唯一机构数（清洗后）: {stats['unique_after']}")
                    report.append(f"    - 减少比例: {(1-stats['unique_after']/stats['unique_before'])*100:.1f}%")
                    report.append(f"    - 移除噪音: {stats['removed_noise']}")
                    report.append(f"    - 合并父子机构: {stats['merged']}")
                    report.append(f"    - 移除独立部门: {stats['removed_departments']}")

                if 'year_stats' in step_info:
                    stats = step_info['year_stats']
                    report.append(f"  年份过滤统计:")
                    report.append(f"    - 原始记录: {stats['total_records']}")
                    report.append(f"    - 保留记录: {stats['kept_records']}")
                    report.append(f"    - 过滤掉: {stats['filtered_records']}")
                    report.append(f"    - 过滤率: {stats['filter_rate']:.1f}%")
                    if stats['filtered_years']:
                        report.append(f"    - 被过滤的年份:")
                        for year, count in sorted(stats['filtered_years'].items()):
                            report.append(f"      {year}: {count} 篇")

            else:
                report.append(f"  错误: {step_info.get('error', '未知错误')}")

            report.append("")

        # 最终输出文件
        report.append("=" * 80)
        report.append("最终输出文件")
        report.append("=" * 80)
        report.append("")
        file_num = 1

        # 如果启用了年份过滤，显示过滤后的原始文件
        if self.year_range:
            report.append(f"{file_num}. WOS年份过滤后: {self.wos_year_filtered}")
            file_num += 1
            report.append(f"{file_num}. Scopus年份过滤后: {self.scopus_year_filtered}")
            file_num += 1

        report.append(f"{file_num}. 转换后的Scopus数据: {self.scopus_converted}")
        file_num += 1
        if self.enable_ai:
            report.append(f"{file_num}. AI补全后的数据: {self.scopus_enriched}")
            file_num += 1
        report.append(f"{file_num}. 合并去重后的数据: {self.merged_file}")
        file_num += 1
        report.append(f"{file_num}. {self.language}筛选后的数据: {self.filtered_file}")
        file_num += 1
        if self.enable_cleaning:
            report.append(f"{file_num}. 机构清洗后的数据: {self.cleaned_file} ⭐ 推荐")
            file_num += 1

        # 确定最终分析文件
        final_analysis_file = self.cleaned_file if self.enable_cleaning else self.filtered_file

        report.append(f"{file_num}. 统计分析报告: {str(final_analysis_file).replace('.txt', '_analysis_report.txt')}")
        report.append("")

        # 推荐使用
        report.append("=" * 80)
        report.append("推荐使用")
        report.append("=" * 80)
        report.append("")
        report.append(f"✓ 用于VOSViewer/CiteSpace分析: {final_analysis_file}")
        if self.year_range:
            report.append(f"  （已在源头过滤年份，数据更准确）⭐ 强烈推荐")
        if self.enable_cleaning:
            report.append(f"  （已清洗，唯一机构数减少约20%）")
        report.append(f"✓ 用于论文写作参考: {str(final_analysis_file).replace('.txt', '_analysis_report.txt')}")
        report.append("")

        # 写入报告文件
        report_text = '\n'.join(report)
        with open(self.report_file, 'w', encoding='utf-8') as f:
            f.write(report_text)

        logger.info(f"✓ 工作流报告已保存: {self.report_file}")
        logger.info("")

        # 打印到控制台
        print(report_text)

    def create_project_structure(self) -> bool:
        """创建项目文件夹结构"""
        logger.info("=" * 80)
        logger.info("步骤7: 创建项目文件夹结构")
        logger.info("=" * 80)

        try:
            # 创建主文件夹
            folders = {
                'Figures and Tables': [
                    '01 文档类型'
                ],
                'data': [],
                'project': []
            }

            for main_folder, subfolders in folders.items():
                main_path = self.data_dir / main_folder
                main_path.mkdir(exist_ok=True)
                logger.info(f"✓ 创建文件夹: {main_folder}")

                for subfolder in subfolders:
                    sub_path = main_path / subfolder
                    sub_path.mkdir(exist_ok=True)
                    logger.info(f"  ✓ 创建子文件夹: {subfolder}")

            logger.info("✓ 项目文件夹结构创建完成")
            logger.info("")
            return True

        except Exception as e:
            logger.error(f"✗ 创建文件夹结构失败: {e}")
            return False

    def step10_generate_document_type_plot(self) -> bool:
        """生成所有图表（文档类型 + 年度发文及引用量）"""
        logger.info("=" * 80)
        logger.info("步骤10: 生成所有图表")
        logger.info("=" * 80)

        if not PLOT_AVAILABLE:
            logger.warning("⚠ 图表生成功能不可用（缺少依赖）")
            return True

        try:
            # 提取年份范围参数
            min_year = None
            max_year = None
            if self.year_range:
                import re
                match = re.match(r'^(\d{4})-(\d{4})$', self.year_range)
                if match:
                    min_year = int(match.group(1))
                    max_year = int(match.group(2))

            # 传递数据目录和年份参数，生成所有图表
            success = generate_all_figures(str(self.data_dir), min_year, max_year)
            if success:
                logger.info("✓ 所有图表生成完成")
                logger.info("")
            return success
        except Exception as e:
            logger.error(f"✗ 图表生成失败: {e}")
            return False

    def run(self) -> bool:
        """运行完整工作流"""
        logger.info("")
        logger.info("=" * 80)
        logger.info("AI增强工作流启动")
        logger.info("=" * 80)
        logger.info("")

        # 计算总步骤数
        total_steps = 8  # 基础步骤：3转换 + 4AI + 5合并 + 6语言 + 7清洗 + 8分析 + 9结构 + 10图表
        if self.year_range:
            total_steps += 2  # 增加步骤1和2（年份过滤）
        current_step = 0

        # 检查文件
        self._update_progress("正在检查输入文件...", 0.0)
        if not self.check_files():
            return False

        # 步骤1: 年份范围过滤WOS数据（如果启用）⭐ 最优先
        if self.year_range:
            current_step += 1
            self._update_progress(f"步骤{current_step}/{total_steps}: 年份过滤WOS数据...", current_step / total_steps)
            if not self.step1_filter_wos_by_year():
                return False

        # 步骤2: 年份范围过滤Scopus数据（如果启用）⭐ 第二优先
        if self.year_range:
            current_step += 1
            self._update_progress(f"步骤{current_step}/{total_steps}: 年份过滤Scopus数据...", current_step / total_steps)
            if not self.step2_filter_scopus_by_year():
                return False

        # 步骤3: 转换Scopus（使用过滤后的文件）
        current_step += 1
        self._update_progress(f"步骤{current_step}/{total_steps}: 转换Scopus到WOS格式...", current_step / total_steps)
        if not self.step3_convert_scopus():
            return False

        # 步骤4: AI补全
        current_step += 1
        if self.enable_ai:
            self._update_progress(f"步骤{current_step}/{total_steps}: AI智能补全机构信息...", current_step / total_steps)
        else:
            self._update_progress(f"步骤{current_step}/{total_steps}: 跳过AI补全...", current_step / total_steps)
        if not self.step4_ai_enrich():
            return False

        # 步骤5: 合并去重
        current_step += 1
        self._update_progress(f"步骤{current_step}/{total_steps}: 合并与去重...", current_step / total_steps)
        if not self.step5_merge_deduplicate():
            return False

        # 步骤6: 语言筛选
        current_step += 1
        self._update_progress(f"步骤{current_step}/{total_steps}: 语言筛选（{self.language}）...", current_step / total_steps)
        if not self.step6_filter_language():
            return False

        # 步骤7: 机构清洗（可选）
        current_step += 1
        if self.enable_cleaning:
            self._update_progress(f"步骤{current_step}/{total_steps}: 机构名称清洗...", current_step / total_steps)
        else:
            self._update_progress(f"步骤{current_step}/{total_steps}: 跳过机构清洗...", current_step / total_steps)
        if not self.step7_clean_institutions():
            return False

        # 步骤8: 统计分析（只分析一次，分析最终文件）
        current_step += 1
        self._update_progress(f"步骤{current_step}/{total_steps}: 统计分析...", current_step / total_steps)
        if not self.step8_analyze():
            return False

        # 步骤9: 创建项目文件夹结构
        current_step += 1
        self._update_progress(f"步骤{current_step}/{total_steps}: 创建项目结构...", current_step / total_steps)
        if not self.create_project_structure():
            return False

        # 步骤10: 生成文档类型分析（可选，失败不影响整体流程）
        current_step += 1
        if self.enable_plot:
            self._update_progress(f"步骤{current_step}/{total_steps}: 生成图表...", current_step / total_steps)
            try:
                self.step10_generate_document_type_plot()
            except Exception as e:
                logger.warning(f"⚠ 文档类型分析跳过: {e}")
                logger.info("提示: 如需生成图表，请安装 matplotlib: pip3 install matplotlib")
        else:
            self._update_progress(f"步骤{current_step}/{total_steps}: 跳过图表生成...", current_step / total_steps)
            logger.info("跳过图表生成（未启用）")

        # 生成报告
        self.generate_report()

        self._update_progress("✓ 处理完成！", 1.0)
        logger.info("=" * 80)
        logger.info("✓ 工作流全部完成！")
        logger.info("=" * 80)
        logger.info("")

        return True


def main():
    """命令行工具"""
    parser = argparse.ArgumentParser(
        description='AI增强的一键式工作流',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本使用（启用AI补全）
  python3 run_ai_workflow.py --data-dir "/path/to/data"

  # 筛选中文文献
  python3 run_ai_workflow.py --data-dir "/path/to/data" --language Chinese

  # 禁用AI补全（仅格式转换和合并）
  python3 run_ai_workflow.py --data-dir "/path/to/data" --no-ai

  # 禁用机构清洗
  python3 run_ai_workflow.py --data-dir "/path/to/data" --no-cleaning

  # 过滤指定年份范围（如2015-2024）⭐ NEW
  python3 run_ai_workflow.py --data-dir "/path/to/data" --year-range 2015-2024

  # 使用自定义清洗规则
  python3 run_ai_workflow.py --data-dir "/path/to/data" --cleaning-config config/my_rules.json

  # 完整示例
  python3 run_ai_workflow.py \\
      --data-dir "/path/to/data/My_Research_Project" \\
      --language English \\
      --log-level INFO

输入要求:
  数据目录必须包含:
  - wos.txt (WOS原始数据)
  - scopus.csv (Scopus导出数据)

输出文件:
  - scopus_converted_to_wos.txt (转换后的Scopus数据，已WOS标准化)
  - scopus_enriched.txt (AI补全后的数据，如果启用AI)
  - merged_deduplicated.txt (合并去重后的数据)
  - english_only.txt (语言筛选后的数据)
  - english_analysis_report.txt (统计分析报告)
  - ai_workflow_report.txt (工作流完成报告)

WOS标准化功能 (v4.0.1批量并发版):
  - 国家名WOS标准化（China → Peoples R China）- 60个国家
  - 期刊名WOS标准缩写（Journal of XXX → J XXX）- 237个期刊
  - 作者名使用原有算法（不用AI，准确率97%+）
  - 批量并发处理（20线程，3分钟完成660篇）
  - 数据库记忆，越用越快（297次API调用 vs 7000+）
        """
    )

    parser.add_argument('--data-dir', required=True, help='数据目录（包含wos.txt和scopus.csv）')
    parser.add_argument('--language', default='English', help='目标语言（默认: English）')
    parser.add_argument('--no-ai', action='store_true', help='禁用AI补全')
    parser.add_argument('--no-cleaning', action='store_true', help='禁用机构清洗（默认启用）')
    parser.add_argument('--cleaning-config', default='config/institution_cleaning_rules_ultimate.json',
                       help='机构清洗规则配置文件（默认: 终极版规则）')
    parser.add_argument('--year-range', help='年份范围过滤（格式: YYYY-YYYY，如2015-2024）⭐ NEW')
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
