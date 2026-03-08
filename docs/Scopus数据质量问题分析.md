# Scopus→WOS 对齐中的质量问题与当前处理策略

## 这份文档的定位

这不是一份“普通数据清洗问题汇总”，而是一份针对当前项目主线的背景说明：

- 为什么 Scopus→WOS 转换难
- 为什么不能把问题简化为普通机构清洗
- 为什么当前系统要用 WOS 重复对做校准
- 为什么 `C3` 需要保守处理，而不能全局乱补

## 核心判断

Scopus 的问题不只是“脏”，而是**与 WOS 的组织表达层级不一致**。这会直接影响：

- 转换后的 WOS 风格是否自然
- WOS / Scopus 去重是否稳定
- Scopus 独有记录能否顺利融入 WOS 语料
- 后续机构共现、合作网络、机构排名等分析结果

因此，当前项目的主问题应理解为：**Scopus→WOS 对齐问题**，而不是普通清洗问题。

## 当前最重要的问题类型

### 1. companion / parent 级组织缺失

Scopus 经常只给出局部单位，而 WOS 更容易保留 companion / parent 级组织。常见表现包括：

- institute 缺 academy / university companion
- hospital 缺 university / system companion
- research center 缺 parent institution

这类问题会直接造成 `C3` 与 WOS 风格不一致。

### 2. 机构层级选择不一致

同一条记录里，Scopus 和 WOS 可能都“没错”，但选择的组织层级不同，例如：

- 只保留具体 institute
- 只保留 parent university / academy
- 同时保留 institute + parent
- system 级组织是否进入 `C3`

这里不能靠“谁出现过就都补上”，必须保持保守。

### 3. 原始 affiliation 片段化，导致映射不稳

Scopus 原始 affiliation 常常更碎、更短、层级关系更模糊。如果直接复用某个参考映射，很容易误把：

- 不相干的 parent 组织补进去
- 另一个机构系统的 companion 错迁过来
- 只在少数重复对里成立的模式泛化到全局

因此需要 plausibility guard 来控制精确映射复用。

### 4. WOS 风格往往更压缩、更规范

WOS 在组织名表达上经常更压缩，例如：

- 简写更稳定
- parent / companion 组合更固定
- 同一机构的写法更集中

Scopus 转换后的目标不是逐字符复刻 WOS，而是尽量对齐到**结构、层级和可分析性**都接近 WOS。

### 5. Scopus 也可能比 WOS 更“多”

有些重复对里，Scopus 的 `C3` 会比 WOS 多出若干组织。这里不能简单认为“更多就更好”。

当前系统的原则是：

- 优先减少明确的漏项
- 对明显多出的组织保持谨慎
- 不为了追求表面一致而盲目删减或扩写

## 当前处理策略

### 策略一：先做本地转换，再做 WOS 校准

系统先把 Scopus 转成 WOS 风格结构，再利用当前 `wos.txt` 中的重复记录校准差异，而不是先做一堆泛化清洗再说。

### 策略二：重复对用于校准规则，不用于直接抄字段

重复文献最重要的作用是回答两个问题：

1. 哪些组织在 Scopus 中经常被漏掉？
2. 这些漏项能否从原始 Scopus affiliation 中找到足够证据？

如果没有证据，就不应该因为 WOS 里出现过而直接补回。

### 策略三：补充必须有原始 Scopus affiliation 证据

当前 round 迭代中，`C3` 的 companion 恢复必须尽量依赖：

- 原始 affiliation 文本中的局部短语
- institute / center / hospital / academy / university 的可追溯关联
- 当前 WOS 输入中重复对所揭示的稳定模式

### 策略四：对精确映射加合理性保护

即使某个 WOS / Scopus 重复对里出现过“精确映射”，也不能无条件套用到其他记录。当前系统会增加合理性保护，避免：

- 一次匹配，处处复用
- system / parent 级组织误补
- 不同机构体系之间发生串扰

### 策略五：明确拒绝激进的全局共现补全

当前系统明确避免回到早期那种“只要全局经常共现，就全部补进 `C3`”的策略，因为它会快速引入大量噪声。

## 当前方法不是什么

当前方法：

- 不是普通机构清洗
- 不是单纯外部数据库查表
- 不是按 DOI 复制 WOS 字段
- 不是纯统计共现补全

更准确地说，它是一个：

- 基于本地规则
- 以当前 WOS 输入为主标准
- 结合重复对校准
- 结合原始 Scopus affiliation 证据
- 保守迭代 `C3`

的 Scopus→WOS 转换与整合流程。

## 当前验证快照

当前本地示例验证方式：

```bash
python3 run_ai_workflow.py --data-dir Example --no-ai
```

已实际基于 `Example/wos.txt` 与 `Example/scopus.csv` 做重复对核对。当前 local round11 快照为：

- 重复对数量：100 组
- 关注字段：`C3`
- 差异数量：从 `24` 降到 `12`

这类验证结果说明：当前改进是通过规则收敛逐步逼近 WOS，而不是靠直接借用 WOS 字段制造“伪一致”。

## 后续仍需关注的残留方向

即使在当前 round11 后，残留问题仍主要集中在以下模式：

- academy / institute / university companion 仍有少量漏项
- hospital / research center 的 parent 级组织偶有缺失
- system 级组织需要更严格但仍保守的触发条件
- 少数记录中 Scopus 比 WOS 额外多出组织，仍需进一步判断是否应收敛

后续迭代仍应坚持：**先看重复对，再看原始 affiliation 证据，再决定是否写成泛化规则。**
