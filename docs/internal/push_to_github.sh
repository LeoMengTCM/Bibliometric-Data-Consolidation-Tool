#!/bin/bash
# MultiDatabase v5.0.0 - 一键推送脚本
#
# 使用方法：
#   chmod +x push_to_github.sh
#   ./push_to_github.sh

set -e  # 遇到错误立即停止

echo "🚀 开始推送 MultiDatabase v5.0.0 到 GitHub..."
echo ""

# 步骤 1: 推送 main 分支
echo "📤 步骤 1/3: 推送 main 分支..."
git push origin main
echo "✅ Main 分支推送成功！"
echo ""

# 步骤 2: 推送 v5.0.0 标签
echo "🏷️  步骤 2/3: 推送 v5.0.0 标签..."
git push origin v5.0.0
echo "✅ 标签推送成功！"
echo ""

# 步骤 3: 提示创建 Release
echo "📝 步骤 3/3: 创建 GitHub Release"
echo ""
echo "请选择以下方式之一创建 Release："
echo ""
echo "方式 A - 使用 GitHub CLI (推荐):"
echo "----------------------------------------"
echo "gh auth login"
echo "gh release create v5.0.0 \\"
echo "  --title \"MultiDatabase v5.0.0 - Stable Release\" \\"
echo "  --notes-file GITHUB_RELEASE_v5.0.0.md"
echo ""
echo "方式 B - 使用网页界面:"
echo "----------------------------------------"
echo "1. 访问: https://github.com/LeoMengTCM/scopus-wos-tools/releases/new"
echo "2. 选择标签: v5.0.0"
echo "3. 标题: MultiDatabase v5.0.0 - Stable Release"
echo "4. 描述: 复制 GITHUB_RELEASE_v5.0.0.md 内容"
echo "5. 点击 'Publish release'"
echo ""
echo "🎉 推送完成！"
echo "🔗 查看仓库: https://github.com/LeoMengTCM/scopus-wos-tools"
