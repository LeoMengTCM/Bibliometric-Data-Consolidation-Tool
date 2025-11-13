#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档类型分析和可视化

自动从WOS文件中提取文档类型统计并生成可视化图表
"""

import pandas as pd
import matplotlib.pyplot as plt
import re
from pathlib import Path
from typing import Dict, Tuple


class DocumentTypeAnalyzer:
    def __init__(self):
        """初始化分析器"""
        self._setup_plot_style()
        self._setup_color_palette()

    def _setup_plot_style(self):
        """设置图表样式"""
        try:
            plt.rcParams['font.family'] = 'Arial'
        except:
            pass
        plt.rcParams['axes.labelsize'] = 14
        plt.rcParams['xtick.labelsize'] = 12
        plt.rcParams['ytick.labelsize'] = 12
        plt.rcParams['legend.fontsize'] = 12
        plt.rcParams['figure.titlesize'] = 22
        plt.rcParams['axes.titlesize'] = 18
        plt.rcParams['axes.titleweight'] = 'bold'
        plt.rcParams['axes.labelweight'] = 'bold'
        plt.style.use('seaborn-v0_8-whitegrid')

    def _setup_color_palette(self):
        """设置颜色"""
        self.palette = {
            'Article': '#1f77b4',
            'Review': '#ff7f0e',
        }

    def parse_wos_file(self, file_path: str) -> Dict[str, int]:
        """解析WOS文件，统计文档类型"""
        counts = {'Article': 0, 'Review': 0}

        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()

        records = content.split('\n\nPT ')[1:]  # 跳过文件头

        for record in records:
            if record.strip():
                match = re.search(r'^J\s*$', record, re.MULTILINE)
                if match:
                    # 查找DT字段
                    dt_match = re.search(r'^DT\s+(.+?)$', record, re.MULTILINE)
                    if dt_match:
                        doc_type = dt_match.group(1).strip()
                        if 'Article' in doc_type:
                            counts['Article'] += 1
                        elif 'Review' in doc_type:
                            counts['Review'] += 1

        return counts

    def create_data_from_files(self, wos_file: str, scopus_file: str, final_file: str) -> pd.DataFrame:
        """从三个文件中提取数据"""
        wos_counts = self.parse_wos_file(wos_file)
        scopus_counts = self.parse_wos_file(scopus_file)
        final_counts = self.parse_wos_file(final_file)

        data = pd.DataFrame({
            'Article_Type': ['Article', 'Review'],
            'WoS_Count': [wos_counts['Article'], wos_counts['Review']],
            'Scopus_Count': [scopus_counts['Article'], scopus_counts['Review']],
            'Final_Count': [final_counts['Article'], final_counts['Review']]
        })

        return data

    def plot_distribution(self, data: pd.DataFrame, output_dir: str):
        """绘制文档类型分布图"""
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(22, 8))

        donut_width = 0.4
        wedge_props = {'width': donut_width, 'edgecolor': 'white', 'linewidth': 2}
        text_props = {'fontsize': 16, 'fontweight': 'bold'}

        # Web of Science
        data1 = data[['Article_Type', 'WoS_Count']].rename(columns={'WoS_Count': 'Count'})
        total1 = data1['Count'].sum()
        colors1 = [self.palette[cat] for cat in data1['Article_Type']]
        labels1 = [f"{row['Article_Type']}\n(n={row['Count']})" for _, row in data1.iterrows()]

        ax1.pie(data1['Count'], labels=labels1, colors=colors1, autopct='%1.1f%%',
                startangle=90, wedgeprops=wedge_props, textprops=text_props, pctdistance=0.8)
        ax1.text(0, 0, f'n={total1}', ha='center', va='center', fontsize=30, fontweight='bold')
        ax1.set_title('Web of Science', pad=20)

        # Scopus
        data2 = data[['Article_Type', 'Scopus_Count']].rename(columns={'Scopus_Count': 'Count'})
        total2 = data2['Count'].sum()
        colors2 = [self.palette[cat] for cat in data2['Article_Type']]
        labels2 = [f"{row['Article_Type']}\n(n={row['Count']})" for _, row in data2.iterrows()]

        ax2.pie(data2['Count'], labels=labels2, colors=colors2, autopct='%1.1f%%',
                startangle=90, wedgeprops=wedge_props, textprops=text_props, pctdistance=0.8)
        ax2.text(0, 0, f'n={total2}', ha='center', va='center', fontsize=30, fontweight='bold')
        ax2.set_title('Scopus', pad=20)

        # Final Dataset
        data3 = data[['Article_Type', 'Final_Count']].rename(columns={'Final_Count': 'Count'})
        total3 = data3['Count'].sum()
        colors3 = [self.palette[cat] for cat in data3['Article_Type']]
        labels3 = [f"{row['Article_Type']}\n(n={row['Count']})" for _, row in data3.iterrows()]

        ax3.pie(data3['Count'], labels=labels3, colors=colors3, autopct='%1.1f%%',
                startangle=90, wedgeprops=wedge_props, textprops=text_props, pctdistance=0.8)
        ax3.text(0, 0, f'n={total3}', ha='center', va='center', fontsize=30, fontweight='bold')
        ax3.set_title('Final Dataset', pad=20)

        # 设置百分比标签颜色为白色
        for ax in [ax1, ax2, ax3]:
            for text in ax.texts:
                if text.get_text().endswith('%'):
                    text.set_color('white')
                    text.set_fontsize(16)
                    text.set_fontweight('bold')

        fig.suptitle('Distribution of Articles and Reviews Across Databases', y=1.02, fontweight='bold')
        fig.tight_layout(rect=[0, 0, 1, 0.95])

        # 保存图片
        output_path = Path(output_dir)
        for fmt in ['tiff', 'png']:
            fig.savefig(output_path / f'document_types.{fmt}', dpi=300, bbox_inches='tight',
                       format=fmt, facecolor='white', edgecolor='none')

        plt.close(fig)
        print(f"✓ 图表已保存: {output_path}/document_types.tiff 和 .png")


def generate_document_type_analysis(data_dir: str):
    """生成文档类型分析"""
    data_dir = Path(data_dir)
    output_dir = data_dir / 'Figures and Tables' / '01 文档类型'

    # 文件路径
    wos_file = data_dir / 'wos.txt'
    scopus_file = data_dir / 'scopus_enriched.txt'
    final_file = data_dir / 'Final_Version.txt'

    # 检查文件
    if not all([wos_file.exists(), scopus_file.exists(), final_file.exists()]):
        print("✗ 缺少必要文件")
        return False

    # 分析
    analyzer = DocumentTypeAnalyzer()
    data = analyzer.create_data_from_files(str(wos_file), str(scopus_file), str(final_file))

    # 保存数据
    data.to_csv(output_dir / 'document_types_data.csv', index=False)
    print(f"✓ 数据已保存: {output_dir}/document_types_data.csv")

    # 生成图表
    analyzer.plot_distribution(data, str(output_dir))

    # 保存代码副本
    import shutil
    shutil.copy(__file__, output_dir / 'plot_document_types.py')
    print(f"✓ 代码已保存: {output_dir}/plot_document_types.py")

    return True


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        generate_document_type_analysis(sys.argv[1])
    else:
        print("Usage: python3 plot_document_types.py <data_dir>")
