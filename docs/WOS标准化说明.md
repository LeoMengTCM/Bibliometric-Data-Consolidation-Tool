# WOS 标准化与 `C3` 对齐说明

## 这份说明解决什么问题

本项目中的“WOS 标准化”并不只是把字段格式改得像 WOS 一样，更重要的是：

- 尽可能让 Scopus 记录在结构上、组织字段上接近 WOS
- 让转换后的 Scopus 能自然混入 WOS 语料
- 在 WOS / Scopus 去重与合并时保持一致性
- 尤其保守地处理 `C3` 选择与 companion / parent 级组织补充

因此，这里说的“标准化”本质上是一个**以 WOS 为主标准的转换与校准过程**。

## 当前实现由哪几层组成

### 1. 本地结构转换

首先把 `scopus.csv` 转成 WOS 风格纯文本记录，包括常见字段结构、换行形式和多值字段组织方式。

这一步是整个系统的底座，即使关闭 AI 也仍然执行。

### 2. 当前 WOS 输入语料校准

系统会把当前输入目录里的 `wos.txt` 当成**主参考语料**，从中提取对齐线索，用于：

- 识别 WOS 风格下更常见的组织表达
- 校准 Scopus 转换时的机构层级选择
- 评估哪些 companion / parent 级组织值得保守恢复

这里依赖的是**当前输入的 WOS 语料**，不是外部机构权威数据库。

### 3. 保守的 `C3` 恢复与补充

这是当前 round 迭代中最核心的部分。

当前策略强调三点：

1. **重复对只用于校准，不直接抄 WOS 字段**  
   WOS / Scopus 的重复文献用于发现“Scopus 常漏哪些 companion / parent 级组织”，但不会因为 DOI 对上就直接把 WOS 的 `C3` 填回 Scopus。

2. **必须有原始 Scopus affiliation 证据**  
   只有当原始 Scopus affiliation 文本本身能支持该组织存在时，才允许恢复或补充 `C3`。

3. **要有合理性保护**  
   对精确 affiliation 映射和 companion 恢复都要加 plausibility guard，避免把一个 WOS 组织模式错误复用到不相干记录上。

目前重点在于减少以下类型的漏项：

- institute ↔ academy / university companion
- hospital ↔ university / system companion
- parent 级组织缺失
- system 级组织在少数场景下的保守补回

同时明确避免回到“只要全局共现过就到处乱补”的旧策略。

### 4. 可选 AI 分支

当 AI 启用时，还会附加：

- 国家名和期刊名的进一步标准化
- 机构信息补全

AI 分支是附加层，不是当前 `C3` 对齐逻辑的根基。

## `--no-ai` 的真实行为

`--no-ai` 关闭的是 AI 分支，但**不会**关闭以下核心逻辑：

- 本地 Scopus → WOS 风格转换
- 当前 WOS 语料校准
- 基于重复对校准的本地 `C3` 恢复
- 合并去重、语言筛选、机构清洗与分析

也就是说，`--no-ai` 仍然保留当前最关键的本地 WOS 对齐机制。

## 当前方法明确不做什么

为避免误解，当前方法明确不做以下事情：

- 不按 DOI 直接把单条 WOS 记录的 `C3` 覆盖到 Scopus 输出
- 不把外部机构数据库当成主真值来源
- 不用全局共现规则激进补 companion
- 不把“看起来像 parent”就全部补进 `C3`

## 当前验证方式

当前项目要求每轮都基于**实际运行结果**验证，而不是凭印象修改。

推荐的最小可复现方式：

```bash
python3 run_ai_workflow.py --data-dir Example --no-ai
```

当前本地 round11 验证快照：

- 输入：`Example/wos.txt` + `Example/scopus.csv`
- 对照方式：WOS 与转换后 Scopus 的重复文献逐对检查
- 关注字段：`C3`
- 结果：100 组重复对中的 `C3` 差异已从 `24` 降到 `12`

这说明当前系统是通过**泛化规则迭代**在逐步逼近 WOS，而不是靠直接偷用 WOS 字段完成表面对齐。

## 相关代码

当前最关键的实现位于：

- `src/bibliometrics/converters/scopus.py`

相关逻辑包括：

- 当前 WOS 参考语料构建
- 原始 Scopus affiliation 候选抽取
- `C3` raw recovery / companion map
- affiliation 映射合理性保护

如果后续继续迭代 `C3`，应优先在这里做**保守、可泛化、可复验**的修改。
