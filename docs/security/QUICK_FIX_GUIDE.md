# 🚨 紧急操作指南 - API密钥泄露

**⏰ 预计时间**: 15分钟
**🔴 紧急程度**: HIGH

---

## ⚡ 立即执行（5分钟）

### 1️⃣ 撤销API密钥（最重要！）⭐

**前往API提供商网站撤销密钥**：
```
密钥: sk-leomeng1997
URL: https://gptload.drmeng.top
```

1. 登录API管理后台
2. 找到密钥列表
3. **删除/撤销** `sk-leomeng1997`
4. **生成新密钥**（保存好，稍后使用）

> ⚠️ 为什么要先做这个？因为密钥已在GitHub公开，任何人都可能复制使用！

---

## 🛠️ 清理代码（10分钟）

### 2️⃣ 自动替换硬编码密钥

```bash
cd /Users/menglinghan/Desktop/MultiDatabase

# 运行自动替换脚本
python3 remove_hardcoded_keys.py
```

这会自动修改8个Python文件，将硬编码密钥改为环境变量。

---

### 3️⃣ 创建 .env 配置文件

```bash
# 复制模板
cp .env.example .env

# 编辑文件，填入新的API密钥
nano .env
```

`.env` 文件内容：
```bash
GEMINI_API_KEY=你的新密钥
GEMINI_API_URL=https://gptload.drmeng.top/proxy/bibliometrics/v1beta
GEMINI_MODEL=gemini-2.5-flash
```

---

### 4️⃣ 测试代码

```bash
# 快速测试（不调用AI）
python3 run_ai_workflow.py --data-dir "/path/to/test" --no-ai

# 如果测试通过，继续下一步
```

---

### 5️⃣ 提交并推送

```bash
# 提交修改
git add .
git commit -m "security: Remove hardcoded API keys, use environment variables

BREAKING CHANGE: Users must now create a .env file with API credentials.
See .env.example for template."

# 推送到GitHub
git push origin main
```

---

## 🧹 清理Git历史（可选，但推荐）

如果你想彻底删除历史中的密钥记录：

### 选项A: 使用BFG（推荐）

```bash
# 1. 安装BFG
brew install bfg

# 2. 运行清理脚本
./clean_git_history.sh

# 3. Force push
git push origin main --force
git push origin --tags --force
```

### 选项B: 创建新的干净仓库

如果Git历史很乱，可以考虑创建新仓库：

```bash
# 1. 删除.git目录
rm -rf .git

# 2. 重新初始化
git init
git add .
git commit -m "Initial commit - v5.0.0 clean"

# 3. 推送到GitHub（需要force）
git remote add origin git@github.com:LeoMengTCM/scopus-wos-tools.git
git push origin main --force
```

---

## ✅ 完成检查清单

- [ ] ⭐ **撤销旧API密钥** `sk-leomeng1997`
- [ ] **生成新API密钥**
- [ ] **运行** `remove_hardcoded_keys.py`
- [ ] **创建** `.env` 文件
- [ ] **测试代码**正常工作
- [ ] **提交并推送**修改
- [ ] （可选）**清理Git历史**

---

## 📚 相关文档

- **详细说明**: `SECURITY_ALERT_API_KEY_LEAK.md`
- **自动化脚本**: `remove_hardcoded_keys.py`
- **历史清理**: `clean_git_history.sh`
- **配置模板**: `.env.example`

---

## 💡 避免将来再次发生

1. ✅ `.gitignore` 已更新，`.env` 不会被提交
2. ✅ `.env.example` 模板已创建
3. ⭐ **养成习惯**: 永远不要在代码中硬编码密钥！

---

**创建时间**: 2026-01-15
**状态**: ⚠️ 待执行
