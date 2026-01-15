# MultiDatabase v4.4.0 更新日志

**发布日期**: 2025-11-17
**版本**: v4.4.0 (WOS Format Alignment)

## 🎯 核心功能：WOS格式对齐

### ⭐ 重大更新

**Scopus独有记录自动对齐WOS标准格式！**

在合并去重阶段，系统会自动将Scopus独有记录（未在WOS中出现的记录）的格式对齐到WOS标准：

1. **机构名称（C3字段）**：如果在WOS中出现过，使用WOS的写法
2. **期刊名称（SO字段）**：如果在WOS中出现过，使用WOS的写法
3. **国家名称（C1字段）**：如果在WOS中出现过，使用WOS的写法
4. **作者名称（AU字段）**：如果在WOS中出现过，使用WOS的写法

### 🔧 技术实现

**新增类**: `WOSStandardExtractor`
- 位置：`merge_deduplicate.py:192-322`
- 功能：
  - `extract_from_wos_records()`: 从WOS记录中提取所有标准格式
  - `standardize_scopus_record()`: 将Scopus记录标准化为WOS格式

**修改**: `MergeDeduplicateTool`
- 新增步骤2：提取WOS标准格式
- 修改步骤4：合并记录时自动对齐Scopus独有记录

### 📊 处理流程

```
步骤1: 读取WOS和Scopus文件
   ↓
步骤2: 从WOS记录中提取标准格式 ⭐ 新增
   - 提取机构、期刊、国家、作者的标准格式
   ↓
步骤3: 识别WOS-Scopus重复记录
   ↓
步骤4: 合并记录 ⭐ 改进
   - Scopus独有记录自动对齐WOS标准
   ↓
步骤5: 写入输出文件
```

### 📈 统计报告改进

合并去重报告新增信息：
```
Scopus独有记录:         150 条（已保留）
  ⭐ Scopus独有记录标准化: 150 条
     （机构、期刊、国家、作者已对齐WOS格式）
```

详细说明：
```
- ⭐ Scopus独有记录已对齐WOS标准格式：
    · 机构名称：如果在WOS中出现过，使用WOS格式
    · 期刊名称：如果在WOS中出现过，使用WOS格式
    · 国家名称：如果在WOS中出现过，使用WOS格式
    · 作者名称：如果在WOS中出现过，使用WOS格式
```

## 🎨 GUI改进

### v2.1 更新

**显示问题修复**：
1. ✅ 窗口高度自适应屏幕（85%屏幕高度，最小900px）
2. ✅ 窗口宽度调整为1300px
3. ✅ **支持窗口自由调整大小**
4. ✅ **整体界面支持滚动**（CTkScrollableFrame）
5. ✅ 最小窗口尺寸: 1100x800

**布局优化**：
- 卡片间距缩小（15px → 10px）
- 内边距缩小（20px → 18px）
- 字体大小优化（1-2pt缩减）
- 日志区域固定高度（300px，避免占用过多空间）

**版本更新**：
- 窗口标题：v4.4.0 - WOS Format Alignment
- 版本标签：v4.4.0
- 特性标签：✨ AI增强 | 🎯 WOS格式对齐 | ⚡ 批量处理 | 📈 专业输出

## 📝 文档更新

**新增文档**：
- `WOS_FORMAT_ALIGNMENT.md`: WOS格式对齐功能详细说明
- `CHANGELOG_v4.4.0.md`: 版本更新日志

## ✨ 优势与价值

### 1. 数据质量提升
- **格式一致性**：所有记录使用统一的格式标准（WOS）
- **避免误判**：VOSviewer/CiteSpace不会因格式差异误判同一实体

### 2. 分析准确性
- **机构共现分析**：同一机构不会因大小写差异被识别为不同实体
- **作者合作网络**：作者名称格式统一，提高识别准确率
- **国际合作分析**：国家名称使用WOS标准（如：Peoples R China）

### 3. 用户体验
- **自动化**：无需手动调整，系统自动对齐
- **可追溯**：报告中显示详细的标准化统计信息
- **透明度**：清晰说明哪些记录被标准化

## 🔄 向后兼容

- ✅ 完全兼容现有工作流
- ✅ 不影响WOS-Scopus重复对的合并逻辑
- ✅ 仅对Scopus独有记录进行标准化
- ✅ 如果机构/期刊/作者只在Scopus中出现，保留Scopus格式

## 📦 修改的文件

1. **merge_deduplicate.py**
   - 新增：`WOSStandardExtractor` 类
   - 修改：`MergeDeduplicateTool` 类
   - 修改：合并流程（5步）
   - 修改：统计报告格式

2. **gui_app.py**
   - 版本号：v2.0 → v2.1
   - 窗口高度：自适应（85%屏幕）
   - 添加：滚动支持
   - 优化：布局和间距

3. **文档**
   - 新增：`WOS_FORMAT_ALIGNMENT.md`
   - 新增：`CHANGELOG_v4.4.0.md`

## 🚀 使用方法

无需额外配置，自动集成到工作流：

```bash
# GUI方式（推荐）
python3 gui_app.py

# 命令行方式
python3 run_ai_workflow.py --data-dir "/path/to/data"

# 单独运行合并去重
python3 merge_deduplicate.py wos.txt scopus_converted.txt merged.txt
```

## 📊 示例效果

### 对齐前（Scopus独有记录）
```
C3 peking university; tsinghua university
SO nature medicine
C1 [Zhang, Y] Peking Univ, Beijing, China.
```

### 对齐后（使用WOS格式）
```
C3 PEKING UNIVERSITY; Tsinghua University
SO NATURE MEDICINE
C1 [Zhang, Y] Peking Univ, Beijing, Peoples R China.
```

## 🎓 适用场景

1. **文献计量分析**：确保VOSviewer、CiteSpace准确识别
2. **机构共现分析**：避免同一机构被识别为不同实体
3. **作者合作网络**：作者名称格式统一
4. **国际合作分析**：国家名称标准化

## ⚠️ 注意事项

1. **对齐范围**：只对齐在WOS中出现过的内容
2. **保留原创**：如果只在Scopus中出现，保留Scopus格式
3. **不区分大小写**：匹配时不区分大小写
4. **精确匹配**：使用完全匹配，避免误判

## 🙏 致谢

感谢用户的宝贵反馈，帮助我们不断改进产品质量！

---

**开发者**: Meng Linghan
**开发工具**: Claude Code
**版本**: v4.4.0 (WOS Format Alignment)
**日期**: 2025-11-17
