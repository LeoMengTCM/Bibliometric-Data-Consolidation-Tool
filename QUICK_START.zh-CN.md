# 快速开始

[English](QUICK_START.md) | 中文 | [日本語](QUICK_START.ja.md)

## 项目定位

请把这个仓库当成一个**以 WOS 为标准的 Scopus→WOS 转换与整合系统**，而不是普通清洗脚本集合。

## 推荐第一次运行

仓库自带可复现实例：

```text
Example/
├── wos.txt
└── scopus.csv
```

如果你想先看本地规则和 WOS 对齐逻辑，建议运行：

```bash
python3 run_ai_workflow.py --data-dir Example --no-ai
```

如果直接跑默认完整流程：

```bash
python3 run_ai_workflow.py --data-dir Example
```

## 输入文件要求

你自己的数据目录必须包含：

```text
/path/to/your-data/
├── wos.txt
└── scopus.csv
```

## 默认工作流会做什么

1. 把 Scopus CSV 转成 WOS 风格纯文本
2. 使用当前 WOS 语料校准转换和 `C3` 对齐
3. 对 WOS 与 Scopus 进行合并去重
4. 进行语言筛选
5. 进行机构清洗
6. 输出统计分析与图表

## 常用命令

基础运行：

```bash
python3 run_ai_workflow.py --data-dir "/path/to/data"
```

只关闭 AI 分支：

```bash
python3 run_ai_workflow.py --data-dir "/path/to/data" --no-ai
```

禁用机构清洗：

```bash
python3 run_ai_workflow.py --data-dir "/path/to/data" --no-cleaning
```

指定年份范围：

```bash
python3 run_ai_workflow.py --data-dir "/path/to/data" --year-range 2015-2024
```

筛选中文文献：

```bash
python3 run_ai_workflow.py --data-dir "/path/to/data" --language Chinese
```

查看帮助：

```bash
python3 run_ai_workflow.py --help
```

## 关于 `--no-ai`

`--no-ai` **不会**关闭本地的 WOS 对齐转换逻辑。

它仍然保留：

- 本地 Scopus → WOS 风格转换
- 本地 WOS 语料校准
- 本地基于重复对的 `C3` 恢复
- 合并 / 去重 / 筛选 / 清洗 / 分析

它只会跳过：

- AI WOS 风格标准化
- AI 机构补全

## 主要输出文件

- `scopus_converted_to_wos.txt`
- `scopus_enriched.txt`
- `merged_deduplicated.txt`
- `english_only.txt` 或其他语言筛选结果
- `Final_Version.txt`
- `*_analysis_report.txt`
- `ai_workflow_report.txt`
- `Figures and Tables/`

## 当前验证快照

基于仓库自带示例，本地 round11 复核已把 100 组重复文献中的 `C3` 差异从 `24` 降到 `12`。

## GUI 启动

```bash
python3 gui_app.py
```

或双击项目根目录下的 `启动GUI.command`。

## 下一步阅读

- `README.zh-CN.md`
- `PROJECT_STRUCTURE.md`
- `docs/README.md`
- `docs/WOS标准化说明.md`
