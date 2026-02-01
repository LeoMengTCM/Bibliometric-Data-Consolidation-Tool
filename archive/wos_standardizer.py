import os
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WOS格式标准化器（AI增强版）

以WOS格式为绝对标准，通过AI学习和数据库记忆实现：
1. 作者名标准化（去重音符号）
2. 国家名称WOS标准化
3. 期刊名WOS标准缩写
4. 机构名称WOS标准化

作者：Meng Linghan
开发工具：Claude Code
日期：2025-11-11
版本：v1.0
"""

import re
import json
import time
import logging
import requests
from typing import Dict, List, Optional
from pathlib import Path
from gemini_config import GeminiConfig

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class WOSStandardDatabase:
    """WOS标准格式数据库"""

    def __init__(self, db_path: str = 'config/wos_standard_cache.json'):
        self.db_path = Path(db_path)
        self.db = self._load_database()

    def _load_database(self) -> Dict:
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    db = json.load(f)
                    logger.info(f"✓ 加载WOS标准数据库: {len(db.get('authors', {}))} 作者, {len(db.get('countries', {}))} 国家, {len(db.get('journals', {}))} 期刊")
                    return db
            except Exception as e:
                logger.warning(f"加载数据库失败: {e}")

        return {
            'metadata': {
                'version': '1.0',
                'created': time.strftime('%Y-%m-%d %H:%M:%S'),
                'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
            },
            'authors': {},      # 作者名标准化
            'countries': {},    # 国家名WOS标准
            'journals': {},     # 期刊名WOS缩写
            'institutions': {}  # 机构名WOS标准
        }

    def save_database(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db['metadata']['last_updated'] = time.strftime('%Y-%m-%d %H:%M:%S')

        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.db, f, ensure_ascii=False, indent=2)

        logger.info(f"✓ WOS标准数据库已保存")

    def get_author(self, author_name: str) -> Optional[str]:
        """获取作者WOS标准名称"""
        key = self._normalize_key(author_name)
        return self.db['authors'].get(key)

    def add_author(self, original: str, wos_standard: str):
        """添加作者标准化映射"""
        key = self._normalize_key(original)
        self.db['authors'][key] = wos_standard

    def get_country(self, country_name: str) -> Optional[str]:
        """获取国家WOS标准名称"""
        key = self._normalize_key(country_name)
        return self.db['countries'].get(key)

    def add_country(self, original: str, wos_standard: str):
        """添加国家标准化映射"""
        key = self._normalize_key(original)
        self.db['countries'][key] = wos_standard

    def get_journal(self, journal_name: str) -> Optional[str]:
        """获取期刊WOS标准缩写"""
        key = self._normalize_key(journal_name)
        return self.db['journals'].get(key)

    def add_journal(self, original: str, wos_abbrev: str):
        """添加期刊缩写映射"""
        key = self._normalize_key(original)
        self.db['journals'][key] = wos_abbrev

    def _normalize_key(self, text: str) -> str:
        """标准化键（小写，去除标点）"""
        key = text.lower().strip()
        key = re.sub(r'[^\w\s-]', '', key)
        key = ' '.join(key.split())
        return key


class WOSStandardizer:
    """WOS格式标准化器（AI驱动）"""

    def __init__(self, config: GeminiConfig, db_path: str = 'config/wos_standard_cache.json'):
        self.config = config
        self.db = WOSStandardDatabase(db_path)
        self.stats = {
            'author_hits': 0,
            'author_misses': 0,
            'country_hits': 0,
            'country_misses': 0,
            'journal_hits': 0,
            'journal_misses': 0
        }

    def standardize_author(self, author_name: str) -> str:
        """标准化作者名（去重音符号，WOS格式）"""
        # 检查数据库
        cached = self.db.get_author(author_name)
        if cached:
            self.stats['author_hits'] += 1
            return cached

        # 调用AI
        self.stats['author_misses'] += 1
        wos_name = self._ai_standardize_author(author_name)

        if wos_name:
            self.db.add_author(author_name, wos_name)
            return wos_name

        return author_name

    def standardize_country(self, country_name: str) -> str:
        """标准化国家名（WOS格式）"""
        # 检查数据库
        cached = self.db.get_country(country_name)
        if cached:
            self.stats['country_hits'] += 1
            return cached

        # 调用AI
        self.stats['country_misses'] += 1
        wos_country = self._ai_standardize_country(country_name)

        if wos_country:
            self.db.add_country(country_name, wos_country)
            return wos_country

        return country_name

    def standardize_journal(self, journal_name: str) -> str:
        """标准化期刊名（WOS缩写）"""
        # 检查数据库
        cached = self.db.get_journal(journal_name)
        if cached:
            self.stats['journal_hits'] += 1
            return cached

        # 调用AI
        self.stats['journal_misses'] += 1
        wos_abbrev = self._ai_standardize_journal(journal_name)

        if wos_abbrev:
            self.db.add_journal(journal_name, wos_abbrev)
            return wos_abbrev

        return journal_name

    def _ai_standardize_author(self, author_name: str) -> Optional[str]:
        """AI标准化作者名"""
        prompt = f"""You are an expert in Web of Science (WOS) author name formatting.

