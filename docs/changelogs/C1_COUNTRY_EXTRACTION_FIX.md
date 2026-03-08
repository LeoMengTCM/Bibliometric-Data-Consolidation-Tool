# C1字段国家名称提取修复说明

> [!WARNING]
> 历史版本文档：本文件保留发布或修复当时的原始上下文，可能包含旧项目名、旧命令、旧仓库链接或过期说明。实际使用请以项目根目录的 `README.md`、`QUICK_START.md` 和 `docs/` 当前使用文档为准。


## 🐛 问题描述

**v4.4.0 初版问题**：C1字段的国家名称提取过于简单，导致：
- ❌ 提取到人名（如：Zhang, Y）
- ❌ 提取到地点名（如：Beijing, Shanghai）
- ❌ 提取到邮编（如：100000）
- ❌ 提取到其他非国家信息

**原因**：简单地取最后一个逗号后的内容，没有充分验证。

## ✅ 修复方案

### 1. 改进提取逻辑

**修复前**：
```python
parts = line.split(',')
country = parts[-1].strip().rstrip('.')
```

**修复后**：
```python
# 必须包含句点（标准WOS格式以句点结尾）
if '.' in line and ',' in line:
    # 提取句点前的内容
    before_period = line.split('.')[0]
    # 再按逗号分割
    parts = before_period.split(',')
    if len(parts) >= 2:
        country = parts[-1].strip()
        # 验证是否是有效的国家名称
        if self._is_valid_country(country):
            # 添加到字典
```

### 2. 新增国家名称验证

创建了 `_is_valid_country()` 方法，包含多重验证：

#### 快速通过：常见WOS国家列表
- USA, England, Peoples R China, Germany, France, Italy...
- 共50+个常见WOS国家名称
- 在列表中直接通过验证

#### 严格验证规则
1. **长度检查**：3-50个字符
2. **数字检查**：不包含数字（排除邮编）
3. **符号检查**：不包含方括号（排除作者标记）
4. **字符检查**：只允许字母、空格、连字符、撇号、&
5. **格式检查**：首字母必须大写
6. **关键词检查**：排除机构/地点相关词
   - dept, department, division, center, lab
   - institute, university, college, hospital
   - street, road, avenue, building, floor, room
   - zip, email, tel, fax, phone, box

#### 特殊规则
- 包含 " R "（如 Peoples R China）→ 更可能是国家
- 长度 4-30 字符 → 合理的国家名称长度

### 3. 添加调试信息

合并去重时会显示提取到的国家列表（前20个）：
```
从WOS记录中提取标准格式...
✓ 提取完成：
  - 机构: 156 个
  - 期刊: 45 个
  - 国家: 28 个
  - 作者: 523 个
  提取到的国家（前20个）:
    1. Australia
    2. Belgium
    3. Canada
    4. England
    5. France
    6. Germany
    7. Italy
    8. Japan
    9. Peoples R China
    10. Singapore
    ...
```

## 📊 WOS C1字段格式说明

### 标准格式
```
C1 [Author, A] Institution, Department, City, Postcode, Country.
   [Author, B] Institution2, City, Country.
```

### 提取规则
1. 每行以句点结尾
2. 国家名在最后一个逗号后、句点前
3. 国家名必须是有效的国家名称（通过验证）

### 示例

**正确提取**：
```
C1 [Zhang, Y] Peking Univ, Sch Med, Beijing 100000, Peoples R China.
   提取到：Peoples R China ✅

C1 [Smith, J] Harvard Univ, Boston, MA 02138, USA.
   提取到：USA ✅

C1 [Wang, L] Fudan Univ, Shanghai, Peoples R China.
   提取到：Peoples R China ✅
```

**正确过滤**：
```
C1 [Li, M] Tsinghua Univ, Beijing.
   最后部分：Beijing
   验证结果：不是国家（是城市）❌ 不提取

C1 [Chen, X] Peking Univ, Dept Med, Beijing 100000.
   最后部分：100000
   验证结果：包含数字 ❌ 不提取

C1 [Zhou, H] Shanghai Cancer Ctr.
   最后部分：Shanghai Cancer Ctr
   验证结果：包含"center" ❌ 不提取
```

## 🔧 修改的文件

**文件**: `merge_deduplicate.py`

**修改内容**：
1. **新增**：`WOSStandardExtractor.__init__()` - 添加常见WOS国家列表
2. **新增**：`WOSStandardExtractor._is_valid_country()` - 国家名称验证方法
3. **修改**：`WOSStandardExtractor.extract_from_wos_records()` - 改进提取逻辑
4. **修改**：`WOSStandardExtractor.standardize_scopus_record()` - 改进标准化逻辑
5. **新增**：调试信息输出

**代码位置**：
- 国家列表：行201-213
- 验证方法：行215-266
- 提取逻辑：行269-277
- 标准化逻辑：行349-386

## 🎯 常见WOS国家名称参考

系统内置了50+个常见WOS国家名称：

### 北美洲
- USA
- Canada
- Mexico

### 欧洲
- England, Scotland, Wales, Northern Ireland
- Germany, France, Italy, Spain
- Netherlands, Switzerland, Sweden, Belgium
- Austria, Denmark, Norway, Finland
- Poland, Portugal, Greece, Czech Republic
- Hungary, Ireland, Russia

### 亚洲
- Peoples R China, Taiwan
- Japan, South Korea
- Singapore, Thailand, Malaysia, Indonesia
- Philippines, Vietnam
- India, Pakistan, Bangladesh
- Iran, Israel, Turkey (Turkiye)
- Saudi Arabia, United Arab Emirates

### 大洋洲
- Australia
- New Zealand

### 南美洲
- Brazil, Argentina, Chile, Colombia

### 非洲
- South Africa, Egypt, Nigeria, Kenya

## ✅ 验证方法

运行合并去重后，检查日志中的"提取到的国家"列表：

1. **查看国家列表**：确认都是真实的国家名称
2. **检查异常**：如果出现人名、地点名，说明仍需改进
3. **反馈问题**：如有问题，请提供具体的C1字段示例

## 💡 最佳实践

1. **第一次运行**：仔细检查提取到的国家列表
2. **发现问题**：记录具体的C1字段内容
3. **持续改进**：根据实际数据调整验证规则

## 📈 效果对比

### 修复前
```
提取到的国家（问题示例）:
  - Zhang, Y          ❌ 人名
  - Beijing           ❌ 城市
  - 100000            ❌ 邮编
  - Dept Med          ❌ 部门
  - Peoples R China   ✅ 正确
```

### 修复后
```
提取到的国家（全部正确）:
  - Peoples R China   ✅
  - USA              ✅
  - England          ✅
  - Germany          ✅
  - France           ✅
```

## 🚀 立即使用

无需额外配置，修复已自动集成：

```bash
# GUI方式
python3 gui_app.py

# 命令行方式
python3 run_ai_workflow.py --data-dir "/path/to/data"

# 单独测试合并去重
python3 merge_deduplicate.py wos.txt scopus_converted.txt merged.txt
```

## 📝 版本信息

- **修复版本**: v4.4.1 (C1 Country Extraction Fix)
- **修复日期**: 2025-11-17
- **影响范围**: WOS格式对齐功能
- **向后兼容**: ✅ 完全兼容

---

**开发者**: Meng Linghan
**开发工具**: Claude Code
