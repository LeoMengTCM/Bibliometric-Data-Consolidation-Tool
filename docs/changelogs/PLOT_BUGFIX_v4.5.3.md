# 图表生成修复 v4.5.3

**修复日期**: 2025-11-20
**版本**: v4.5.3 (Plot Generation Fix)
**重要性**: ⭐⭐⭐⭐ 图表生成关键修复

---

## 🐛 修复的问题

### 问题: 图表生成失败 - NaN转换错误 ❌ 严重

**症状**:
- 工作流完成，但 `Figures and Tables` 文件夹为空或只有CSV文件
- 日志显示错误: `cannot convert float NaN to integer`
- 图表文件(.tiff 和 .png)没有生成

**根本原因**:
`plot_document_types.py` 的 `plot_distribution()` 方法在绘制Scopus饼图时，当所有数据都为0时（如未启用AI补全），matplotlib的`pie()`函数计算百分比会出现 **0/0 = NaN** 错误。

**错误位置**: `plot_document_types.py:140`

```python
# ❌ 错误的代码
ax2.pie(data2['Count'], labels=labels2, colors=colors2, autopct='%1.1f%%', ...)
# 当 data2['Count'] 全为0时，autopct计算百分比 → 0/0 → NaN
```

**详细分析**:

1. **触发条件**:
   - 当用户使用 `--no-ai` 参数时
   - `scopus_enriched.txt` 文件不存在
   - `parse_wos_file(scopus_file)` 返回 `{'Article': 0, 'Review': 0}`

2. **错误传播**:
   ```python
   total2 = data2['Count'].sum()  # total2 = 0
   ax2.pie(data2['Count'], ...)   # 尝试绘制全0饼图
   # matplotlib内部：每个扇区 = 值 / 总和 = 0 / 0 = NaN
   # autopct格式化: f'{NaN * 100:.1f}%' → 抛出ValueError
   ```

3. **为什么CSV能生成但图表不能**:
   - CSV只是数据保存，不涉及计算
   - 图表需要计算百分比，触发NaN错误

---

## 🔧 修复方案

### 修复内容

在 `plot_document_types.py:115-163` 的 `plot_distribution()` 方法中，为每个数据集添加了 **总数检查**：

```python
# ✅ 修复后的代码
# Scopus
data2 = data[['Article_Type', 'Scopus_Count']].rename(columns={'Scopus_Count': 'Count'})
total2 = int(data2['Count'].sum())  # 转为int避免float NaN
if total2 > 0:
    # 有数据：正常绘制饼图
    colors2 = [self.palette[cat] for cat in data2['Article_Type']]
    labels2 = [f"{row['Article_Type']}\n(n={int(row['Count'])})" for _, row in data2.iterrows()]
    ax2.pie(data2['Count'], labels=labels2, colors=colors2, autopct='%1.1f%%', ...)
    ax2.text(0, 0, f'n={total2}', ha='center', va='center', fontsize=30, fontweight='bold')
else:
    # 无数据：显示占位文本
    ax2.text(0.5, 0.5, 'No Data', ha='center', va='center', fontsize=20,
            transform=ax2.transAxes, color='gray')
ax2.set_title('Scopus', pad=20)
```

### 修复的关键点

1. **类型转换**: `total2 = int(data2['Count'].sum())`
   - 确保总数是整数，避免float NaN
   - 即使sum()返回NaN，int()会抛出明确的错误而不是静默失败

2. **条件绘制**: `if total2 > 0:`
   - 只在有数据时调用 `ax2.pie()`
   - 避免0/0计算

3. **占位文本**: `ax2.text(0.5, 0.5, 'No Data', ...)`
   - 当无数据时，显示友好的提示文本
   - 使用 `transform=ax2.transAxes` 确保文本居中

4. **同样修复**:
   - WOS饼图（ax1）
   - Final Dataset饼图（ax3）
   - 确保三个图表都能正确处理空数据情况

---

## 📊 修复效果

### 修复前

```
执行: python3 run_ai_workflow.py --data-dir "/path" --no-ai

输出:
  ✓ 步骤1-8: 成功
  ✓ CSV数据已保存: document_types_data.csv
  ✗ 图表生成失败: cannot convert float NaN to integer

结果:
  Figures and Tables/01 文档类型/
    ✓ document_types_data.csv  (有)
    ✗ document_types.tiff      (无)
    ✗ document_types.png       (无)
```

### 修复后

```
执行: python3 run_ai_workflow.py --data-dir "/path" --no-ai

输出:
  ✓ 步骤1-8: 成功
  ✓ CSV数据已保存: document_types_data.csv
  ✓ 图表已保存: document_types.tiff 和 .png

结果:
  Figures and Tables/01 文档类型/
    ✓ document_types_data.csv  (81B)
    ✓ document_types.tiff      (60MB - 高分辨率)
    ✓ document_types.png       (341KB - 预览)
    ✓ plot_document_types.py   (脚本副本)
```

