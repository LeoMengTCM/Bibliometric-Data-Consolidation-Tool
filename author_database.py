#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
作者数据库管理系统

从WOS原始文件中提取作者信息，建立标准化的作者数据库。
用于Scopus转换时的作者名称标准化。

数据库结构:
{
    "authors": {
        "Smith, J": {
            "full_name": "Smith, John",
            "abbreviated": "Smith, J",
            "institutions": [
                "Harvard University",
                "MIT"
            ],
            "first_seen": "2020-01-01",
            "last_seen": "2023-12-31",
            "article_count": 15,
            "source": "wos"
        }
    },
    "metadata": {
        "total_authors": 1234,
        "last_updated": "2025-11-12",
        "source_file": "wos.txt"
    }
}
"""

import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class AuthorDatabase:
    """作者数据库管理类"""

    def __init__(self, db_path: str = "config/author_database.json"):
        """
        初始化作者数据库

        Args:
            db_path: 数据库文件路径
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.authors = {}
        self.metadata = {
            'total_authors': 0,
            'last_updated': '',
            'source_file': ''
        }
        self.load_database()

    def load_database(self) -> bool:
        """加载数据库"""
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.authors = data.get('authors', {})
                    self.metadata = data.get('metadata', self.metadata)
                logger.info(f"✓ 加载作者数据库: {len(self.authors)} 位作者")
                return True
            except Exception as e:
                logger.warning(f"加载数据库失败: {e}，将创建新数据库")
                return False
        else:
            logger.info("数据库文件不存在，将创建新数据库")
            return False

    def save_database(self) -> bool:
        """保存数据库"""
        try:
            # 更新元数据
            self.metadata['total_authors'] = len(self.authors)
            self.metadata['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # 保存到文件
            data = {
                'authors': self.authors,
                'metadata': self.metadata
            }

            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info(f"✓ 保存作者数据库: {len(self.authors)} 位作者")
            return True

        except Exception as e:
            logger.error(f"✗ 保存数据库失败: {e}")
            return False

    def parse_wos_file(self, wos_file: str) -> bool:
        """
        从WOS文件中提取作者信息

        Args:
            wos_file: WOS文件路径

        Returns:
            是否成功
        """
        logger.info(f"开始解析WOS文件: {wos_file}")

        try:
            with open(wos_file, 'r', encoding='utf-8-sig') as f:
                content = f.read()

            # 按记录分割
            records = content.split('\n\nPT ')
            logger.info(f"找到 {len(records)} 条记录")

            for i, record in enumerate(records):
                if i == 0:
                    record = record.replace('PT ', '')
                else:
                    record = 'PT ' + record

                # 提取作者信息
                self._extract_authors_from_record(record)

            self.metadata['source_file'] = wos_file
            logger.info(f"✓ 解析完成，共提取 {len(self.authors)} 位作者")
            return True

        except Exception as e:
            logger.error(f"✗ 解析WOS文件失败: {e}")
            return False

    def _extract_authors_from_record(self, record: str) -> None:
        """从单条记录中提取作者信息"""

        # 提取AU字段（作者缩写）
        au_match = re.search(r'^AU (.+?)(?=\n[A-Z]{2} |\n\n|$)', record, re.MULTILINE | re.DOTALL)
        au_authors = []
        if au_match:
            au_text = au_match.group(1)
            # 处理多行
            au_text = re.sub(r'\n   ', ' ', au_text)
            au_authors = [a.strip() for a in au_text.split('\n') if a.strip()]

        # 提取AF字段（作者全名）
        af_match = re.search(r'^AF (.+?)(?=\n[A-Z]{2} |\n\n|$)', record, re.MULTILINE | re.DOTALL)
        af_authors = []
        if af_match:
            af_text = af_match.group(1)
            # 处理多行
            af_text = re.sub(r'\n   ', ' ', af_text)
            af_authors = [a.strip() for a in af_text.split('\n') if a.strip()]

        # 提取C1字段（机构地址）
        c1_match = re.search(r'^C1 (.+?)(?=\n[A-Z]{2} |\n\n|$)', record, re.MULTILINE | re.DOTALL)
        author_institutions = defaultdict(set)
        if c1_match:
            c1_text = c1_match.group(1)
            # 处理多行
            c1_text = re.sub(r'\n   ', ' ', c1_text)
            c1_lines = c1_text.split('\n')

            for line in c1_lines:
                # 提取作者名和机构
                # 格式: [Author1, A; Author2, B] Institution, City, Country.
                author_match = re.match(r'\[([^\]]+)\]\s*(.+)', line)
                if author_match:
                    authors_str = author_match.group(1)
                    institution_str = author_match.group(2)

                    # 提取机构名（第一个逗号之前）
                    institution = institution_str.split(',')[0].strip()

                    # 分割作者
                    authors_in_line = [a.strip() for a in authors_str.split(';')]
                    for author in authors_in_line:
                        author_institutions[author].add(institution)

        # 提取PY字段（年份）
        py_match = re.search(r'^PY (\d{4})', record, re.MULTILINE)
        year = py_match.group(1) if py_match else ''

        # 合并AU和AF信息
        for i, au_author in enumerate(au_authors):
            af_author = af_authors[i] if i < len(af_authors) else au_author

            # 添加或更新作者信息
            if au_author not in self.authors:
                self.authors[au_author] = {
                    'full_name': af_author,
                    'abbreviated': au_author,
                    'institutions': [],
                    'first_seen': year,
                    'last_seen': year,
                    'article_count': 1,
                    'source': 'wos'
                }
            else:
                # 更新现有作者
                author_data = self.authors[au_author]
                author_data['article_count'] += 1

                # 更新全名（如果新的更完整）
                if len(af_author) > len(author_data['full_name']):
                    author_data['full_name'] = af_author

                # 更新年份范围
                if year:
                    if not author_data['first_seen'] or year < author_data['first_seen']:
                        author_data['first_seen'] = year
                    if not author_data['last_seen'] or year > author_data['last_seen']:
                        author_data['last_seen'] = year

            # 添加机构信息
            if au_author in author_institutions:
                current_institutions = set(self.authors[au_author]['institutions'])
                current_institutions.update(author_institutions[au_author])
                self.authors[au_author]['institutions'] = sorted(list(current_institutions))

    def lookup_author(self, abbreviated_name: str) -> Optional[Dict]:
        """
        查找作者信息

        Args:
            abbreviated_name: 作者缩写名（如 "Smith, J"）

        Returns:
            作者信息字典，如果未找到返回None
        """
        return self.authors.get(abbreviated_name)

    def get_full_name(self, abbreviated_name: str) -> str:
        """
        获取作者全名

        Args:
            abbreviated_name: 作者缩写名

        Returns:
            作者全名，如果未找到返回原始缩写名
        """
        author = self.lookup_author(abbreviated_name)
        if author:
            return author['full_name']
        return abbreviated_name

    def get_institutions(self, abbreviated_name: str) -> List[str]:
        """
        获取作者的机构列表

        Args:
            abbreviated_name: 作者缩写名

        Returns:
            机构列表
        """
        author = self.lookup_author(abbreviated_name)
        if author:
            return author['institutions']
        return []

    def search_by_lastname(self, lastname: str) -> List[Dict]:
        """
        按姓氏搜索作者

        Args:
            lastname: 姓氏

        Returns:
            匹配的作者列表
        """
        results = []
        for abbr_name, author_data in self.authors.items():
            if abbr_name.startswith(lastname + ','):
                results.append({
                    'abbreviated': abbr_name,
                    **author_data
                })
        return results

    def get_statistics(self) -> Dict:
        """获取数据库统计信息"""
        total_institutions = set()
        total_articles = 0
        year_range = {'min': '9999', 'max': '0000'}

        for author_data in self.authors.values():
            total_institutions.update(author_data['institutions'])
            total_articles += author_data['article_count']

            if author_data['first_seen'] and author_data['first_seen'] < year_range['min']:
                year_range['min'] = author_data['first_seen']
            if author_data['last_seen'] and author_data['last_seen'] > year_range['max']:
                year_range['max'] = author_data['last_seen']

        return {
            'total_authors': len(self.authors),
            'total_institutions': len(total_institutions),
            'total_articles': total_articles,
            'year_range': f"{year_range['min']}-{year_range['max']}",
            'last_updated': self.metadata['last_updated'],
            'source_file': self.metadata['source_file']
        }

    def print_statistics(self) -> None:
        """打印数据库统计信息"""
        stats = self.get_statistics()

        print("\n" + "=" * 80)
        print("作者数据库统计信息")
        print("=" * 80)
        print(f"总作者数: {stats['total_authors']}")
        print(f"总机构数: {stats['total_institutions']}")
        print(f"总文章数: {stats['total_articles']}")
        print(f"年份范围: {stats['year_range']}")
        print(f"数据来源: {stats['source_file']}")
        print(f"最后更新: {stats['last_updated']}")
        print("=" * 80)


def build_author_database_from_wos(wos_file: str, output_db: str = "config/author_database.json") -> bool:
    """
    从WOS文件构建作者数据库

    Args:
        wos_file: WOS文件路径
        output_db: 输出数据库路径

    Returns:
        是否成功
    """
    logger.info("=" * 80)
    logger.info("构建作者数据库")
    logger.info("=" * 80)

    # 创建数据库
    db = AuthorDatabase(output_db)

    # 解析WOS文件
    if not db.parse_wos_file(wos_file):
        return False

    # 保存数据库
    if not db.save_database():
        return False

    # 打印统计信息
    db.print_statistics()

    return True


def build_author_database_from_folder(folder_path: str, pattern: str = "savedrecs*.txt",
                                      output_db: str = "config/author_database.json") -> bool:
    """
    从文件夹中的多个WOS文件构建作者数据库

    Args:
        folder_path: 包含WOS文件的文件夹路径
        pattern: 文件名匹配模式（默认: savedrecs*.txt）
        output_db: 输出数据库路径

    Returns:
        是否成功
    """
    import glob

    logger.info("=" * 80)
    logger.info("从文件夹构建作者数据库")
    logger.info("=" * 80)
    logger.info(f"文件夹: {folder_path}")
    logger.info(f"匹配模式: {pattern}")
    logger.info("")

    # 查找所有匹配的WOS文件
    search_pattern = str(Path(folder_path) / pattern)
    wos_files = sorted(glob.glob(search_pattern))

    if not wos_files:
        logger.error(f"✗ 未找到匹配的WOS文件: {search_pattern}")
        return False

    logger.info(f"找到 {len(wos_files)} 个WOS文件:")
    for i, file in enumerate(wos_files, 1):
        logger.info(f"  {i}. {Path(file).name}")
    logger.info("")

    # 创建数据库
    db = AuthorDatabase(output_db)

    # 逐个解析WOS文件
    total_records = 0
    for i, wos_file in enumerate(wos_files, 1):
        logger.info(f"处理文件 {i}/{len(wos_files)}: {Path(wos_file).name}")

        # 记录处理前的作者数
        authors_before = len(db.authors)

        # 解析文件
        if not db.parse_wos_file(wos_file):
            logger.warning(f"⚠️  文件解析失败，跳过: {wos_file}")
            continue

        # 统计新增作者数
        authors_after = len(db.authors)
        new_authors = authors_after - authors_before
        logger.info(f"  ✓ 新增作者: {new_authors} 位（总计: {authors_after} 位）")
        logger.info("")

    # 保存数据库
    if not db.save_database():
        return False

    # 打印最终统计信息
    logger.info("=" * 80)
    logger.info("数据库构建完成")
    logger.info("=" * 80)
    db.print_statistics()

    return True


if __name__ == '__main__':
    import sys
    import argparse

    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # 命令行参数
    parser = argparse.ArgumentParser(description='作者数据库管理工具')
    parser.add_argument('--build', type=str, help='从WOS文件构建数据库')
    parser.add_argument('--build-from-folder', type=str, help='从文件夹中的多个WOS文件构建数据库')
    parser.add_argument('--pattern', type=str, default='savedrecs*.txt',
                        help='文件名匹配模式（默认: savedrecs*.txt）')
    parser.add_argument('--output', type=str, default='config/author_database.json',
                        help='输出数据库路径')
    parser.add_argument('--lookup', type=str, help='查找作者信息')
    parser.add_argument('--search', type=str, help='按姓氏搜索作者')
    parser.add_argument('--stats', action='store_true', help='显示统计信息')

    args = parser.parse_args()

    if args.build:
        # 从单个文件构建数据库
        success = build_author_database_from_wos(args.build, args.output)
        sys.exit(0 if success else 1)

    elif args.build_from_folder:
        # 从文件夹构建数据库
        success = build_author_database_from_folder(args.build_from_folder, args.pattern, args.output)
        sys.exit(0 if success else 1)

    elif args.lookup:
        # 查找作者
        db = AuthorDatabase(args.output)
        author = db.lookup_author(args.lookup)
        if author:
            print(f"\n作者信息:")
            print(f"  缩写名: {args.lookup}")
            print(f"  全名: {author['full_name']}")
            print(f"  机构: {', '.join(author['institutions'])}")
            print(f"  文章数: {author['article_count']}")
            print(f"  年份范围: {author['first_seen']}-{author['last_seen']}")
        else:
            print(f"未找到作者: {args.lookup}")

    elif args.search:
        # 搜索作者
        db = AuthorDatabase(args.output)
        results = db.search_by_lastname(args.search)
        if results:
            print(f"\n找到 {len(results)} 位姓氏为 '{args.search}' 的作者:")
            for author in results[:10]:  # 只显示前10个
                print(f"  {author['abbreviated']} → {author['full_name']} ({author['article_count']} 篇)")
        else:
            print(f"未找到姓氏为 '{args.search}' 的作者")

    elif args.stats:
        # 显示统计信息
        db = AuthorDatabase(args.output)
        db.print_statistics()

    else:
        parser.print_help()