Task: Standardize this author name to WOS format.

Input: {author_name}

WOS Author Name Rules:
1. Remove ALL accent marks and diacritics
   - é → e, ñ → n, ö → o, ü → u, etc.
2. Keep format: Lastname, Initials
3. No spaces between initials
4. Keep hyphens in compound lastnames
5. Capitalize properly

Examples:
- "Pénault-Llorca, Frédérique M." → "Penault-Llorca, FM"
- "Remón, Javier" → "Remon, J"
- "Özgüroĝlu, Mustafa" → "Ozguroglu, M"
- "Abu Akar, Firas" → "Abu Akar, F"

Output ONLY the standardized name, no explanation:"""

        try:
            response = self._call_gemini_api(prompt)
            if response:
                wos_name = response.strip().strip('"\'')
                logger.info(f"✓ AI标准化作者: {author_name} → {wos_name}")
                return wos_name
        except Exception as e:
            logger.error(f"✗ AI标准化作者失败: {e}")

        return None

    def _ai_standardize_country(self, country_name: str) -> Optional[str]:
        """AI标准化国家名"""
        prompt = f"""You are an expert in Web of Science (WOS) country name formatting.

Task: Convert this country name to WOS standard format.

Input: {country_name}

WOS Country Name Standards:
- USA (not United States, not US)
- Peoples R China (for mainland China, not China, not PRC)
- England (not UK, for England specifically)
- Scotland (not UK, for Scotland specifically)
- Wales (not UK, for Wales specifically)
- North Ireland (not UK, for Northern Ireland)
- Turkiye (not Turkey, updated 2022)
- South Korea (not Korea)
- North Korea (not Korea)
- Taiwan (not China Taiwan)
- Hong Kong (not China Hong Kong)

Other countries: Use standard English name
- France, Germany, Italy, Spain, Japan, etc.

Output ONLY the WOS standard country name, no explanation:"""

        try:
            response = self._call_gemini_api(prompt)
            if response:
                wos_country = response.strip().strip('"\'')
                logger.info(f"✓ AI标准化国家: {country_name} → {wos_country}")
                return wos_country
        except Exception as e:
            logger.error(f"✗ AI标准化国家失败: {e}")

        return None

    def _ai_standardize_journal(self, journal_name: str) -> Optional[str]:
        """AI标准化期刊名"""
        prompt = f"""You are an expert in Web of Science (WOS) journal abbreviations.

Task: Convert this journal name to WOS standard abbreviation.

Input: {journal_name}

WOS Journal Abbreviation Rules:
1. Common abbreviations:
   - Journal → J
   - American → AM
   - International → INT
   - Science → SCI
   - Medicine → MED
   - Research → RES
   - Review/Reviews → REV
   - Society → SOC
   - Technology → TECHNOL
   - Clinical → CLIN

