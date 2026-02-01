# 🚨 紧急安全警告 - API密钥泄露

**发现时间**: 2026-01-15
**严重程度**: 🔴 HIGH
**状态**: ⚠️ 需要立即处理

---

## ⚠️ 问题描述

在GitHub推送过程中，发现以下敏感信息被硬编码在源代码中：

- **API密钥**: `sk-leomeng1997`
- **API URL**: `https://gptload.drmeng.top/proxy/bibliometrics/v1beta`

### 受影响的文件（13个）

**Python源文件（9个）**：
1. `enhanced_converter_batch_v2.py:49-50`
2. `wos_standardizer_batch.py:622-623`
3. `run_ai_workflow.py:336-337`
4. `gemini_enricher_v2.py:778-779`
5. `wos_standardizer.py:371-372`
6. `enhanced_converter.py:47-48`
7. `institution_enricher_v2.py:396, 402-403`
8. `gemini_config.py:40, 197-198`
9. `CLAUDE.md:535-536`

**文档文件（4个）**：
10. `docs/快速使用指南.md`
11. `docs/WOS标准化说明.md`
12. `docs/使用指南.md`
13. `CLAUDE.md`

---

## 🛡️ 立即执行的步骤

### 步骤1: 撤销API密钥 ⭐ 最优先

**立即前往API提供商网站撤销密钥**：
- 登录 `https://gptload.drmeng.top` 或API管理后台
- 找到密钥 `sk-leomeng1997`
- **立即撤销/删除此密钥**
- 生成新的API密钥

**⚠️ 原因**: 一旦密钥被推送到GitHub，应视为已公开，任何人都可能已经复制使用。

---

### 步骤2: 从Git历史中删除敏感信息

使用 BFG Repo Cleaner（推荐）或 git filter-branch 清理历史。

#### 方法A: 使用 BFG Repo Cleaner（最简单） ⭐ 推荐

```bash
# 1. 安装 BFG
brew install bfg

# 2. 创建密钥文件
echo "sk-leomeng1997" > secrets.txt

# 3. 清理所有历史
bfg --replace-text secrets.txt --no-blob-protection MultiDatabase

# 4. 清理引用
cd MultiDatabase
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 5. Force push（会覆盖GitHub历史）
git push origin main --force
git push origin --tags --force
```

#### 方法B: 使用 git filter-branch（手动）

```bash
cd /Users/menglinghan/Desktop/MultiDatabase

# 从所有历史中删除包含密钥的行
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch *.py *.md || true" \
  --prune-empty --tag-name-filter cat -- --all

# 清理引用
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push
git push origin main --force
git push origin --tags --force
```

---

### 步骤3: 修改代码使用环境变量

已创建以下文件：
- ✅ `.env.example` - 环境变量模板
- ✅ `.gitignore` - 已添加 `.env` 忽略规则

**创建你的 .env 文件**：
```bash
cd /Users/menglinghan/Desktop/MultiDatabase
cp .env.example .env

# 编辑 .env 填入新的API密钥
nano .env
```

`.env` 内容示例：
```bash
GEMINI_API_KEY=your-new-api-key-here
GEMINI_API_URL=https://gptload.drmeng.top/proxy/bibliometrics/v1beta
GEMINI_MODEL=gemini-2.5-flash
```

---

### 步骤4: 修改源代码（需要手动完成）

需要修改所有硬编码API密钥的文件，改为从环境变量读取：

**修改示例** (`run_ai_workflow.py`):
```python
# 修改前：
config = GeminiConfig.from_params(
    api_key='sk-leomeng1997',  # ❌ 硬编码
    api_url='https://gptload.drmeng.top/proxy/bibliometrics/v1beta',
    model='gemini-2.5-flash-lite'
)

# 修改后：
import os
from dotenv import load_dotenv  # pip install python-dotenv

load_dotenv()  # 加载 .env 文件

config = GeminiConfig.from_params(
    api_key=os.getenv('GEMINI_API_KEY'),  # ✅ 从环境变量读取
    api_url=os.getenv('GEMINI_API_URL', 'https://gptload.drmeng.top/proxy/bibliometrics/v1beta'),
    model=os.getenv('GEMINI_MODEL', 'gemini-2.5-flash-lite')
)
```

**需要修改的所有文件**：
1. `enhanced_converter_batch_v2.py`
2. `wos_standardizer_batch.py`
3. `run_ai_workflow.py`
4. `gemini_enricher_v2.py`
5. `wos_standardizer.py`
6. `enhanced_converter.py`
7. `institution_enricher_v2.py`
8. `gemini_config.py`

**文档中的示例**：
- 替换为 `your-api-key-here` 或 `${GEMINI_API_KEY}`

---

### 步骤5: 测试并重新提交

```bash
# 1. 测试代码是否正常工作
python3 run_ai_workflow.py --data-dir "/path/to/test" --no-ai

# 2. 提交修改
git add .
git commit -m "security: Remove hardcoded API keys, use environment variables

BREAKING CHANGE: Users must now create a .env file with API credentials.
See .env.example for template.

Fixes: API key exposure in version history"

# 3. 推送到GitHub
git push origin main
```

---

## 📋 完整检查清单

- [ ] **撤销旧的API密钥** `sk-leomeng1997` ⭐ 最优先
- [ ] **生成新的API密钥**
- [ ] **从Git历史中删除敏感信息** (使用BFG或filter-branch)
- [ ] **Force push清理后的历史到GitHub**
- [ ] **创建 .env 文件**（基于 .env.example）
- [ ] **修改所有源文件使用环境变量**（9个文件）
- [ ] **更新文档示例**（4个文件）
- [ ] **测试代码**
- [ ] **提交并推送修改**
- [ ] **通知团队成员更新密钥**（如有）

---

## 🔒 长期安全建议

1. **永远不要硬编码密钥**
   - 使用 `.env` 文件（本地开发）
   - 使用环境变量（生产环境）
   - 使用密钥管理服务（AWS Secrets Manager, HashiCorp Vault）

2. **定期轮换API密钥**
   - 建议每3-6个月更换一次

3. **使用预提交钩子**
   - 安装 `pre-commit` 和 `detect-secrets`
   - 自动检测敏感信息

4. **启用GitHub Secret Scanning**
   - GitHub会自动检测已知格式的密钥
   - 启用通知

---

## 📞 需要帮助？

如果遇到问题，请：
1. 先撤销API密钥（最重要）
2. 然后再处理Git历史清理
3. 遇到技术问题可以查阅：
   - BFG文档: https://rtyley.github.io/bfg-repo-cleaner/
   - GitHub删除敏感数据: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository

---

**创建时间**: 2026-01-15
**创建者**: Claude Code
**状态**: ⚠️ 待处理
