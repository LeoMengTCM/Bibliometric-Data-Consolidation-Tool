# API密钥泄露应急响应报告

**发现时间**: 2026-01-15
**响应时间**: 立即
**状态**: ✅ 已准备好清理工具

---

## 📊 问题总结

### 发现的问题
在准备推送v5.0.0到GitHub时，发现以下敏感信息被硬编码：

- **API密钥**: `sk-leomeng1997`
- **API URL**: `https://gptload.drmeng.top/proxy/bibliometrics/v1beta`
- **影响文件**: 13个（9个源文件 + 4个文档）
- **Git状态**: 已推送到GitHub远程仓库

### 受影响的源文件
1. `enhanced_converter_batch_v2.py:49-50`
2. `wos_standardizer_batch.py:622-623`
3. `run_ai_workflow.py:336-337`
4. `gemini_enricher_v2.py:778-779`
5. `wos_standardizer.py:371-372`
6. `enhanced_converter.py:47-48`
7. `institution_enricher_v2.py:396, 402-403`
8. `gemini_config.py:40, 197-198`

### 受影响的文档
9. `CLAUDE.md:535-536`
10. `docs/快速使用指南.md`
11. `docs/WOS标准化说明.md`
12. `docs/使用指南.md`

---

## ✅ 已完成的响应措施

### 1. 创建安全工具

#### 📄 `.env.example` - 环境变量模板
- 用途: 提供API配置示例
- 位置: `/Users/menglinghan/Desktop/MultiDatabase/.env.example`

#### 📝 `.gitignore` - 已更新
- 新增规则: 忽略 `.env`, `config/secrets.json`, `*_secret.json`
- 确保将来不会提交敏感文件

#### 🔧 `remove_hardcoded_keys.py` - 自动替换脚本
- 功能: 自动将硬编码密钥改为环境变量
- 影响: 8个Python源文件
- 使用: `python3 remove_hardcoded_keys.py`

#### 🧹 `clean_git_history.sh` - Git历史清理脚本
- 功能: 使用BFG从Git历史中删除敏感信息
- 使用: `./clean_git_history.sh`

### 2. 创建文档

#### 📚 `SECURITY_ALERT_API_KEY_LEAK.md` - 详细安全警告
- 内容: 完整的问题描述、影响范围、解决步骤
- 8.5KB, 包含所有技术细节

#### ⚡ `QUICK_FIX_GUIDE.md` - 快速修复指南
- 内容: 15分钟快速操作指南
- 包含完整检查清单

#### 📋 `API_KEY_LEAK_RESPONSE.md` - 本报告
- 内容: 应急响应总结

---

## 🚨 用户需要立即执行的步骤

### ⏰ 第1步: 撤销API密钥（5分钟）⭐ 最优先

**必须立即执行！**

1. 登录: `https://gptload.drmeng.top` 或你的API管理后台
2. 找到密钥: `sk-leomeng1997`
3. **删除/撤销**此密钥
4. **生成新密钥**并保存

> ⚠️ 为什么最优先？因为密钥已在GitHub公开，可能已被他人复制使用！

---

### 🛠️ 第2步: 清理代码（5分钟）

```bash
cd /Users/menglinghan/Desktop/MultiDatabase

# 1. 运行自动替换脚本
python3 remove_hardcoded_keys.py

# 2. 创建.env文件
cp .env.example .env

# 3. 编辑.env，填入新的API密钥
nano .env
```

`.env` 文件内容：
```bash
GEMINI_API_KEY=你刚生成的新密钥
GEMINI_API_URL=https://gptload.drmeng.top/proxy/bibliometrics/v1beta
GEMINI_MODEL=gemini-2.5-flash
```

---

### ✅ 第3步: 测试并提交（3分钟）

```bash
# 1. 快速测试
python3 run_ai_workflow.py --data-dir "/path/to/test" --no-ai

# 2. 提交修改
git add .
git commit -m "security: Remove hardcoded API keys, use environment variables"

# 3. 推送到GitHub
git push origin main
```

---

### 🧹 第4步: 清理Git历史（可选，2分钟）

**方法A: 使用BFG（推荐）**
```bash
# 1. 安装BFG
brew install bfg

# 2. 运行清理脚本
./clean_git_history.sh

# 3. Force push
git push origin main --force
git push origin --tags --force
```

**方法B: 不清理历史**
- 如果觉得麻烦，也可以不清理
- 只要撤销了旧密钥，风险已经大大降低

---

## 📋 完整检查清单

### 必须完成 ⭐
- [ ] **撤销旧API密钥** `sk-leomeng1997`（API提供商）
- [ ] **生成新API密钥**（API提供商）
- [ ] **运行** `python3 remove_hardcoded_keys.py`
- [ ] **创建** `.env` 文件并填入新密钥
- [ ] **测试**代码正常工作
- [ ] **提交并推送**到GitHub

### 可选（但推荐）
- [ ] **安装BFG**: `brew install bfg`
- [ ] **清理Git历史**: `./clean_git_history.sh`
- [ ] **Force push**: `git push origin main --force`

---

## 📊 创建的文件清单

| 文件名 | 大小 | 用途 |
|--------|------|------|
| `.env.example` | 0.3KB | 环境变量模板 |
| `.gitignore` | +0.1KB | 已更新忽略规则 |
| `remove_hardcoded_keys.py` | 3.8KB | 自动替换脚本 |
| `clean_git_history.sh` | 2.0KB | Git历史清理脚本 |
| `SECURITY_ALERT_API_KEY_LEAK.md` | 8.5KB | 详细安全警告 |
| `QUICK_FIX_GUIDE.md` | 3.2KB | 快速修复指南 |
| `API_KEY_LEAK_RESPONSE.md` | 本文件 | 应急响应报告 |

**总计**: 7个新文件，~18KB文档

---

## 💡 经验教训

### 导致此问题的原因
1. **开发过程中硬编码密钥**用于快速测试
2. **未及时清理**就推送到GitHub
3. **缺少预提交检查**机制

### 将来如何避免

#### ✅ 已完成
1. ✅ 更新 `.gitignore` 忽略 `.env`
2. ✅ 创建 `.env.example` 模板
3. ✅ 提供自动化清理工具

#### 📋 建议增加
1. 使用预提交钩子 (`pre-commit`)
   ```bash
   pip install pre-commit detect-secrets
   pre-commit install
   ```

2. 启用GitHub Secret Scanning
   - Settings → Security → Secret scanning

3. 定期轮换API密钥（每3-6个月）

4. 团队培训：密钥管理最佳实践

---

## 📞 获取帮助

如果执行过程中遇到问题：

1. **查看详细文档**: `SECURITY_ALERT_API_KEY_LEAK.md`
2. **快速指南**: `QUICK_FIX_GUIDE.md`
3. **GitHub文档**: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository
4. **BFG文档**: https://rtyley.github.io/bfg-repo-cleaner/

---

## 🎯 预期结果

完成所有步骤后：
1. ✅ 旧API密钥已失效，无法被滥用
2. ✅ 代码使用环境变量，不再硬编码
3. ✅ `.env` 文件不会被提交到Git
4. ✅ （可选）Git历史已清理干净
5. ✅ 项目安全性大幅提升

---

**报告时间**: 2026-01-15
**响应级别**: 🔴 HIGH
**完成度**: ✅ 工具已准备好，等待用户执行