2. Keep important words capitalized
3. Remove articles (the, a, an)
4. Use standard WOS format

Examples:
- "Nature" → "NATURE"
- "Journal of Clinical Oncology" → "J CLIN ONCOL"
- "The Lancet Oncology" → "LANCET ONCOL"
- "American Journal of Respiratory and Critical Care Medicine" → "AM J RESP CRIT CARE"

Output ONLY the WOS abbreviation in UPPERCASE, no explanation:"""

        try:
            response = self._call_gemini_api(prompt)
            if response:
                wos_abbrev = response.strip().strip('"\'').upper()
                logger.info(f"✓ AI标准化期刊: {journal_name} → {wos_abbrev}")
                return wos_abbrev
        except Exception as e:
            logger.error(f"✗ AI标准化期刊失败: {e}")

        return None

    def _call_gemini_api(self, prompt: str) -> Optional[str]:
        """调用Gemini API"""
        url = f"{self.config.api_url}/models/{self.config.model}:generateContent"

        headers = {'Content-Type': 'application/json'}
        data = {
            'contents': [{'parts': [{'text': prompt}]}],
            'generationConfig': {
                'temperature': 0.1,
                'maxOutputTokens': 500
            }
        }

        for attempt in range(self.config.max_retries):
            try:
                response = requests.post(
                    url,
                    headers=headers,
                    params={'key': self.config.api_key},
                    json=data,
                    timeout=self.config.timeout
                )

                if response.status_code == 200:
                    result = response.json()
                    if 'candidates' in result and len(result['candidates']) > 0:
                        text = result['candidates'][0]['content']['parts'][0]['text']
                        return text.strip()

                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay)

            except Exception as e:
                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay)

        return None

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        total_author = self.stats['author_hits'] + self.stats['author_misses']
        total_country = self.stats['country_hits'] + self.stats['country_misses']
        total_journal = self.stats['journal_hits'] + self.stats['journal_misses']

        return {
            'authors': {
                'hits': self.stats['author_hits'],
                'misses': self.stats['author_misses'],
                'hit_rate': f"{self.stats['author_hits']/total_author*100:.1f}%" if total_author > 0 else "0%"
            },
            'countries': {
                'hits': self.stats['country_hits'],
                'misses': self.stats['country_misses'],
                'hit_rate': f"{self.stats['country_hits']/total_country*100:.1f}%" if total_country > 0 else "0%"
            },
            'journals': {
                'hits': self.stats['journal_hits'],
                'misses': self.stats['journal_misses'],
                'hit_rate': f"{self.stats['journal_hits']/total_journal*100:.1f}%" if total_journal > 0 else "0%"
            }
        }


def main():
    """测试标准化器"""
    import argparse

    parser = argparse.ArgumentParser(description='WOS格式标准化器测试')
    parser.add_argument('--type', choices=['author', 'country', 'journal'], required=True)
    parser.add_argument('--input', required=True, help='输入文本')

    args = parser.parse_args()

    # 创建配置
    config = GeminiConfig.from_params(
        api_key=os.getenv('GEMINI_API_KEY', 'YOUR_API_KEY'),
        api_url=os.getenv('GEMINI_API_URL', 'https://your-api-gateway.com/proxy/bibliometrics/v1beta'),
        model='gemini-2.5-flash-lite'
    )

    # 创建标准化器
    standardizer = WOSStandardizer(config)

    print("\n" + "=" * 80)
    print("WOS格式标准化器测试")
    print("=" * 80)
    print(f"输入: {args.input}")
    print()

    if args.type == 'author':
        result = standardizer.standardize_author(args.input)
        print(f"WOS标准作者名: {result}")
    elif args.type == 'country':
        result = standardizer.standardize_country(args.input)
        print(f"WOS标准国家名: {result}")
    elif args.type == 'journal':
        result = standardizer.standardize_journal(args.input)
        print(f"WOS标准期刊缩写: {result}")

    # 保存数据库
    standardizer.db.save_database()

    print()
    print("=" * 80)


if __name__ == '__main__':
    main()
