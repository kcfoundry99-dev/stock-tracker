#!/bin/bash
echo "🚀 Vinyl Vault 一鍵部署"
echo "========================"
echo ""
cd /tmp/vinyl-vault

echo "步驟 1/3: 登入 GitHub"
gh auth login

echo ""
echo "步驟 2/3: 建立遠端並推送"
git remote add origin https://github.com/Kcfoundry99-dev/vinyl-vault.git 2>/dev/null || true
git push -u origin main

echo ""
echo "步驟 3/3: 啟用 GitHub Pages"
gh api repos/Kcfoundry99-dev/pages -X PUT -f source='{"branch":"main"}' --silent 2>/dev/null || \
echo "Pages 設定: 請到手動到 https://github.com/Kcfoundry99-dev/vinyl-vault/settings/pages 設定"

echo ""
echo "========================"
echo "✅ 完成！"
echo ""
echo "你的網站將在 1-2 分鐘後上線於："
echo "🔗 https://Kcfoundry99-dev.github.io/vinyl-vault/"
echo ""
echo "用手機開啟上面的網址即可使用！"