### 图表内容

修复后的图表正确显示:
- **WOS饼图**: 显示Article和Review分布
- **Scopus饼图**: 显示"No Data"占位文本（因为未启用AI）
- **Final Dataset饼图**: 显示最终的Article和Review分布

---

## 🔍 测试验证

### 测试场景 1: 不启用AI补全

```bash
python3 run_ai_workflow.py \
  --data-dir "/Users/xxx/文献计量学/雄脱+ECMP" \
  --year-range 2015-2024 \
  --no-ai

# 结果:
✓ 图表生成成功
✓ Scopus饼图显示 "No Data"
✓ WOS 和 Final 饼图正常显示数据
```

### 测试场景 2: 启用AI补全

```bash
python3 run_ai_workflow.py \
  --data-dir "/Users/xxx/文献计量学/雄脱+ECMP" \
  --year-range 2015-2024

# 结果:
✓ 图表生成成功
✓ 所有三个饼图都显示数据
✓ Scopus饼图显示 scopus_enriched.txt 的数据
```

### 测试场景 3: GUI界面

```bash
python3 gui_app.py

# 操作:
1. 选择数据文件夹
2. 勾选"生成专业分析图表"
3. 点击"开始处理"

# 结果:
✓ 进度条实时更新（v4.5.2修复）
✓ 图表自动生成
✓ 处理完成后弹出提示
✓ Figures and Tables 文件夹包含完整图表
```

---

## 📁 修改的文件

### plot_document_types.py

**修改位置**: 第115-163行

**修改内容**:
1. 第125行: `total1 = int(data1['Count'].sum())`
2. 第126-135行: 添加 `if total1 > 0:` 条件分支
3. 第139行: `total2 = int(data2['Count'].sum())`
4. 第140-149行: 添加 `if total2 > 0:` 条件分支
5. 第153行: `total3 = int(data3['Count'].sum())`
6. 第154-163行: 添加 `if total3 > 0:` 条件分支

**修改行数**: 约50行

---

## 🚀 使用建议

### 推荐使用方式

1. **GUI界面**（最简单）:
   ```bash
   python3 gui_app.py
   ```
   - ✅ 进度条实时更新
   - ✅ 自动生成图表
   - ✅ 友好的错误提示

2. **命令行（完整功能）**:
   ```bash
   python3 run_ai_workflow.py \
     --data-dir "/path/to/data" \
     --year-range 2015-2024
   ```
   - ✅ AI补全（默认启用）
   - ✅ 机构清洗（默认启用）
   - ✅ 图表生成（默认启用）

3. **命令行（快速测试）**:
   ```bash
   python3 run_ai_workflow.py \
     --data-dir "/path/to/data" \
     --year-range 2015-2024 \
     --no-ai
   ```
   - ⚡ 跳过AI补全，速度更快
   - ✅ 图表仍然正常生成
   - ✅ Scopus饼图显示"No Data"

### 图表文件用途

生成的图表文件:
- **document_types.tiff** (60MB, 300 DPI)
  - 用于论文投稿
  - 高分辨率，印刷质量
  - 适合期刊要求

- **document_types.png** (341KB)
  - 用于预览和PPT
  - 快速加载
  - 在线分享

- **document_types_data.csv**
  - 原始统计数据
  - Excel可直接打开
  - 用于自定义分析

---

## 📖 相关修复

### v4.5.1 (2025-11-20)
- ✅ AI补全C1格式修复（州/邮编分离）
- ✅ C3人名过滤修复
- 文档: `BUGFIX_v4.5.1.md`

### v4.5.2 (2025-11-20)
- ✅ GUI进度条实时更新
- ✅ 图表生成控制参数
- 文档: `GUI_BUGFIX_v4.5.2.md`

### v4.5.3 (2025-11-20) ⭐ 本次修复
- ✅ 图表生成NaN错误修复
- ✅ 空数据占位文本显示
- 文档: `PLOT_BUGFIX_v4.5.3.md`

---

## 🎯 总结

### 问题本质
matplotlib的`pie()`函数在处理全0数据时，计算百分比会产生NaN值，导致绘图失败。

### 解决方案
在绘制饼图前检查数据总数，当总数为0时显示占位文本而不是调用`pie()`。

### 影响范围
- **修复前**: 使用 `--no-ai` 参数时，图表生成失败
- **修复后**: 所有场景下图表都能正常生成，空数据显示"No Data"

### 预期效果
- ✅ GUI和命令行都能正确生成图表
- ✅ 支持有/无AI补全两种模式
- ✅ 图表质量符合论文投稿要求
- ✅ 错误信息清晰，易于诊断

---

**开发者**: Meng Linghan
**开发工具**: Claude Code
**版本**: v4.5.3 (Plot Generation Fix)
**日期**: 2025-11-20
