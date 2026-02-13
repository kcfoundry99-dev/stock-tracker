#!/bin/bash
echo "🚀 Vinyl Vault 部署到 GitHub Pages"
echo "================================"
echo ""

# 初始化 git
git init
git add .
git commit -m "Initial commit: Vinyl Vault 黑膠典藏系統"

# 建立 GitHub 專案
echo ""
echo "1/3 建立 GitHub 專案..."
gh repo create vinyl-vault --public --description "黑膠唱片收藏管理系統 with AI 辨識" --disable-wiki --disable-issues

# 推送
echo ""
echo "2/3 推送到 GitHub..."
git branch -M main
gh repo set-default Kcfoundry99-dev/vinyl-vault
git push -u origin main

echo ""
echo "3/3 啟用 GitHub Pages..."
gh api repos/Kcfoundry99-dev/pages -X PUT -f source='{"branch":"main"}' --silent 2>/dev/null || true

echo ""
echo "================================"
echo "✅ 部署完成！"
echo ""
echo "你的 Vinyl Vault 網站將在 1-2 分鐘後上線於："
echo "🔗 https://Kcfoundry99-dev.github.io/vinyl-vault/"
echo ""
echo "請到手機瀏覽器開啟上面的網址測試！"
