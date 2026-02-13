#!/bin/bash

# 股票追蹤系統 - 快速啟動腳本
# Stock Tracker - Quick Start Script

set -e

echo "📈 股票追蹤系統啟動腳本"
echo "=========================="

# 檢查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ 錯誤: 請先安裝 Docker"
    echo "   macOS: brew install --cask docker"
    echo "   Linux: curl -fsSL https://get.docker.com | sh"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ 錯誤: 請先安裝 Docker Compose"
    exit 1
fi

# 進入專案目錄
cd "$(dirname "$0")"
echo "📁 工作目錄: $(pwd)"

# 檢查必要檔案
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ 錯誤: docker-compose.yml 不存在"
    exit 1
fi

echo ""
echo "🏗️  建構映像檔..."
docker-compose build

echo ""
echo "🚀 啟動服務..."
if docker compose version &> /dev/null; then
    docker compose up -d
else
    docker-compose up -d
fi

echo ""
echo "⏳ 等待服務啟動..."
sleep 10

echo ""
echo "✅ 服務狀態:"
if docker compose version &> /dev/null; then
    docker compose ps
else
    docker-compose ps
fi

echo ""
echo "🌐 請打開瀏覽器存取:"
echo "   http://localhost:80"
echo ""
echo "📊 API 接口:"
echo "   http://localhost:5000/api/portfolio/summary"
echo ""
echo "💡 使用說明:"
echo "   1. 點擊「新增持股」加入你的股票"
echo "   2. 系統會自動抓取股價並分析"
echo "   3. 查看「買賣建議」決定下一步"
echo ""
echo "🔧 管理指令:"
echo "   查看日誌: docker-compose logs -f"
echo "   重啟服務: docker-compose restart"
echo "   停止服務: docker-compose down"
