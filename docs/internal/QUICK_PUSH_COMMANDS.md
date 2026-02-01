# 🚀 快速推送命令 (v5.0.0)

## 一键推送到 GitHub

```bash
# === 步骤 1: 配置远程仓库（首次） ===
git remote add origin https://github.com/YOUR_USERNAME/MultiDatabase.git
# 替换 YOUR_USERNAME 为您的 GitHub 用户名

# === 步骤 2: 推送代码和标签 ===
git push origin main && git push origin v5.0.0

# === 步骤 3: 创建 GitHub Release (CLI 方式) ===
gh auth login
gh release create v5.0.0 \
  --title "MultiDatabase v5.0.0 - Stable Release" \
  --notes-file GITHUB_RELEASE_v5.0.0.md
```

## 或者使用网页界面创建 Release

1. 访问: https://github.com/YOUR_USERNAME/MultiDatabase/releases/new
2. Tag: v5.0.0
3. Title: MultiDatabase v5.0.0 - Stable Release
4. Description: 复制 `GITHUB_RELEASE_v5.0.0.md` 内容
5. 点击 "Publish release"

---

## 检查推送结果

```bash
# 查看远程分支
git branch -r

# 查看远程标签
git ls-remote --tags origin

# 查看最新提交
git log --oneline -5
```

---

## 问题排查

### 问题 1: "fatal: remote origin already exists"
```bash
# 查看现有远程仓库
git remote -v

# 如需更改：
git remote set-url origin https://github.com/YOUR_USERNAME/MultiDatabase.git
```

### 问题 2: "Permission denied (publickey)"
```bash
# 使用 HTTPS 而不是 SSH
git remote set-url origin https://github.com/YOUR_USERNAME/MultiDatabase.git

# 或配置 SSH 密钥：
ssh-keygen -t ed25519 -C "drmengtcm@gmail.com"
# 然后将 ~/.ssh/id_ed25519.pub 添加到 GitHub
```

### 问题 3: 标签已存在
```bash
# 删除本地和远程标签
git tag -d v5.0.0
git push origin :refs/tags/v5.0.0

# 重新创建
git tag -a v5.0.0 -m "Version 5.0.0 - Stable Release"
git push origin v5.0.0
```

---

## 当前状态

✅ 本地所有更改已提交
✅ v5.0.0 标签已创建
✅ 发布文档已准备
⏳ 等待推送到 GitHub

---

**快速链接**:
- 详细推送指南: [GITHUB_PUSH_GUIDE.md](./GITHUB_PUSH_GUIDE.md)
- 发布总结: [RELEASE_SUMMARY_v5.0.0.md](./RELEASE_SUMMARY_v5.0.0.md)
- 更新日志: [CHANGELOG_v5.0.0.md](./CHANGELOG_v5.0.0.md)
