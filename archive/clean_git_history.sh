#!/bin/bash
# Git历史清理脚本 - 删除API密钥
# 使用BFG Repo Cleaner清理敏感信息

set -e  # 遇到错误立即退出

echo "🚨 Git历史清理脚本 - 删除API密钥"
echo "================================"
echo ""

# 检查BFG是否安装
if ! command -v bfg &> /dev/null; then
    echo "❌ BFG Repo Cleaner 未安装"
    echo ""
    echo "请先安装 BFG:"
    echo "  brew install bfg"
    echo ""
    exit 1
fi

# 检查是否在Git仓库中
if [ ! -d .git ]; then
    echo "❌ 当前目录不是Git仓库"
    exit 1
fi

echo "📋 准备清理以下敏感信息:"
echo "  - API密钥: sk-leomeng1997"
echo "  - API URL: gptload.drmeng.top"
echo ""

# 创建备份
echo "📦 创建备份..."
BACKUP_DIR="../MultiDatabase_backup_$(date +%Y%m%d_%H%M%S)"
cp -r . "$BACKUP_DIR"
echo "✅ 备份已创建: $BACKUP_DIR"
echo ""

# 创建密钥替换文件
echo "📝 创建密钥替换文件..."
cat > secrets.txt << EOF
sk-leomeng1997==>YOUR_API_KEY_HERE
gptload.drmeng.top==>YOUR_API_DOMAIN_HERE
EOF
echo "✅ 替换规则已创建"
echo ""

# 确认操作
echo "⚠️  警告: 此操作将重写Git历史，无法撤销！"
echo ""
read -p "确定要继续吗? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ 操作已取消"
    rm secrets.txt
    exit 0
fi

echo ""
echo "🔧 开始清理Git历史..."
echo ""

# 使用BFG清理
bfg --replace-text secrets.txt --no-blob-protection .

# 清理引用
echo ""
echo "🧹 清理Git引用..."
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 删除临时文件
rm secrets.txt

echo ""
echo "✅ Git历史清理完成！"
echo ""
echo "📋 下一步操作:"
echo "1. 检查修改: git log --oneline -10"
echo "2. Force push到GitHub:"
echo "   git push origin main --force"
echo "   git push origin --tags --force"
echo ""
echo "⚠️  重要提醒:"
echo "- 立即前往API提供商撤销旧密钥 sk-leomeng1997"
echo "- 生成新的API密钥"
echo "- 创建 .env 文件填入新密钥"
echo "- 通知所有协作者更新仓库"
echo ""
