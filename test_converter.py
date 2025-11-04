#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单元测试
测试scopus_to_wos_converter.py的核心功能

运行测试:
    python3 -m unittest test_converter.py

或运行单个测试:
    python3 -m unittest test_converter.TestInstitutionRecognition.test_independent_college
"""

import unittest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scopus_to_wos_converter import ScopusToWosConverter


class TestAuthorConversion(unittest.TestCase):
    """测试作者姓名转换"""

    def setUp(self):
        # 使用临时文件初始化
        self.converter = ScopusToWosConverter.__new__(ScopusToWosConverter)
        self.converter.institution_config = {
            'independent_colleges': [],
            'independent_schools': [],
            'abbreviations': {}
        }

    def test_convert_authors_basic(self):
        """测试基本作者转换"""
        authors_str = "Smith, J.; Doe, M.V."
        result = self.converter.convert_authors(authors_str)
        self.assertEqual(result, ["Smith, J", "Doe, MV"])

    def test_convert_authors_dots(self):
        """测试带点号的缩写"""
        authors_str = "Wang, L.H.; Zhang, M. V."
        result = self.converter.convert_authors(authors_str)
        self.assertEqual(result, ["Wang, LH", "Zhang, MV"])

    def test_convert_authors_empty(self):
        """测试空输入"""
        result = self.converter.convert_authors("")
        self.assertEqual(result, [])


class TestInstitutionRecognition(unittest.TestCase):
    """测试机构识别"""

    def setUp(self):
        self.converter = ScopusToWosConverter.__new__(ScopusToWosConverter)
        self.converter.institution_config = {
            'independent_colleges': ['Imperial College London', 'King\'s College London'],
            'independent_schools': ['Harvard Medical School'],
            'abbreviations': {}
        }

    def test_independent_college(self):
        """测试独立College识别"""
        result = self.converter._is_independent_college_or_school(
            "Imperial College London",
            ["Imperial College London", "London", "UK"]
        )
        self.assertTrue(result)

    def test_college_with_university(self):
        """测试有University时College为二级机构"""
        result = self.converter._is_independent_college_or_school(
            "College of Pharmacy",
            ["University of California", "College of Pharmacy", "San Francisco"]
        )
        self.assertFalse(result)

    def test_school_of_medicine(self):
        """测试School of Medicine为独立机构"""
        result = self.converter._is_independent_college_or_school(
            "Johns Hopkins School of Medicine",
            ["Johns Hopkins School of Medicine", "Baltimore"]
        )
        self.assertTrue(result)

    def test_college_of_format(self):
        """测试College of XX格式（通常是二级）"""
        result = self.converter._is_independent_college_or_school(
            "College of Arts and Sciences",
            ["College of Arts and Sciences"]
        )
        self.assertFalse(result)


class TestReferenceConversion(unittest.TestCase):
    """测试参考文献转换"""

    def setUp(self):
        self.converter = ScopusToWosConverter.__new__(ScopusToWosConverter)
        self.converter.journal_abbrev = {
            "Nature": "NATURE",
            "Science": "SCIENCE"
        }
        self.converter.JOURNAL_ABBREV = self.converter.journal_abbrev

    def test_parse_reference_basic(self):
        """测试基本参考文献解析"""
        ref = "Smith, John, Article Title, Nature, 10, 5, pp. 123-130, (2020)"
        result = self.converter.parse_reference(ref)

        self.assertEqual(result['author'], 'Smith')
        self.assertEqual(result['year'], '2020')
        self.assertEqual(result['journal'], 'Nature')
        self.assertEqual(result['volume'], '10')
        self.assertEqual(result['page'], '123')


class TestJournalAbbreviation(unittest.TestCase):
    """测试期刊缩写"""

    def setUp(self):
        self.converter = ScopusToWosConverter.__new__(ScopusToWosConverter)
        self.converter.journal_abbrev = {
            "Nature": "NATURE",
            "American Journal of Medicine": "AM J MED"
        }
        self.converter.JOURNAL_ABBREV = self.converter.journal_abbrev

    def test_known_journal(self):
        """测试已知期刊"""
        result = self.converter.abbreviate_journal("Nature")
        self.assertEqual(result, "NATURE")

    def test_unknown_journal(self):
        """测试未知期刊（应生成缩写）"""
        result = self.converter.abbreviate_journal("Journal of Interesting Research")
        # 应该生成某种缩写
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)


def run_tests():
    """运行所有测试"""
    unittest.main(verbosity=2)


if __name__ == '__main__':
    run_tests()
