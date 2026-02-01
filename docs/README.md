# MultiDatabase 文档目录

本目录包含项目的所有文档。

---

## 📁 目录结构

### `/` 根目录
主要文档：
- **README.md** - 项目主文档 ⭐
- **CLAUDE.md** - 开发指南和架构说明
- **CHANGELOG.md** - 完整更新历史
- **PROJECT_FINAL_STATUS.md** - 项目最终状态 ⭐ NEW

### `docs/` 文档目录

#### `docs/release/` - 发布相关文档
- **CHANGELOG_v5.0.0.md** - v5.0.0完整更新日志
- **GITHUB_RELEASE_v5.0.0.md** - GitHub发布说明
- **RELEASE_STATUS_v5.0.0.md** - 发布状态
- **RELEASE_SUMMARY_v5.0.0.md** - 发布摘要

#### `docs/security/` - 安全相关文档
- **SECURITY_ALERT_API_KEY_LEAK.md** - 安全警告详情
- **SECURITY_FIX_COMPLETED.md** - 安全修复报告
- **API_KEY_LEAK_RESPONSE.md** - 应急响应报告
- **QUICK_FIX_GUIDE.md** - 快速修复指南

#### `docs/internal/` - 内部文档
- **GITHUB_PUSH_GUIDE.md** - GitHub推送指南
- **QUICK_PUSH_COMMANDS.md** - 快速命令参考
- **push_to_github.sh** - 自动推送脚本

#### `docs/` 用户指南（中文）
- **快速使用指南.md** - 新手快速入门
- **使用指南.md** - 详细使用说明
- **WOS标准化说明.md** - WOS格式标准化说明

#### `docs/` 技术文档
- **API_RATE_LIMIT_FIX.md** - API速率限制修复
- **BUGFIX_v4.5.1.md** - v4.5.1 bug修复
- **GUI_BUGFIX_v4.5.2.md** - GUI修复
- **PLOT_BUGFIX_v4.5.3.md** - 绘图修复
- **WOS_FORMAT_ALIGNMENT.md** - WOS格式对齐
- **C1_COUNTRY_EXTRACTION_FIX.md** - C1国家提取修复
- **WORKFLOW_UPDATE_v4.5.0.md** - 工作流更新
- **PROJECT_STRUCTURE.md** - 项目结构说明

---

## 📖 文档阅读顺序

### 新用户
1. **README.md** - 了解项目概况
2. **docs/快速使用指南.md** - 快速入门
3. **PROJECT_FINAL_STATUS.md** - 项目当前状态

### 开发者
1. **CLAUDE.md** - 开发架构
2. **CHANGELOG.md** - 历史更新
3. **docs/release/CHANGELOG_v5.0.0.md** - 最新改进
4. **docs/security/** - 安全相关

### 故障排查
1. **docs/security/QUICK_FIX_GUIDE.md** - 快速修复
2. **docs/API_RATE_LIMIT_FIX.md** - API问题
3. **docs/BUGFIX_v4.5.1.md** - Bug修复

---

## 🔍 查找特定信息

| 需求 | 文档 |
|------|------|
| 快速开始 | README.md, docs/快速使用指南.md |
| API配置 | .env.example, docs/security/ |
| 版本历史 | CHANGELOG.md, docs/release/ |
| 安全问题 | docs/security/ |
| 开发指南 | CLAUDE.md |
| 项目状态 | PROJECT_FINAL_STATUS.md |

---

**更新时间**: 2026-01-15
**版本**: v5.0.0
