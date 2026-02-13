#!/bin/bash
echo "🎵 Vinyl Vault 部署到 GitHub Pages"
echo ""

# 詢問使用者
read -p "請輸入你的 GitHub 用戶名: " GH_USER

if [ -z "$GH_USER" ]; then
    echo "錯誤：請輸入 GitHub 用戶名"
    exit 1
fi

echo ""
echo "1. 建立 vinyl-vault 資料夾..."
mkdir -p /tmp/vinyl-vault
cp vinyl_vault.html /tmp/vinyl-vault/
cp README.md /tmp/vinyl-vault/
cp .nojekyll /tmp/vinyl-vault/

echo "2. 建立 CNAME 和部署腳本..."
cd /tmp/vinyl-vault

# 建立 deploy.sh
cat > deploy.sh << 'DEPLOY'
#!/bin/bash
echo "🚀 部署到 GitHub Pages..."
echo ""

if [ -z "$1" ]; then
    echo "使用方法: ./deploy.sh <commit-message>"
    echo "範例: ./deploy.sh 'Update vinyl vault'"
    exit 1
fi

git init
git add .
git commit -m "$1"
git branch -M main
git remote add origin https://github.com/$USER/vinyl-vault.git
git push -u origin main --force

echo ""
echo "✅ 部署完成！"
echo "請到 https://github.com/$USER/vinyl-vault/settings/pages"
echo "確認 Source 設定為 'main' 然後 Save"
echo ""
echo "你的網站將會在幾分鐘後上線於："
echo "https://$USER.github.io/vinyl-vault/"
DEPLOY

chmod +x deploy.sh

echo ""
echo "✅ 準備完成！"
echo ""
echo "請執行以下指令："
echo ""
echo "cd /tmp/vinyl-vault"
echo "./deploy.sh 'Initial commit'"
echo ""
echo "或者你想讓我繼續嗎？(y/n)"
