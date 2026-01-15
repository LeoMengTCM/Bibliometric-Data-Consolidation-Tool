# WOS格式对齐功能说明

## ⭐ 核心功能

**Scopus独有记录必须严格以WOS格式为准！**

在合并去重过程中，系统会自动将Scopus独有记录的格式对齐到WOS标准：

### 对齐字段

1. **机构名称（C3字段）**
   - 如果某个机构在WOS中出现过，使用WOS的写法
   - 例如：`PEKING UNIVERSITY` (WOS) vs `peking university` (Scopus) → 统一为 `PEKING UNIVERSITY`

2. **期刊名称（SO字段）**
   - 如果某个期刊在WOS中出现过，使用WOS的写法
   - 例如：`NATURE` (WOS) vs `Nature` (Scopus) → 统一为 `NATURE`

3. **国家名称（C1字段）**
   - 如果某个国家在WOS中出现过，使用WOS的写法
   - 例如：`Peoples R China` (WOS) vs `China` (Scopus) → 统一为 `Peoples R China`

4. **作者名称（AU字段）**
   - 如果某个作者在WOS中出现过，使用WOS的写法
   - 例如：`Zhang, Y` (WOS) vs `Zhang, Y.` (Scopus) → 统一为 `Zhang, Y`

## 📊 处理流程

```
步骤1: 读取WOS和Scopus文件
   ↓
步骤2: 从WOS记录中提取标准格式
   - 提取所有机构名称（C3字段）
   - 提取所有期刊名称（SO字段）
   - 提取所有国家名称（C1字段）
   - 提取所有作者名称（AU字段）
   ↓
步骤3: 识别WOS-Scopus重复记录
   ↓
步骤4: 合并记录
   - WOS-Scopus重复对：以WOS为准，Scopus补充缺失字段
   - WOS独有记录：直接保留
   - Scopus独有记录：⭐ 对齐WOS标准格式
   ↓
步骤5: 写入输出文件
```

## 🎯 对齐逻辑

### 1. 机构名称对齐（C3字段）

```python
# 原始Scopus C3字段
C3 = "peking university; tsinghua university"

# WOS中已有的机构格式
WOS_institutions = {
    "peking university": "PEKING UNIVERSITY",
    "tsinghua university": "Tsinghua University"
}

# 对齐后
C3 = "PEKING UNIVERSITY; Tsinghua University"
```

### 2. 期刊名称对齐（SO字段）

```python
# 原始Scopus SO字段
SO = "Nature Medicine"

# WOS中已有的期刊格式
WOS_journals = {
    "nature medicine": "NATURE MEDICINE"
}

# 对齐后
SO = "NATURE MEDICINE"
```

### 3. 国家名称对齐（C1字段）

```python
# 原始Scopus C1字段
C1 = "[Zhang, Y] Peking Univ, Sch Med, Beijing, China."

# WOS中已有的国家格式
WOS_countries = {
    "china": "Peoples R China"
}

# 对齐后
C1 = "[Zhang, Y] Peking Univ, Sch Med, Beijing, Peoples R China."
```

## 📈 统计信息

合并去重完成后，报告会显示：

```
合并去重报告
============================================================
WOS原始记录数:          500 条
Scopus原始记录数:       300 条

WOS-Scopus重复记录:     150 条（已从Scopus删除）
Scopus独有记录:         150 条（已保留）
  ⭐ Scopus独有记录标准化: 150 条
     （机构、期刊、国家、作者已对齐WOS格式）

最终记录数:             650 条
  = WOS记录（含补充）:  500 条
  + Scopus独有:         150 条
```

## 🔧 技术实现

### WOSStandardExtractor类

负责从WOS记录中提取标准格式：

- `extract_from_wos_records()`: 提取WOS中的所有标准格式
- `standardize_scopus_record()`: 将Scopus记录标准化为WOS格式

### 关键代码位置

- 文件：`merge_deduplicate.py`
- 类：`WOSStandardExtractor`
- 方法：
  - `extract_from_wos_records()` (行192-248)
  - `standardize_scopus_record()` (行250-322)
  - `merge_records()` (行510-545)

## ✅ 优势

1. **格式一致性**：所有记录使用统一的格式标准（WOS）
2. **数据质量**：避免VOSviewer/CiteSpace因格式差异而误判
3. **自动化**：无需手动调整，系统自动对齐
4. **可追溯**：报告中显示标准化统计信息

## 📝 示例

### 对齐前（Scopus独有记录）

```
PT J
AU Smith, J.
   Wang, L.
TI A study on cancer research
SO nature medicine
C1 [Smith, J.] Harvard Univ, Boston, USA.
   [Wang, L.] Peking Univ, Beijing, China.
C3 harvard university; peking university
```

### 对齐后（使用WOS格式）

```
PT J
AU Smith, J
   Wang, L
TI A study on cancer research
SO NATURE MEDICINE
C1 [Smith, J] Harvard Univ, Boston, USA.
   [Wang, L] Peking Univ, Beijing, Peoples R China.
C3 Harvard University; PEKING UNIVERSITY
```

## 🎓 适用场景

- **文献计量分析**：确保VOSviewer、CiteSpace等工具准确识别机构/作者
- **机构共现分析**：避免同一机构因格式差异被识别为不同实体
- **作者合作网络**：确保作者名称格式统一
- **国际合作分析**：国家名称使用WOS标准格式

## 🚀 使用方法

合并去重时自动执行，无需额外配置：

```bash
# 自动工作流（已集成WOS格式对齐）
python3 run_ai_workflow.py --data-dir "/path/to/data"

# 或单独运行合并去重
python3 merge_deduplicate.py wos.txt scopus_converted.txt merged.txt
```

## 💡 注意事项

1. **对齐范围**：只对齐在WOS中出现过的内容
2. **保留原创**：如果某个机构/期刊/作者只在Scopus中出现，保留Scopus格式
3. **不区分大小写**：匹配时不区分大小写
4. **精确匹配**：使用完全匹配（lowercase），避免误判

---

**版本**: v4.4.0 (WOS Format Alignment)
**日期**: 2025-11-17
**作者**: Meng Linghan
**开发工具**: Claude Code
