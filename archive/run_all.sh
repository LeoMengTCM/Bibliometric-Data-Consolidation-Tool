#!/bin/bash
# 完整的 WOS + Scopus 数据处理流程
# 从原始文件 wos.txt 和 scopus.csv 开始

echo "============================================================"
echo "WOS + Scopus 完整数据处理流程"
echo "============================================================"
echo ""

# 获取脚本所在目录并切换到该目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 步骤1：转换 Scopus CSV 到 WOS 格式
echo "步骤 1/2: 转换 Scopus CSV 到 WOS 格式..."
echo "------------------------------------------------------------"
python3 scopus_to_wos_converter.py

if [ $? -ne 0 ]; then
    echo "❌ Scopus转换失败，流程终止"
    exit 1
fi

echo ""
echo "✓ Scopus 转换完成"
echo ""

# 步骤2：合并 WOS 和 Scopus 并去重
echo "步骤 2/2: 合并 WOS 和 Scopus 数据并去重..."
echo "------------------------------------------------------------"
python3 merge_deduplicate.py

if [ $? -ne 0 ]; then
    echo "❌ 合并去重失败，流程终止"
    exit 1
fi

echo ""
echo "============================================================"
echo "✓ 完整流程执行成功！"
echo "============================================================"
echo ""
echo "生成的文件："
echo "  1. scopus_converted_to_wos.txt    - Scopus转换后的WOS格式"
echo "  2. merged_deduplicated.txt        - 合并去重后的最终文件"
echo "  3. merged_deduplicated_report.txt - 详细去重报告"
echo ""
echo "现在可以使用 merged_deduplicated.txt 进行文献计量分析！"
echo "============================================================"
