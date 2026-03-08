# 项目结构说明

**当前定位**：以 WOS 为主标准的 Scopus→WOS 转换与整合系统  
**当前文档状态**：post-5.1.0 本地迭代  
**更新日期**：2026-03-07

## 项目概览

本项目的目标不是做“泛化清洗”，而是围绕以下主线持续迭代：

- 尽可能把 Scopus 转成 WOS 风格
- 用当前输入的 `wos.txt` 作为主要参考标准
- 通过重复 WOS/Scopus 记录校准转换规则
- 做好去重与合并
- 输出统一、可直接用于文献计量分析的最终数据库

## 根目录结构

```text
.
├── README.md
├── README.zh-CN.md
├── README.ja.md
├── QUICK_START.md
├── QUICK_START.zh-CN.md
├── QUICK_START.ja.md
├── CHANGELOG.md
├── PROJECT_STRUCTURE.md
├── run_ai_workflow.py
├── gui_app.py
├── 启动GUI.command
├── Example/
├── scripts/
│   └── run_workflow.py
├── src/
│   └── bibliometrics/
├── config/
├── docs/
└── archive/
```

## 核心入口

- `run_ai_workflow.py`：兼容入口，推荐直接复制命令时使用
- `scripts/run_workflow.py`：实际 CLI 入口
- `gui_app.py`：图形界面入口
- `启动GUI.command`：macOS 下的 GUI 快捷入口

## 示例与验证目录

- `Example/`：仓库自带可复现实例，包含 `wos.txt` 与 `scopus.csv`
- `tmp_review_round*/`：本地迭代验证输出目录，用于对照每一轮规则调整后的结果
- `tmp_review_probe_*/`：局部探针验证目录，用于快速验证特定规则或异常案例

这些 `tmp_review_*` 目录属于**本地审阅产物**，不是面向最终用户的稳定接口文档。

## 源码目录

核心代码位于 `src/bibliometrics/`。

### `src/bibliometrics/converters/`

与当前项目定位最相关的目录。

- `src/bibliometrics/converters/scopus.py`：Scopus → WOS 风格转换主逻辑
- `src/bibliometrics/converters/batch.py`：批处理转换逻辑
- `src/bibliometrics/converters/author_database.py`：作者标准化辅助数据库逻辑

当前 round 迭代中，`src/bibliometrics/converters/scopus.py` 是最关键文件，尤其集中在：

- WOS 语料校准
- `C3` 选择与补充
- companion / parent 级机构恢复
- affiliation 映射合理性保护

### `src/bibliometrics/pipeline/`

- 主工作流编排
- WOS / Scopus 合并与去重调度
- 各步骤衔接

### `src/bibliometrics/standardizers/`

- WOS 风格标准化
- AI / Gemini 相关标准化与补全
- 机构名称清洗与标准化

### `src/bibliometrics/filters/`

- 语言筛选
- 年份范围筛选

### `src/bibliometrics/analysis/`

- 文献统计分析
- 图表生成
- 分析报告

### `src/bibliometrics/utils/`

- 路径工具
- 限流与辅助函数
- 其他通用工具

## 配置目录

`config/` 中主要包含：

- `institution_cleaning_rules_ultimate.json`：默认机构清洗规则
- `country_mapping.json`：国家名称映射
- `journal_abbrev.json`：期刊缩写映射
- `biomedical_institutions.json`：机构知识数据
- 各类缓存文件：AI 或标准化阶段生成并复用

## 当前使用文档

### 根目录入口

- `README.md`
- `README.zh-CN.md`
- `README.ja.md`
- `QUICK_START.md`
- `QUICK_START.zh-CN.md`
- `QUICK_START.ja.md`
- `CHANGELOG.md`
- `PROJECT_STRUCTURE.md`

### `docs/` 当前建议阅读

- `docs/README.md`
- `docs/快速使用指南.md`
- `docs/使用指南.md`
- `docs/数据准备说明.md`
- `docs/WOS标准化说明.md`
- `docs/Scopus数据质量问题分析.md`
- `docs/年份过滤使用指南.md`
- `docs/机构清洗使用指南.md`

### `docs/` 历史或背景材料

- `docs/AI补全系统完整总结.md`
- `docs/changelogs/`
- `docs/release/`
- `docs/security/`
- `docs/internal/`

这些目录和文档保留原始上下文，可能出现旧版本术语、旧流程或旧命令，不应和“当前使用文档”混用。

## 推荐阅读顺序

1. `README.zh-CN.md` / `README.md` / `README.ja.md`
2. `QUICK_START.zh-CN.md` / `QUICK_START.md` / `QUICK_START.ja.md`
3. `docs/README.md`
4. `docs/WOS标准化说明.md`
5. `docs/Scopus数据质量问题分析.md`
6. `docs/使用指南.md`

## 方法边界

为避免误解，当前系统明确遵循以下边界：

- 不是普通“机构清洗项目”
- 不是纯靠外部数据库查表
- 不是按重复 DOI 直接复制 WOS 字段
- 是基于**本地规则 + 当前 WOS 输入校准 + 原始 Scopus affiliation 证据**的保守转换与整合流程

## 仓库整洁约定

- `__pycache__/`、`*.pyc` 不应纳入版本控制
- macOS 资源分叉文件 `._*` 不应纳入版本控制
- `tmp_review_*` 属于本地验证输出，应与源码和正式文档区分管理
- 当前实际命令入口以 `run_ai_workflow.py` 和 `scripts/run_workflow.py` 为准
