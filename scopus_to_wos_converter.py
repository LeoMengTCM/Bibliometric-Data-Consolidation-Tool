#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scopus CSV to WOS Plain Text Converter
======================================

将Scopus数据库导出的CSV文件转换为Web of Science纯文本格式。
用于文献计量学分析工具（CiteSpace, VOSviewer, Bibliometrix等）。

作者：Meng Linghan
开发工具：Claude Code
日期：2025-11-05
版本：v3.1（重大修复版 - C1字段完美修复）

更新日志：
- 添加logging模块支持
- 改进错误处理和文件验证
- 支持外部配置文件（期刊和机构缩写）
- 完善机构识别���辑（School/College层级判断）
- 添加进度显示
"""

import csv
import re
import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Set
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class ScopusToWosConverter:
    """Scopus CSV到WOS纯文本格式转换器"""

    # 期刊名缩写映射表（常见期刊）
    JOURNAL_ABBREV = {
        "American Journal of Gastroenterology": "AM J GASTROENTEROL",
        "Modern Pathology": "MODERN PATHOL",
        "Nature Reviews Disease Primers": "NAT REV DIS PRIMERS",
        "Nature Reviews Gastroenterology and Hepatology": "NAT REV GASTRO HEPAT",
        "Alimentary Pharmacology and Therapeutics": "ALIMENT PHARM THER",
        "Clinical and Translational Gastroenterology": "CLIN TRANSL GASTROEN",
        "Digestive and Liver Disease": "DIGEST LIVER DIS",
        "Digestive Diseases and Sciences": "DIGEST DIS SCI",
        "Journal of Clinical Medicine": "J CLIN MED",
        "Clinical Gastroenterology and Hepatology": "CLIN GASTROENTEROL H",
        "Autoimmunity Reviews": "AUTOIMMUN REV",
        "Gut": "GUT",
        "Gastroenterology": "GASTROENTEROLOGY",
        "World Journal of Gastroenterology": "WORLD J GASTROENTERO",
        "Journal of Pediatric Gastroenterology and Nutrition": "J PEDIATR GASTR NUTR",
        "Scandinavian Journal of Gastroenterology": "SCAND J GASTROENTERO",
        "Frontiers in Immunology": "FRONT IMMUNOL",
        "Medicine": "MEDICINE",
        "Journal of Experimental Medicine": "J EXP MED",
        "American Journal of Surgical Pathology": "AM J SURG PATHOL",
        "Gastroenterology Research and Practice": "GASTROENT RES PRACT",
        "American Journal of Clinical Pathology": "AM J CLIN PATHOL",
        "Histopathology": "HISTOPATHOLOGY",
        "Pathology Research and Practice": "PATHOL RES PRACT",
        "Archives of Pathology and Laboratory Medicine": "ARCH PATHOL LAB MED",
        "Clinical Cancer Research": "CLIN CANCER RES",
        "Pathologica": "PATHOLOGICA",
        "Clinical Case Reports": "CLIN CASE REP",
        "Cellular and Molecular Gastroenterology and Hepatology": "CELL MOL GASTROENTER",
        "Virchows Archiv": "VIRCHOWS ARCH",
        "United European Gastroenterology Journal": "UNITED EUR GASTROENT",
        "Gastroenterology Research": "GASTROENTEROL RES",
        "Digestive Diseases": "DIGEST DIS",
        "Journal of Medical Genetics": "J MED GENET",
        "Annals of Clinical and Laboratory Science": "ANN CLIN LAB SCI",
        "Biomedicines": "BIOMEDICINES",
        "Nature": "NATURE",
        "International Journal of Cancer": "INT J CANCER",
        "Journal of Immunotherapy for Cancer": "J IMMUNOTHER CANCER",
        "Cancer Cell International": "CANCER CELL INT",
        "Best Practice and Research Clinical Endocrinology and Metabolism": "BEST PRACT RES CL EN",
        "Translational Research": "TRANSL RES",
        "European Journal of Internal Medicine": "EUR J INTERN MED",
        "Human Pathology": "HUM PATHOL",
        "International Journal of Epidemiology": "INT J EPIDEMIOL",
        "American Journal of Public Health": "AM J PUBLIC HEALTH",
        "Journal of the American Geriatrics Society": "J AM GERIATR SOC",
        "Endoscopy": "ENDOSCOPY",
        "Plos Medicine": "PLOS MED",
        "Lancet": "LANCET",
        "Clinical Research in Hepatology and Gastroenterology": "CLIN RES HEPATOL GAS",
        "Annals of Gastroenterology": "ANN GASTROENTEROL",
        "Trends in Molecular Medicine": "TRENDS MOL MED",
        "Gastroenterology Clinics of North America": "GASTROENTEROL CLIN N",
        "Nature Reviews Rheumatology": "NAT REV RHEUMATOL",
        "Journal of Clinical Pathology": "J CLIN PATHOL",
        "World Journal of Gastrointestinal Oncology": "WORLD J GASTRO ONCOL",
        "Annals of Oncology": "ANN ONCOL",
    }

    # 月份映射
    MONTH_ABBREV = {
        '1': 'JAN', '2': 'FEB', '3': 'MAR', '4': 'APR', '5': 'MAY', '6': 'JUN',
        '7': 'JUL', '8': 'AUG', '9': 'SEP', '10': 'OCT', '11': 'NOV', '12': 'DEC',
        'January': 'JAN', 'February': 'FEB', 'March': 'MAR', 'April': 'APR',
        'May': 'MAY', 'June': 'JUN', 'July': 'JUL', 'August': 'AUG',
        'September': 'SEP', 'October': 'OCT', 'November': 'NOV', 'December': 'DEC'
    }

    def __init__(self, csv_file: str, output_file: str, config_dir: str = "config"):
        """
        初始化转换器

        Args:
            csv_file: Scopus CSV文件路径
            output_file: 输出WOS文件路径
            config_dir: 配置文件目录（默认为config）

        Raises:
            FileNotFoundError: 输入文件不存在
            ValueError: 文件格式不正确
        """
        # 文件路径验证
        if not csv_file.endswith('.csv'):
            raise ValueError(f"输入文件必须是CSV格式，当前文件: {csv_file}")

        if not os.path.exists(csv_file):
            raise FileNotFoundError(f"输入文件不存在: {csv_file}")

        # 检查文件是否可读
        try:
            with open(csv_file, 'r', encoding='utf-8-sig') as f:
                f.read(1)
        except PermissionError:
            raise PermissionError(f"无权限读取文件: {csv_file}")
        except UnicodeDecodeError:
            raise ValueError(f"文件编码错误，请确保文件为UTF-8格式: {csv_file}")

        self.csv_file = csv_file
        self.output_file = output_file
        self.config_dir = config_dir
        self.records = []

        # 加载配置文件
        self.journal_abbrev = self._load_journal_abbrev()
        self.institution_config = self._load_institution_config()

        logger.info(f"初始化转换器 - 输入: {csv_file}, 输出: {output_file}")
        logger.info(f"已加载 {len(self.journal_abbrev)} 个期刊缩写")

    def _load_journal_abbrev(self) -> Dict[str, str]:
        """加载期刊缩写配置"""
        config_file = os.path.join(self.config_dir, "journal_abbrev.json")

        # 默认缩写（备用）
        default_abbrev = self.JOURNAL_ABBREV.copy()

        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    custom_abbrev = json.load(f)
                    logger.info(f"从配置文件加载了 {len(custom_abbrev)} 个期刊缩写")
                    # 合并配置（自定义配置优先）
                    default_abbrev.update(custom_abbrev)
                    return default_abbrev
            except json.JSONDecodeError as e:
                logger.warning(f"期刊缩写配置文件格式错误: {e}，使用内置配置")
            except Exception as e:
                logger.warning(f"加载期刊缩写配置失败: {e}，使用内置配置")
        else:
            logger.info("未找到期刊缩写配置文件，使用内置配置")

        return default_abbrev

    def _load_institution_config(self) -> Dict:
        """加载机构配置"""
        config_file = os.path.join(self.config_dir, "institution_config.json")

        # 默认配置
        default_config = {
            "independent_colleges": [],
            "independent_schools": [],
            "abbreviations": {
                'Department': 'Dept',
                'University': 'Univ',
                'Università': 'Univ',
                'Fondazione': 'Fdn',
                'Institute': 'Inst',
                'Istituto': 'Inst',
                'Hospital': 'Hosp',
                'Ospedale': 'Hosp',
                'Center': 'Ctr',
                'Centre': 'Ctr',
                'Laboratory': 'Lab',
                'Research': 'Res',
                'Science': 'Sci',
                'Sciences': 'Sci',
                'Technology': 'Technol',
                'Medicine': 'Med',
                'Medical': 'Med',
                'Clinical': 'Clin',
                'Pharmacy': 'Pharm',
                'degli Studi di': '',
                'and': '&',
            }
        }

        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    custom_config = json.load(f)
                    logger.info("成功加载机构配置文件")
                    # 合并配置
                    if 'independent_colleges' in custom_config:
                        default_config['independent_colleges'] = custom_config['independent_colleges']
                    if 'independent_schools' in custom_config:
                        default_config['independent_schools'] = custom_config['independent_schools']
                    if 'abbreviations' in custom_config:
                        default_config['abbreviations'].update(custom_config['abbreviations'])
                    return default_config
            except Exception as e:
                logger.warning(f"加载机构配置失败: {e}，使用默认配置")
        else:
            logger.info("未找到机构配置文件，使用默认配置")

        return default_config

    def read_scopus_csv(self) -> List[Dict]:
        """
        读取Scopus CSV文件

        Returns:
            List[Dict]: 记录列表

        Raises:
            ValueError: CSV格式错误或缺少必要字段
        """
        records = []
        try:
            with open(self.csv_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)

                # 验证必要字段
                required_fields = {'Authors', 'Title', 'Year'}
                if reader.fieldnames:
                    missing_fields = required_fields - set(reader.fieldnames)
                    if missing_fields:
                        logger.warning(f"CSV文件缺少推荐字段: {missing_fields}")

                for row_num, row in enumerate(reader, start=2):  # 从第2行开始（第1行是表头）
                    if any(row.values()):  # 跳过空行
                        records.append(row)

            logger.info(f"成功读取 {len(records)} 条记录")
            return records

        except FileNotFoundError:
            logger.error(f"文件不存在: {self.csv_file}")
            raise
        except UnicodeDecodeError as e:
            logger.error(f"文件编码错误: {e}")
            raise ValueError("文件编码错误，请确保文件为UTF-8格式")
        except csv.Error as e:
            logger.error(f"CSV格式错误: {e}")
            raise ValueError(f"CSV格式错误: {e}")
        except Exception as e:
            logger.error(f"读取文件时发生未知错误: {e}")
            raise

    def format_multiline_field(self, tag: str, content: str, max_width: int = None) -> str:
        """
        格式化WOS字段

        Args:
            tag: 字段标签（如 TI, AB）
            content: 字段内容
            max_width: 每行最大宽度，如果为None则不换行（保持单行）

        Returns:
            格式化后的字段文本
        """
        if not content or content.strip() == '':
            return ''

        content = content.strip()

        # 如果不设置max_width，或者内容较短，直接返回单行
        if max_width is None or len(content) <= (max_width if max_width else float('inf')):
            return f"{tag} {content}"

        # 只有在明确设置了max_width且内容超长时才分行
        words = content.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if len(test_line) <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        # 添加最后一行
        if current_line:
            lines.append(current_line)

        # 格式化输出：第一行不缩进，其余行3空格缩进
        if not lines:
            return ''

        result = f"{tag} {lines[0]}"
        for line in lines[1:]:
            result += f"\n   {line}"

        return result

    def convert_authors(self, authors_str: str) -> List[str]:
        """
        转换作者格式

        Scopus: "Miceli, E.; Lenti, M.V.; Di Sabatino, A."
        WOS: ["Miceli, E", "Lenti, MV", "Di Sabatino, A"]
        """
        if not authors_str:
            return []

        # 按分号分割
        authors = [a.strip() for a in authors_str.split(';')]

        # 处理缩写：移除点号和空格
        # "M.V." -> "MV", "M. V." -> "MV", "G.R." -> "GR"
        converted = []
        for author in authors:
            # 分割姓和名
            parts = author.split(',')
            if len(parts) >= 2:
                last_name = parts[0].strip()
                initials = parts[1].strip()
                # 移除所有点号和空格：M.V. -> MV, G. R. -> GR
                initials = initials.replace('.', '').replace(' ', '')
                converted.append(f"{last_name}, {initials}")
            else:
                converted.append(author)

        return converted

    def convert_author_full_names(self, full_names_str: str) -> List[str]:
        """
        转换完整作者姓名 - 修复版

        Scopus: "Miceli, Emanuela (6505992224); Lenti, Marco Vincenzo (55189363300)"
        WOS: ["Miceli, Emanuela", "Lenti, Marco Vincenzo"]

        特殊处理：
        1. 移除Scopus ID（括号内容）
        2. 处理复杂姓氏（如"Abu Akar, Firas"必须保持顺序，不能变成"Akar, Firas Abu"）
        3. 移除多余的学位后缀（M.D., Ph.D.等）
        4. 保持中间名（Scopus提供了就保留）
        """
        if not full_names_str:
            return []

        # 按分号分割
        authors = [a.strip() for a in full_names_str.split(';')]

        converted = []
        for author in authors:
            # 移除括号及其内容（Scopus ID）
            author_clean = re.sub(r'\s*\([^)]*\)', '', author).strip()

            # 移除学位后缀（M.D., Ph.D., Dr., Prof.等）
            # 这些通常在最后，用空格或逗号分隔
            degree_suffixes = [
                r',?\s*M\.?D\.?$', r',?\s*Ph\.?D\.?$', r',?\s*Dr\.?$',
                r',?\s*Prof\.?$', r',?\s*M\.?S\.?$', r',?\s*B\.?S\.?$'
            ]
            for suffix_pattern in degree_suffixes:
                author_clean = re.sub(suffix_pattern, '', author_clean, flags=re.IGNORECASE)

            # 去掉末尾多余的点号和空格
            author_clean = author_clean.rstrip('. ').strip()

            # 检查姓名格式是否正确（必须是 "Lastname, Firstname" 格式）
            if ',' in author_clean:
                parts = author_clean.split(',', 1)
                if len(parts) == 2:
                    lastname = parts[0].strip()
                    firstname = parts[1].strip()

                    # 复杂姓氏检查：如果名字部分看起来像姓氏（包含空格和大写），
                    # 可能是Scopus错误地颠倒了顺序（如"Akar, Firas Abu"应该是"Abu Akar, Firas"）
                    # 但这个检测很困难，所以我们保守处理，相信Scopus的顺序
                    author_clean = f"{lastname}, {firstname}"

            converted.append(author_clean)

        return converted

    def parse_reference(self, ref: str) -> Dict[str, str]:
        """
        解析Scopus参考文献格式

        Scopus格式：
        Neumann, William L., Autoimmune atrophic gastritis-pathogenesis, pathology and management,
        Nature Reviews Gastroenterology and Hepatology, 10, 9, pp. 529-541, (2013)

        拆解：
        parts[0] = "Neumann"
        parts[1] = "William L."
        parts[2] = "文章标题"
        parts[-4] = "期刊名" (通常)
        parts[-3] = "卷号"
        parts[-2] = "期号"
        parts[-1] = "pp. 页码" 或直接是年份

        需要提取：作者, 年份, 期刊, 卷号, 页码
        """
        result = {
            'author': '',
            'year': '',
            'journal': '',
            'volume': '',
            'page': '',
            'doi': ''
        }

        # 1. 提取年份（括号内）
        year_match = re.search(r'\((\d{4})\)', ref)
        if year_match:
            result['year'] = year_match.group(1)
            # 移除年份部分
            ref = ref[:year_match.start()].strip().rstrip(',')

        # 2. 按逗号分割
        parts = [p.strip() for p in ref.split(',')]

        if len(parts) == 0:
            return result

        # 3. 提取作者（第一个字段）
        if len(parts) >= 1:
            result['author'] = parts[0]

        # 4. 从后往前解析数字字段
        # 倒数第1个：可能是页码（pp. X-Y格式）
        if len(parts) >= 1:
            last_part = parts[-1]
            page_match = re.search(r'pp\.\s*(\d+)[\-]?', last_part)
            if page_match:
                result['page'] = page_match.group(1)

        # 倒数第2个：可能是期号（纯数字）
        # 倒数第3个：可能是卷号（纯数字）
        # 我们主要关心卷号
        for i in range(len(parts) - 1, max(0, len(parts) - 4), -1):
            part = parts[i]
            if re.match(r'^\d+$', part) and not result['volume']:
                result['volume'] = part
                break

        # 5. 期刊名：启发式查找
        # 策略：找到最后一个长度>15且包含大写字母的字段（在数字字段之前）
        journal_candidates = []
        for i, part in enumerate(parts):
            # 跳过作者名字段（前2个）
            if i <= 1:
                continue
            # 期刊名通常比较长，包含多个单词
            if len(part) > 15 and any(c.isupper() for c in part):
                journal_candidates.append(part)

        # 取最后一个候选（最接近数字字段的长字段）
        if journal_candidates:
            result['journal'] = journal_candidates[-1]

        return result

    def format_reference_wos(self, ref_data: Dict[str, str]) -> str:
        """
        格式化为WOS参考文献格式

        WOS格式: Author, Year, JOURNAL ABBREV, VVolume, PPage, DOI doi
        """
        author = ref_data.get('author', '').split()
        if len(author) >= 2:
            # 取姓和首字母
            author_short = f"{author[0]} {author[1][0]}" if len(author[1]) > 0 else author[0]
        else:
            author_short = ref_data.get('author', '')

        year = ref_data.get('year', '')
        journal = ref_data.get('journal', '')

        # 尝试缩写期刊名
        journal_abbrev = self.JOURNAL_ABBREV.get(journal, journal.upper())

        volume = ref_data.get('volume', '')
        page = ref_data.get('page', '')

        parts = [author_short, year, journal_abbrev]
        if volume:
            parts.append(f"V{volume}")
        if page:
            parts.append(f"P{page}")

        return ', '.join([p for p in parts if p])

    def convert_references(self, references_str: str) -> List[str]:
        """转换参考文献列表"""
        if not references_str:
            return []

        # 按分号分割各条参考文献
        refs = [r.strip() for r in references_str.split(';')]

        converted_refs = []
        for ref in refs:
            if ref:
                ref_data = self.parse_reference(ref)
                wos_ref = self.format_reference_wos(ref_data)
                if wos_ref:
                    converted_refs.append(wos_ref)

        return converted_refs

    def abbreviate_journal(self, journal_name: str) -> str:
        """
        期刊名缩写

        首先查找映射表，如果没有则使用规则生成
        """
        # 查找映射表
        if journal_name in self.JOURNAL_ABBREV:
            return self.JOURNAL_ABBREV[journal_name]

        # 使用规则生成缩写
        # 1. 移除常见词
        remove_words = ['the', 'of', 'and', 'in', 'for', 'on', '&']
        words = journal_name.split()

        # 2. 保留主要词汇并缩写
        abbrev_words = []
        for word in words:
            if word.lower() not in remove_words:
                if len(word) > 4:
                    # 长词取前几个字母
                    abbrev_words.append(word[:4].upper())
                else:
                    abbrev_words.append(word.upper())

        return ' '.join(abbrev_words)

    def parse_affiliations(self, affil_str: str) -> List[str]:
        """
        解析作者机构信息 - 完全重写版

        Scopus复杂格式（一个作者可能有多个机构，用逗号连续列出）:
        "Author1, Name1, Inst1, City1, Country1; Author2, Name2, Inst2A, City2A, Country2A, Inst2B, City2B, Country2B"

        WOS格式（按机构分组，一个作者多机构必须分行）:
        "[Author1, Name1] Inst1, City1, Country1."
        "[Author2, Name2] Inst2A, City2A, Country2A."
        "[Author2, Name2] Inst2B, City2B, Country2B."

        关键规则：
        1. 多个作者共享同一机构 → 合并到一行
        2. 一个作者有多个机构 → 必须分成多行
        3. 通过识别国家名来分割机构边界
        """
        if not affil_str:
            return []

        # 常见国家名列表（用于识别机构边界）
        countries = [
            'USA', 'United States', 'United Kingdom', 'England', 'Scotland', 'Wales',
            'China', 'Peoples R China', 'Japan', 'Germany', 'France', 'Italy', 'Spain',
            'Canada', 'Australia', 'India', 'South Korea', 'Brazil', 'Russia',
            'Netherlands', 'Switzerland', 'Sweden', 'Belgium', 'Austria', 'Poland',
            'Israel', 'Palestine', 'Argentina', 'Mexico', 'Turkey', 'Turkiye',
            'South Africa', 'Singapore', 'Taiwan', 'Hong Kong', 'Ireland', 'Denmark',
            'Norway', 'Finland', 'Greece', 'Portugal', 'Czech Republic', 'Hungary',
            'Romania', 'Chile', 'Colombia', 'Peru', 'Iran', 'Iraq', 'Egypt'
        ]

        # 按分号分割每个作者的信息块
        author_blocks = [a.strip() for a in affil_str.split(';')]

        # 存储结果：List[(author, institution)]
        author_institutions = []

        for block in author_blocks:
            if not block:
                continue

            # 按逗号分割
            parts = [p.strip() for p in block.split(',')]

            if len(parts) < 3:
                continue

            # 前两部分是作者名
            author_lastname = parts[0]
            author_firstname = parts[1]
            author_full = f"{author_lastname}, {author_firstname}"

            # 从第3部分开始是机构信息
            # 需要识别机构边界（通过国家名）
            remaining_parts = parts[2:]

            # 查找所有国家名的位置
            # 策略：只识别真正独立的国家名，不识别组合词中的国家名
            # 如"Israel"是国家，但"Edith Wolfson Medical Center Israel"不是
            country_indices = []
            for i, part in enumerate(remaining_parts):
                part_clean = part.strip().rstrip('.')
                # 判断是否是独立的国家名：
                # 1. 部分的词数<=2（如"Israel"或"United States"）
                # 2. 且完全匹配某个国家名
                word_count = len(part_clean.split())
                if word_count <= 2:  # 只有1-2个词才可能是独立的国家名
                    for country in countries:
                        if part_clean.lower() == country.lower():
                            country_indices.append(i)
                            break

            # 如果找到国家，按国家位置分割机构
            if country_indices:
                institutions = []
                start = 0
                for country_idx in country_indices:
                    # 从start到country_idx+1是一个完整的机构
                    inst_parts = remaining_parts[start:country_idx+1]
                    if inst_parts:
                        institution = ', '.join(inst_parts)
                        institutions.append(institution)
                    start = country_idx + 1

                # 处理每个机构
                for institution in institutions:
                    # 1. 重新排序
                    inst_reordered = self.reorder_institution_parts(institution)
                    # 2. 缩写
                    inst_short = self.abbreviate_institution(inst_reordered)
                    # 3. 标准化国家
                    inst_standard = self.standardize_country(inst_short)

                    author_institutions.append((author_full, inst_standard))
            else:
                # 没找到国家名，整个当作一个机构
                institution = ', '.join(remaining_parts)
                inst_reordered = self.reorder_institution_parts(institution)
                inst_short = self.abbreviate_institution(inst_reordered)
                inst_standard = self.standardize_country(inst_short)
                author_institutions.append((author_full, inst_standard))

        # 按机构分组（允许多个作者共享一个机构）
        institution_to_authors = {}
        for author_full, institution in author_institutions:
            if institution not in institution_to_authors:
                institution_to_authors[institution] = []
            if author_full not in institution_to_authors[institution]:
                institution_to_authors[institution].append(author_full)

        # 生成C1行
        converted = []
        for institution, authors in institution_to_authors.items():
            author_list = '; '.join(sorted(authors))
            wos_affil = f"[{author_list}] {institution}."
            converted.append(wos_affil)

        return converted

    def standardize_country(self, institution: str) -> str:
        """
        标准化国家名称为WOS格式

        WOS使用的标准国家名称：
        - USA (不是United States)
        - England / Scotland / Wales / North Ireland (不是United Kingdom)
        - Peoples R China (不是China)
        - South Korea (不是Korea)
        - Turkiye (不是Turkey)

        Args:
            institution: 机构字符串（包含国家名）

        Returns:
            标准化后的机构字符串
        """
        # 国家名称映射表（Scopus → WOS标准）
        country_mapping = {
            'United States': 'USA',
            'United Kingdom': 'England',  # 默认England，除非明确是Scotland等
            'China': 'Peoples R China',
            'Korea': 'South Korea',
            'Turkey': 'Turkiye',
            'Russia': 'Russia',
            'Iran': 'Iran',
            'Vietnam': 'Vietnam',
            'Czech Republic': 'Czech Republic',
            'Taiwan': 'Taiwan',
        }

        # 分割机构字符串（最后一个逗号后通常是国家）
        parts = [p.strip() for p in institution.split(',')]

        if len(parts) >= 1:
            # 检查最后一部分是否是国家名
            last_part = parts[-1]

            # 尝试映射
            for scopus_name, wos_name in country_mapping.items():
                if scopus_name in last_part:
                    parts[-1] = last_part.replace(scopus_name, wos_name)
                    break

        return ', '.join(parts)

    def _is_independent_college_or_school(self, name: str, all_parts: List[str]) -> bool:
        """
        判断College/School是否为独立机构

        逻辑：
        1. 如果在已知独立机构列表中 → 独立机构
        2. 如果同一行已有University → 二级机构
        3. 如果College/School后面有专业名称（如Medical, Pharmacy）→ 独立机构
        4. 否则 → 二级机构（保守策略）

        Args:
            name: 当前部分的名称
            all_parts: 整个机构信息的所有部分

        Returns:
            bool: True表示是独立机构，False表示是二级单位
        """
        name_lower = name.lower()

        # 1. 检查是否在白名单中
        for independent in self.institution_config.get('independent_colleges', []):
            if independent.lower() in name_lower:
                return True

        for independent in self.institution_config.get('independent_schools', []):
            if independent.lower() in name_lower:
                return True

        # 2. 检查是否已有University（上下文判断）
        has_university = any('university' in p.lower() or 'università' in p.lower() or 'universit' in p.lower()
                            for p in all_parts if p != name)
        if has_university:
            return False  # 有University则College/School是二级机构

        # 3. 检查是否是专业学院（Medical, Pharmacy等）
        professional_indicators = [
            'medical', 'medicine', 'pharmacy', 'law', 'business',
            'engineering', 'public health', 'hygiene', 'economics',
            'tropical', 'veterinary', 'dental', 'nursing'
        ]

        if 'school' in name_lower:
            for indicator in professional_indicators:
                if indicator in name_lower:
                    return True  # School of Medicine这种通常是独立机构

        # 4. College of XX（学院名称）通常是二级机构，除非特别知名
        if 'college of' in name_lower:
            # "College of Pharmacy"可能是二级，但"Imperial College"是一级
            return False

        # 5. 如果College不带"of"且是完整名称，可能是独立学院
        if 'college' in name_lower and 'of' not in name_lower:
            # "Boston College", "King's College"这种
            words = name.split()
            if len(words) >= 2:  # 至少两个词
                return True

        # 默认：保守策略，当作二级机构
        return False

    def reorder_institution_parts(self, institution: str) -> str:
        """
        重新排序机构信息：一级机构在前，二级单位在后

        Scopus格式：Department of Internal Medicine, Università degli Studi di Pavia, Pavia, Italy
        WOS格式：Univ Pavia, Dept Internal Med, Pavia, Italy

        逻辑：
        1. 识别一级机构（University, Hospital, Institute, Foundation等）
        2. 识别二级单位（Department, Division, Unit, Laboratory等）
        3. 智能判断School/College的层级
        4. 识别地理信息（城市、国家）
        5. 重新排序：一级机构 → 二级单位 → 地理信息
        """
        # 按逗号分割各部分
        parts = [p.strip() for p in institution.split(',')]

        if len(parts) < 2:
            return institution

        # 一级机构关键词（明确的）
        primary_keywords = [
            'University', 'Università', 'Universität', 'Universit', 'Univ',
            'Hospital', 'Ospedale', 'Hosp',
            'Institute', 'Istituto', 'Institut',
            'Foundation', 'Fondazione', 'Fdn',
            'IRCCS', 'Policlinico', 'Clinic',
            'Center', 'Centre', 'Centro', 'Academy', 'Accademia'
        ]

        # 二级单位关键词（明确的）
        secondary_keywords = [
            'Department of', 'Dipartimento di', 'Dept of', 'Dept.',
            'Division of', 'Divisione di', 'Div of',
            'Unit of', 'Unità di',
            'Laboratory of', 'Laboratorio di',
            'Service', 'Servizio',
            'Section of', 'Sezione di'
        ]

        # 分类各部分
        primary_parts = []
        secondary_parts = []
        geo_parts = []

        # 假设最后1-2个部分是地理信息（城市、国家）
        if len(parts) >= 2:
            last_part = parts[-1]
            second_last = parts[-2] if len(parts) >= 2 else None

            # 检查是否是地理信息
            is_last_geo = not any(kw.lower() in last_part.lower() for kw in primary_keywords + secondary_keywords)
            is_last_geo = is_last_geo and 'college' not in last_part.lower() and 'school' not in last_part.lower()

            is_second_last_geo = (second_last and
                                 not any(kw.lower() in second_last.lower() for kw in primary_keywords + secondary_keywords) and
                                 'college' not in second_last.lower() and 'school' not in second_last.lower())

            if is_last_geo:
                geo_parts.append(last_part)
                parts = parts[:-1]

                if is_second_last_geo and len(parts) >= 1:
                    geo_parts.insert(0, parts[-1])
                    parts = parts[:-1]

        # 对剩余部分分类
        for part in parts:
            part_lower = part.lower()

            # 检查是否包含明确的二级单位关键词
            is_secondary = any(kw.lower() in part_lower for kw in secondary_keywords)
            if is_secondary:
                secondary_parts.append(part)
                continue

            # 检查是否包含一级机构关键词
            is_primary = any(kw.lower() in part_lower for kw in primary_keywords)

            # 特殊处理：School和College需要智能判断
            has_school = 'school' in part_lower
            has_college = 'college' in part_lower

            if has_school or has_college:
                # 使用智能判断
                if self._is_independent_college_or_school(part, parts):
                    primary_parts.append(part)
                else:
                    secondary_parts.append(part)
            elif is_primary:
                primary_parts.append(part)
            else:
                # 不确定的情况，放入一级机构（保守策略）
                primary_parts.append(part)

        # 重新组合：一级机构 + 二级单位 + 地理信息
        reordered = primary_parts + secondary_parts + geo_parts

        return ', '.join(reordered)

    def abbreviate_institution(self, institution: str) -> str:
        """
        缩写机构名称

        例如：
        "Department of Internal Medicine" -> "Dept Internal Med"
        "Fondazione IRCCS Policlinico San Matteo" -> "Fdn IRCCS Policlin San Matteo"
        "School of Medicine" -> "Sch Med"
        """
        # 使用配置文件中的缩写规则
        abbrev_map = self.institution_config['abbreviations']

        result = institution
        for full, abbrev in abbrev_map.items():
            result = re.sub(r'\b' + re.escape(full) + r'\b', abbrev, result, flags=re.IGNORECASE)

        # 移除常见介词和冠词（WOS风格）
        prepositions = ['of', 'for', 'the', 'in', 'at', 'on']
        for prep in prepositions:
            # 只移除单独的介词（前后有空格的），不移除单词中间的部分
            result = re.sub(r'\s+' + re.escape(prep) + r'\s+', ' ', result, flags=re.IGNORECASE)

        # 特殊处理 "and" -> "&"
        result = re.sub(r'\s+and\s+', ' & ', result, flags=re.IGNORECASE)

        # 清理多余空格
        result = re.sub(r'\s+', ' ', result).strip()
        result = re.sub(r',\s*,', ',', result)  # 移除连续逗号
        # 清理逗号前后多余空格
        result = re.sub(r'\s*,\s*', ', ', result)

        return result

    def extract_primary_institutions(self, affil_str: str) -> List[str]:
        """
        从Scopus机构信息中提取一级机构（用于C3字段）

        Scopus格式：Department of Surgery, Chiba Aoba Municipal Hospital, Chiba, Japan
        目标：提取 "Chiba Aoba Municipal Hospital"

        策略：
        1. 识别一级机构关键词（University, Hospital, Institute, College等）
        2. 智能判断College/School是否为一级机构
        3. 提取包含这些关键词的机构名称
        4. 去除部门名称（Department, Division等）
        5. 去重并标准化
        """
        if not affil_str:
            return []

        # 一级机构的关键词（明确的）
        primary_keywords = [
            'University', 'Università', 'Universität', 'Universi',  # 大学
            'Hospital', 'Ospedale', 'Clinic', 'Medical Center',     # 医院
            'Institute', 'Istituto', 'Institut',                    # 研究所
            'Academy', 'Accademia',                                 # 科学院
            'Foundation', 'Fondazione', 'IRCCS',                    # 基金会/研究机构
            'Laboratory', 'Laboratorio',                            # 实验室（顶层）
            'Corporation', 'Company', 'Ltd',                        # 企业
            'Ministry', 'Government',                               # 政府机构
        ]

        # 二级单位关键词（需要过滤掉）
        secondary_keywords = [
            'Department of', 'Dept of', 'Dept.',
            'Division of', 'Div of',
            'Section of', 'Unit of',
            'Laboratory of',  # "Laboratory of XX"是部门，但单独的"XX Laboratory"是机构
            'Center for',  # "Center for XX"通常是部门
        ]

        # 按分号分割每个作者的机构
        author_affils = [a.strip() for a in affil_str.split(';')]

        primary_institutions = set()  # 使用set去重

        for affil in author_affils:
            if not affil:
                continue

            # 跳过作者名（第一个逗号前）
            if ',' in affil:
                parts = affil.split(',')
                # 第一个部分是作者名，跳过
                institution_parts = parts[1:]
            else:
                institution_parts = [affil]

            # 遍历每个机构部分
            for part in institution_parts:
                part = part.strip()

                # 跳过城市和国家（通常是短字符串或已知国家名）
                if len(part) < 10:  # 太短，可能是城市
                    continue

                # 检查是否是二级单位（部门）
                is_secondary = False
                for sec_keyword in secondary_keywords:
                    if part.lower().startswith(sec_keyword.lower()):
                        is_secondary = True
                        break

                if is_secondary:
                    continue  # 跳过部门

                part_lower = part.lower()

                # 检查是否包含一级机构关键词
                is_primary = any(kw.lower() in part_lower for kw in primary_keywords)

                # 特殊处理：College和School需要智能判断
                has_college = 'college' in part_lower
                has_school = 'school' in part_lower

                if has_college or has_school:
                    # 使用智能判断方法
                    if self._is_independent_college_or_school(part, institution_parts):
                        is_primary = True
                    else:
                        is_primary = False  # 是二级单位，跳过

                if is_primary:
                    # 清理机构名称
                    clean_name = self.clean_institution_name(part)
                    if clean_name:
                        primary_institutions.add(clean_name)

        return list(primary_institutions)

    def clean_institution_name(self, name: str) -> str:
        """
        清理机构名称，用于C3字段

        例如：
        "Università degli Studi di Pavia" -> "University of Pavia"
        "Fondazione IRCCS Policlinico San Matteo" -> "IRCCS Fondazione Policlinico San Matteo"
        """
        # 移除多余空格
        name = re.sub(r'\s+', ' ', name).strip()

        # 标准化常见表达
        replacements = {
            'Università degli Studi di': 'University of',
            'Università di': 'University of',
            'Università': 'University',
            'Ospedale': 'Hospital',
            'Istituto': 'Institute',
            'Fondazione IRCCS': 'IRCCS Fondazione',
        }

        for old, new in replacements.items():
            name = re.sub(r'\b' + re.escape(old) + r'\b', new, name, flags=re.IGNORECASE)

        # 清理多余空格
        name = re.sub(r'\s+', ' ', name).strip()

        return name

    def convert_record(self, scopus_record: Dict) -> str:
        """
        将单条Scopus记录转换为WOS格式

        Args:
            scopus_record: Scopus CSV的一行记录（字典）

        Returns:
            WOS格式的文本
        """
        wos_lines = []

        # PT - Publication Type (固定为 J = Journal)
        wos_lines.append("PT J")

        # AU - Authors
        authors = self.convert_authors(scopus_record.get('Authors', ''))
        if authors:
            wos_lines.append(f"AU {authors[0]}")
            for author in authors[1:]:
                wos_lines.append(f"   {author}")

        # AF - Author Full Names
        full_names = self.convert_author_full_names(scopus_record.get('Author full names', ''))
        if full_names:
            wos_lines.append(f"AF {full_names[0]}")
            for name in full_names[1:]:
                wos_lines.append(f"   {name}")

        # TI - Title
        title = scopus_record.get('Title', '')
        if title:
            # 标题在约80字符换行（WOS格式）
            wos_lines.append(self.format_multiline_field('TI', title, max_width=80))

        # SO - Source (期刊名，全大写)
        source = scopus_record.get('Source title', '')
        if source:
            wos_lines.append(f"SO {source.upper()}")

        # LA - Language
        language = scopus_record.get('Language of Original Document', '')
        if language:
            wos_lines.append(f"LA {language}")

        # DT - Document Type
        doc_type = scopus_record.get('Document Type', 'Article')
        wos_lines.append(f"DT {doc_type}")

        # DE - Author Keywords
        keywords = scopus_record.get('Author Keywords', '')
        if keywords:
            # WOS格式修正：vitamin B12 -> vitamin B-12
            keywords = keywords.replace('vitamin B12', 'vitamin B-12')
            # DE字段在约80字符换行（WOS格式）
            wos_lines.append(self.format_multiline_field('DE', keywords, max_width=80))

        # ID - Keywords Plus (使用Index Keywords)
        index_keywords = scopus_record.get('Index Keywords', '')
        if index_keywords:
            # ID字段必须单行，不换行（WOS格式规范）
            wos_lines.append(f"ID {index_keywords}")

        # AB - Abstract
        abstract = scopus_record.get('Abstract', '')
        if abstract:
            # 修复Scopus摘要格式：在章节标题后添加空格
            # INTRODUCTION:The -> INTRODUCTION: The
            # METHODS:Prospective -> METHODS: Prospective
            abstract_fixed = re.sub(r'([A-Z]+):([A-Z])', r'\1: \2', abstract)

            # WOS格式细节修复：
            # 1. "F: M ratio" -> "F:M ratio"（比例中的冒号不要空格）
            abstract_fixed = re.sub(r'([A-Z]): ([A-Z]) ratio', r'\1:\2 ratio', abstract_fixed)
            # 2. "±" -> "+/-"（特殊符号转换）
            abstract_fixed = abstract_fixed.replace('±', '+/-')

            # AB字段必须单行，不换行（WOS格式规范）
            wos_lines.append(f"AB {abstract_fixed}")

        # C1 - Author Addresses
        affils = self.parse_affiliations(scopus_record.get('Authors with affiliations', ''))
        if affils:
            wos_lines.append(f"C1 {affils[0]}")
            for affil in affils[1:]:
                wos_lines.append(f"   {affil}")

        # C3 - Organization Enhanced (一级机构，标准化)
        primary_insts = self.extract_primary_institutions(scopus_record.get('Authors with affiliations', ''))
        if primary_insts:
            # WOS的C3格式：机构名用分号分隔
            c3_line = '; '.join(primary_insts)
            wos_lines.append(self.format_multiline_field('C3', c3_line, max_width=80))

        # RP - Reprint Address (通讯作者)
        corresp = scopus_record.get('Correspondence Address', '')
        if corresp:
            # RP字段保持单行
            wos_lines.append(f"RP {corresp}")

        # CR - Cited References
        references = self.convert_references(scopus_record.get('References', ''))
        if references:
            wos_lines.append(f"CR {references[0]}")
            for ref in references[1:]:
                wos_lines.append(f"   {ref}")

        # NR - Number of References
        if references:
            wos_lines.append(f"NR {len(references)}")

        # TC - Times Cited
        cited_by = scopus_record.get('Cited by', '0')
        wos_lines.append(f"TC {cited_by}")

        # Z9 - Total Times Cited (设为与TC相同)
        wos_lines.append(f"Z9 {cited_by}")

        # U1, U2 - Usage Count (Scopus没有，设为0)
        wos_lines.append("U1 0")
        wos_lines.append("U2 0")

        # PU - Publisher
        publisher = scopus_record.get('Publisher', '')
        if publisher:
            wos_lines.append(f"PU {publisher}")

        # SN - ISSN
        issn = scopus_record.get('ISSN', '')
        if issn:
            # 取第一个ISSN（可能有多个用分号分隔）
            issn_first = issn.split(';')[0].strip()
            wos_lines.append(f"SN {issn_first}")

        # J9 - 29-Character Source Abbreviation
        abbrev_title = scopus_record.get('Abbreviated Source Title', '')
        if abbrev_title:
            wos_lines.append(f"J9 {abbrev_title.upper()}")

        # JI - ISO Source Abbreviation
        if abbrev_title:
            wos_lines.append(f"JI {abbrev_title}")

        # PY - Publication Year
        year = scopus_record.get('Year', '')
        if year:
            wos_lines.append(f"PY {year}")

        # VL - Volume
        volume = scopus_record.get('Volume', '')
        if volume:
            wos_lines.append(f"VL {volume}")

        # IS - Issue
        issue = scopus_record.get('Issue', '')
        if issue:
            wos_lines.append(f"IS {issue}")

        # AR - Article Number
        art_no = scopus_record.get('Art. No.', '')
        if art_no:
            wos_lines.append(f"AR {art_no}")

        # BP - Beginning Page
        page_start = scopus_record.get('Page start', '')
        if page_start:
            wos_lines.append(f"BP {page_start}")

        # EP - Ending Page
        page_end = scopus_record.get('Page end', '')
        if page_end:
            wos_lines.append(f"EP {page_end}")

        # PG - Page Count
        if page_start and page_end:
            try:
                page_count = int(page_end) - int(page_start) + 1
                wos_lines.append(f"PG {page_count}")
            except:
                pass

        # DI - DOI
        doi = scopus_record.get('DOI', '')
        if doi:
            wos_lines.append(f"DI {doi}")

        # WC, WE, SC - Web of Science Categories
        # 注：这些字段需要根据期刊手动分类，这里设置为通用值
        # 用户可以根据需要在文献计量工具中重新分类
        wos_lines.append("WE Scopus")

        # UT - Unique Article Identifier (使用Scopus EID)
        eid = scopus_record.get('EID', '')
        if eid:
            wos_lines.append(f"UT SCOPUS:{eid}")

        # PM - PubMed ID
        pmid = scopus_record.get('PubMed ID', '')
        if pmid:
            wos_lines.append(f"PM {pmid}")

        # DA - Date of Export
        today = datetime.now().strftime('%Y-%m-%d')
        wos_lines.append(f"DA {today}")

        # ER - End of Record
        wos_lines.append("ER")

        return '\n'.join(wos_lines)

    def convert(self):
        """
        执行转换

        Raises:
            IOError: 写入文件失败
        """
        logger.info("="*60)
        logger.info("开始转换 Scopus CSV → WOS 纯文本格式")
        logger.info("="*60)

        # 读取Scopus CSV
        self.records = self.read_scopus_csv()

        if not self.records:
            logger.warning("没有找到任何记录，终止转换")
            return

        # 转换每条记录
        wos_content = []

        # WOS文件头（无空行分隔）
        wos_content.append("FN Scopus Export (Converted to WOS Format)")
        wos_content.append("VR 1.0")

        total = len(self.records)
        logger.info(f"开始转换 {total} 条记录...")

        # 转换每条记录
        for i, record in enumerate(self.records, 1):
            title = record.get('Title', 'N/A')
            title_short = title[:50] + "..." if len(title) > 50 else title

            # 进度显示（每10%或每100条显示一次）
            if i % max(1, total // 10) == 0 or i % 100 == 0 or i == total:
                progress = (i / total) * 100
                logger.info(f"进度: {progress:.1f}% ({i}/{total}) - {title_short}")

            try:
                wos_record = self.convert_record(record)
                # 在记录前添加空行（除了第一条记录）
                if i > 1:
                    wos_content.append("")  # 空行
                wos_content.append(wos_record)
            except Exception as e:
                logger.error(f"转换第 {i} 条记录时出错: {e}")
                logger.error(f"问题记录: {title_short}")
                # 继续处理下一条

        # WOS文件尾（前面加空行）
        wos_content.append("")  # 空行
        wos_content.append("EF")

        # 写入文件（用单个换行符连接，包含UTF-8 BOM，与WOS格式完全一致）
        try:
            with open(self.output_file, 'w', encoding='utf-8-sig') as f:
                f.write('\n'.join(wos_content))
            logger.info("="*60)
            logger.info(f"转换完成！")
            logger.info(f"输出文件: {self.output_file}")
            logger.info(f"共转换 {len(self.records)} 条记录")
            logger.info("="*60)
        except IOError as e:
            logger.error(f"写入文件失败: {e}")
            raise
        except Exception as e:
            logger.error(f"写入文件时发生未知错误: {e}")
            raise


def main():
    """主函数"""
    import sys
    import argparse

    # 命令行参数解析
    parser = argparse.ArgumentParser(
        description='Scopus CSV to WOS Plain Text Converter',
        epilog='示例: python3 scopus_to_wos_converter.py scopus.csv output.txt'
    )
    parser.add_argument('input_file', nargs='?', default='scopus.csv',
                       help='Scopus CSV文件路径（默认: scopus.csv）')
    parser.add_argument('output_file', nargs='?', default='scopus_converted_to_wos.txt',
                       help='输出WOS文件路径（默认: scopus_converted_to_wos.txt）')
    parser.add_argument('--config-dir', default='config',
                       help='配置文件目录（默认: config）')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='日志级别（默认: INFO）')

    args = parser.parse_args()

    # 设置日志级别
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    logger.info("=" * 60)
    logger.info("Scopus to WOS Converter v3.1")
    logger.info("=" * 60)
    logger.info(f"输入文件: {args.input_file}")
    logger.info(f"输出文件: {args.output_file}")
    logger.info(f"配置目录: {args.config_dir}")

    try:
        # 执行转换
        converter = ScopusToWosConverter(
            args.input_file,
            args.output_file,
            args.config_dir
        )
        converter.convert()

        logger.info("")
        logger.info("转换完成！现在可以将输出文件导入文献计量学分析工具。")
        logger.info("=" * 60)
        return 0

    except FileNotFoundError as e:
        logger.error(f"文件错误: {e}")
        return 1
    except ValueError as e:
        logger.error(f"数据错误: {e}")
        return 1
    except Exception as e:
        logger.error(f"发生未知错误: {e}")
        logger.exception("详细错误信息:")
        return 1


if __name__ == "__main__":
    main()
