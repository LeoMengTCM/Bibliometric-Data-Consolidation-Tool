#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scopus CSV to WOS Plain Text Converter
======================================

将Scopus数据库导出的CSV文件转换为Web of Science纯文本格式。
用于文献计量学分析工具（CiteSpace, VOSviewer, Bibliometrix等）。

作者：Claude Code
日期：2025-11-03
"""

import csv
import re
from datetime import datetime
from typing import Dict, List, Optional
import textwrap


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

    def __init__(self, csv_file: str, output_file: str):
        """
        初始化转换器

        Args:
            csv_file: Scopus CSV文件路径
            output_file: 输出WOS文件路径
        """
        self.csv_file = csv_file
        self.output_file = output_file
        self.records = []

    def read_scopus_csv(self) -> List[Dict]:
        """读取Scopus CSV文件"""
        records = []
        with open(self.csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if any(row.values()):  # 跳过空行
                    records.append(row)
        print(f"✓ 读取了 {len(records)} 条记录")
        return records

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
        转换完整作者姓名

        Scopus: "Miceli, Emanuela (6505992224); Lenti, Marco Vincenzo (55189363300)"
        WOS: ["Miceli, Emanuela", "Lenti, Marco Vincenzo"]

        注意：Scopus有时只提供缩写，如 "Di Sabatino, A. (6603698114)"
        需要去掉末尾的点号
        """
        if not full_names_str:
            return []

        # 按分号分割
        authors = [a.strip() for a in full_names_str.split(';')]

        # 移除Scopus ID（括号部分）
        converted = []
        for author in authors:
            # 移除括号及其内容
            author_clean = re.sub(r'\s*\([^)]*\)', '', author).strip()
            # 如果名字部分只是缩写（如 "A."），去掉末尾的点号
            # 但保留完整名字
            author_clean = author_clean.rstrip('.')
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
        解析作者机构信息

        Scopus格式（按作者分组）:
        "Miceli, Emanuela, Dept A, Univ X, City, Country; Lenti, Marco Vincenzo, Dept A, Univ X, City, Country; ..."

        WOS格式（按机构分组）:
        "[Author1, Full Name1; Author2, Full Name2] Institution, Dept, City, Country."

        关键：方括号内必须是 [姓, 名]，这样可视化软件才能正确识别机构
        """
        if not affil_str:
            return []

        # 按分号分割每个作者的机构信息
        author_affils = [a.strip() for a in affil_str.split(';')]

        # 存储每个作者（完整姓名）和机构的关系
        author_institutions = []

        for affil in author_affils:
            if not affil:
                continue

            # 按逗号分割
            parts = [p.strip() for p in affil.split(',')]

            if len(parts) >= 3:
                # Scopus格式：第一部分是姓，第二部分是名
                # parts[0] = "Lastname", parts[1] = "Firstname"
                # 需要重组为 "Lastname, Firstname"
                author_lastname = parts[0]
                author_firstname = parts[1]
                author_full = f"{author_lastname}, {author_firstname}"  # "Facciotti, Federica"

                # 机构信息是从第三部分开始的所有部分
                inst_parts = parts[2:]
                institution = ', '.join(inst_parts)

                # 1. 先重新排序：一级机构在前，二级单位在后
                institution_reordered = self.reorder_institution_parts(institution)

                # 2. 再缩写机构名
                institution_short = self.abbreviate_institution(institution_reordered)

                author_institutions.append((author_full, institution_short))

        # 按机构分组（合并相同机构的作者）
        converted = []
        processed_institutions = {}

        for author_full, institution in author_institutions:
            if institution not in processed_institutions:
                processed_institutions[institution] = []
            processed_institutions[institution].append(author_full)

        # 格式化输出：WOS格式 [Author1, Full1; Author2, Full2] Institution.
        for institution, authors in processed_institutions.items():
            # 作者列表用分号分隔，每个作者保持 "Lastname, Firstname" 格式
            author_list = '; '.join(authors)
            wos_affil = f"[{author_list}] {institution}."
            converted.append(wos_affil)

        return converted

    def reorder_institution_parts(self, institution: str) -> str:
        """
        重新排序机构信息：一级机构在前，二级单位在后

        Scopus格式：Department of Internal Medicine, Università degli Studi di Pavia, Pavia, Italy
        WOS格式：Univ Pavia, Dept Internal Med, Pavia, Italy

        逻辑：
        1. 识别一级机构（University, Hospital, Institute, Foundation等）
        2. 识别二级单位（Department, Division, Unit, Laboratory等）
        3. 识别地理信息（城市、国家）
        4. 重新排序：一级机构 → 二级单位 → 地理信息
        """
        # 按逗号分割各部分
        parts = [p.strip() for p in institution.split(',')]

        if len(parts) < 2:
            return institution

        # 一级机构关键词
        primary_keywords = [
            'University', 'Università', 'Universit', 'Univ',
            'Hospital', 'Ospedale', 'Hosp',
            'Institute', 'Istituto', 'Inst',
            'Foundation', 'Fondazione', 'Fdn',
            'College', 'School',
            'IRCCS', 'Policlinico', 'Clinic',
            'Center', 'Centre', 'Centro'
        ]

        # 二级单位关键词
        secondary_keywords = [
            'Department', 'Dipartimento', 'Dept',
            'Division', 'Divisione', 'Div',
            'Unit', 'Unità',
            'Laboratory', 'Laboratorio', 'Lab',
            'Service', 'Servizio',
            'Section', 'Sezione'
        ]

        # 分类各部分
        primary_parts = []
        secondary_parts = []
        geo_parts = []

        # 假设最后1-2个部分是地理信息（城市、国家）
        # 一般格式：..., City, Country 或 ..., City
        if len(parts) >= 2:
            # 最后一个通常是国家
            last_part = parts[-1]
            # 倒数第二个通常是城市
            second_last = parts[-2] if len(parts) >= 2 else None

            # 检查是否是常见国家名或城市名（简单启发式：单个词且不含机构关键词）
            is_last_geo = not any(kw.lower() in last_part.lower() for kw in primary_keywords + secondary_keywords)
            is_second_last_geo = second_last and not any(kw.lower() in second_last.lower() for kw in primary_keywords + secondary_keywords)

            if is_last_geo:
                geo_parts.append(last_part)
                parts = parts[:-1]

                if is_second_last_geo and len(parts) >= 1:
                    geo_parts.insert(0, parts[-1])
                    parts = parts[:-1]

        # 对剩余部分分类
        for part in parts:
            part_lower = part.lower()

            # 检查是否包含一级机构关键词
            is_primary = any(kw.lower() in part_lower for kw in primary_keywords)
            # 检查是否包含二级单位关键词
            is_secondary = any(kw.lower() in part_lower for kw in secondary_keywords)

            if is_primary and not is_secondary:
                primary_parts.append(part)
            elif is_secondary:
                secondary_parts.append(part)
            else:
                # 如果不确定，放入一级机构（保守策略）
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
        """
        # 常见缩写规则
        abbrev_map = {
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
            'Clinici': 'Clin',
            'Scientifici': 'Sci',
            'National': 'Natl',
            'International': 'Int',
            'Advanced': 'Adv',
            'Pathology': 'Pathol',
            'Biology': 'Biol',
            'Chemistry': 'Chem',
            'Physics': 'Phys',
            'Engineering': 'Engn',
            'degli Studi di': '',  # 意大利语"大学"
            'and': '&',
        }

        result = institution
        for full, abbrev in abbrev_map.items():
            result = re.sub(r'\b' + re.escape(full) + r'\b', abbrev, result, flags=re.IGNORECASE)

        # 移除常见介词和冠词（WOS风格）
        prepositions = ['of', 'for', 'the', 'and', 'in', 'at', 'on']
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
        2. 提取包含这些关键词的机构名称
        3. 去除部门名称（Department, Division, School of XX等）
        4. 去重并标准化
        """
        if not affil_str:
            return []

        # 一级机构的关键词（这些通常是顶层机构）
        primary_keywords = [
            'University', 'Università', 'Universität', 'Universi',  # 大学
            'Hospital', 'Ospedale', 'Clinic', 'Medical Center',     # 医院
            'Institute', 'Istituto', 'Institut',                    # 研究所
            'College', 'School of Medicine', 'School of Public',    # 学院
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

                # 检查是否包含一级机构关键词
                is_primary = False
                for prim_keyword in primary_keywords:
                    if prim_keyword.lower() in part.lower():
                        is_primary = True
                        break

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
        """执行转换"""
        print("开始转换 Scopus CSV → WOS 纯文本格式...")
        print("-" * 60)

        # 读取Scopus CSV
        self.records = self.read_scopus_csv()

        # 转换每条记录
        wos_content = []

        # WOS文件头（无空行分隔）
        wos_content.append("FN Scopus Export (Converted to WOS Format)")
        wos_content.append("VR 1.0")

        # 转换每条记录
        for i, record in enumerate(self.records, 1):
            print(f"转换记录 {i}/{len(self.records)}: {record.get('Title', 'N/A')[:50]}...")
            wos_record = self.convert_record(record)
            # 在记录前添加空行（除了第一条记录）
            if i > 1:
                wos_content.append("")  # 空行
            wos_content.append(wos_record)

        # WOS文件尾（前面加空行）
        wos_content.append("")  # 空行
        wos_content.append("EF")

        # 写入文件（用单个换行符连接，包含UTF-8 BOM，与WOS格式完全一致）
        with open(self.output_file, 'w', encoding='utf-8-sig') as f:
            f.write('\n'.join(wos_content))

        print("-" * 60)
        print(f"✓ 转换完成！")
        print(f"✓ 输出文件: {self.output_file}")
        print(f"✓ 共转换 {len(self.records)} 条记录")


def main():
    """主函数"""
    import sys

    # 默认路径（当前目录）
    input_file = "scopus.csv"
    output_file = "scopus_converted_to_wos.txt"

    # 命令行参数
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]

    print("=" * 60)
    print("Scopus to WOS Converter")
    print("=" * 60)
    print(f"输入文件: {input_file}")
    print(f"输出文件: {output_file}")
    print()

    # 执行转换
    converter = ScopusToWosConverter(input_file, output_file)
    converter.convert()

    print()
    print("=" * 60)
    print("转换完成！现在可以将输出文件导入文献计量学分析工具。")
    print("=" * 60)


if __name__ == "__main__":
    main()
