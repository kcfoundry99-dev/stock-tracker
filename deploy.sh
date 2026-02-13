#!/bin/bash
echo "🎵 Vinyl Vault 部署到網路"
echo ""

# 檢查是否安裝 vercel
if ! command -v vercel &> /dev/null; then
    echo "安裝 Vercel 中..."
    npm i -g vercel
fi

echo "正在部署..."
vercel --prod

echo ""
echo "部署完成後會給你一個網址，例如："
echo "https://vinyl-vault-xxx.vercel.app"
echo ""
echo "那個網址可以從世界任何地方訪問！"
