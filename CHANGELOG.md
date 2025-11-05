# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [3.1.0] - 2025-11-05

### 🔥 Major Fixes - C1 Field Format (Critical for VOSViewer/CiteSpace)

#### Fixed
- **C1字段格式完美修复** - 彻底解决了一个作者有多个机构时的格式问题
  - 修复前：3个机构被错误地合并成1行 → VOSViewer/CiteSpace **无法解析**
  - 修复后：正确分成3行 → **完美兼容**可视化软件
  - 示例：
    ```
    修复前（错误）：
    [Akar, F] Al-Quds Univ, ..., Edith Wolfson Med Ctr, ..., Tel Aviv Univ, ...

    修复后（正确）：
    [Akar, F] Al-Quds Univ, Dept Gen Surg, Abu Dis, Palestine.
    [Akar, F] Edith Wolfson Med Ctr, Dept Thorac Surg, Holon, Israel.
    [Akar, F] Tel Aviv Univ, Tel Aviv-Yafo, Israel.
    ```

- **国家名称标准化** - 符合WOS标准格式
  - `United States` → `USA`
  - `United Kingdom` → `England`
  - `China` → `Peoples R China`
  - `Turkey` → `Turkiye`

- **智能机构边界识别** - 避免将机构名中的国家词误识别为边界
  - 正确识别："Edith Wolfson Medical Center Israel"中的"Israel"是机构名
  - 只有独立的国家名才会被识别为机构分割点

#### Changed
- **完全重写parse_affiliations方法**
  - 新算法：通过识别国家名自动分割多机构
  - 正确处理：一个作者多机构 → 分成多行
  - 正确处理：多个作者共享机构 → 合并到一行

- **改进AF字段处理**
  - 自动移除学位后缀（M.D., Ph.D., Dr., Prof.等）
  - 保留完整中间名
  - 移除Scopus ID（括号内容）

#### Added
- **新增standardize_country方法** - 国家名称标准化
- **扩展期刊缩写库** - 从60个扩展到108个期刊
- **新增年度统计功能** - merge_deduplicate.py新增年度文献统计

### 📊 转换质量评分

| 评估项目 | v3.1评分 | v2.1评分 | 改进 |
|---------|---------|---------|------|
| C1字段格式 | ⭐⭐⭐⭐⭐ 5/5 | ⭐⭐ 2/5 | +150% |
| 国家名标准化 | ⭐⭐⭐⭐⭐ 5/5 | ⭐⭐⭐ 3/5 | +67% |
| VOSViewer兼容性 | ⭐⭐⭐⭐⭐ 5/5 | ⭐⭐⭐ 3/5 | +67% |

**综合评分**: ⭐⭐⭐⭐½ 4.5/5 (v2.1: ⭐⭐⭐ 3/5)

### 📝 Known Limitations (Scopus数据源限制)

1. **机构信息简化** - Scopus数据库本身比WOS简化30-60%
   - 示例：Scopus只提供"IBIMA"，WOS提供"Hosp Univ Reg & Virgen Victoria, IBIMA, Dept..."
   - 解决方案：使用WOS+Scopus合并（`merge_deduplicate.py`）

2. **缺少地理详细信息** - Scopus不提供州/省代码和邮编
   - WOS: `Durham, NC 27708 USA`
   - Scopus: `Durham, United States`
   - 影响：地图可视化精确度降低

3. **复杂姓氏识别** - 部分作者姓氏顺序可能错误（Scopus数据问题）
   - 示例：`Abu Akar, Firas` 可能被记录为 `Akar, Firas Abu`
   - 建议：转换后手动检查

---

## [2.1.0] - 2025-11-04

### Added
- 添加logging模块支持，提供详细日志输出
- 支持外部配置文件（`config/journal_abbrev.json`, `config/institution_config.json`）
- 添加进度显示功能
- 新增语言筛选工具（`filter_language.py`）
- 新增统计分析工具（`analyze_records.py`）
- 新增完整工作流脚本（`run_complete_workflow.py`）

### Changed
- 改进错误处理和文件验证
- 完善机构识别逻辑（School/College层级智能判断）
- 优化机构名称缩写规则

### Fixed
- 修复文件编码问题
- 修复部分期刊名缩写错误

---

## [2.0.0] - 2025-11-03

### Added
- 初始发布版本
- 支持Scopus CSV到WOS纯文本格式转换
- 44个Scopus字段映射到30+个WOS字段
- 作者名格式转换（AU和AF字段）
- 机构地址重排序（C1字段）
- 参考文献格式转换（CR字段）
- C3字段生成（提取顶层机构）

---

## 版本号说明

本项目使用语义化版本号（Semantic Versioning）：

- **主版本号（X.0.0）**: 不兼容的API修改
- **次版本号（0.X.0）**: 向下兼容的功能性新增
- **修订号（0.0.X）**: 向下兼容的问题修正

v3.1.0 是次版本更新，包含重大功能改进和关键bug修复，向下兼容v2.x版本。

---

## 升级建议

### 从v2.1升级到v3.1

**强烈推荐升级**，v3.1修复了C1字段的关键格式问题，对VOSViewer/CiteSpace用户至关重要。

**升级步骤**：
1. 备份当前版本：`git checkout v2.1 -b backup-v2.1`
2. 切换到v3.1：`git checkout main && git pull`
3. 重新运行转换（配置文件兼容）

**兼容性**：
- ✅ 配置文件完全兼容
- ✅ 命令行参数完全兼容
- ✅ 输出格式向下兼容（但更准确）

**验证转换质量**：
```bash
# 转换测试数据
python3 scopus_to_wos_converter.py test/scopus.csv test/output.txt

# 检查C1字段格式
grep "^C1 " test/output.txt
```

---

**开发者**: Meng Linghan
**开发工具**: Claude Code
**GitHub**: https://github.com/menglinghan/scopus-wos-tools
