# 📈 股票追蹤與分析系統

美觀的股票投資組合追蹤儀表板，支援每日自動更新、技術分析、買賣建議。

![Dashboard Preview](https://via.placeholder.com/800x400/1a1a2e/ffffff?text=Stock+Tracker+Dashboard)

## ✨ 功能特色

| 功能 | 說明 |
|------|------|
| 📊 **美觀儀表板** | 深色主題、漸層設計、互動式圖表 |
| 💰 **投資組合追蹤** | 總市值、損益、報酬率一目了然 |
| 🔄 **每日自動更新** | 9:00、13:30、23:00 自動抓取股價 |
| 📈 **技術分析** | MA、RSI、MACD、布林通道 |
| 🎯 **買賣建議** | 根據技術指標給出 BUY/HOLD/SELL 建議 |
| 🏆 **績效排名** | 顯示表現最佳/最差股票 |
| 📱 **響應式設計** | 手機、平板、桌機都能用 |

## 🚀 快速開始

### 1. 安裝 Docker

```bash
# macOS
brew install --cask docker

# Linux
curl -fsSL https://get.docker.com | sh

# Windows
# 下載 Docker Desktop
```

### 2. 啟動服務

```bash
cd stock-tracker

# 建立並啟動所有服務
docker-compose up -d

# 查看狀態
docker-compose ps

# 查看日誌
docker-compose logs -f
```

### 3. 打開儀表板

瀏覽器打開：
```
http://localhost:80
```

## 📋 新增持股

1. 點擊右上角「**新增持股**」
2. 輸入股票代碼（台股：2330，美股：AAPL）
3. 輸入股數和平均成本
4. 點擊「**新增**」

系統會自動：
- ✅ 抓取最新股價
- ✅ 計算市值和損益
- ✅ 執行技術分析
- ✅ 產生買賣建議

## 🔧 技術架構

```
┌─────────────────────────────────────────────────────┐
│                   前端 (HTML/JS)                      │
│         - Tailwind CSS + ApexCharts                  │
│         - 響應式設計                                  │
└───────────────────┬─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│              Nginx 反向代理                           │
│         - 負載均衡                                    │
│         - SSL termination (production)               │
└───────────────────┬─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│               Flask API 伺服器                       │
│         - 股票資料抓取 (yfinance)                     │
│         - 技術分析 (Pandas/TA)                        │
│         - 排程任務 (Schedule)                         │
└───────────────────┬─────────────────────────────────┘
                    │
         ┌─────────┴─────────┐
         ▼                   ▼
┌───────────────┐    ┌───────────────┐
│   PostgreSQL   │    │     Redis     │
│   (資料儲存)   │    │   (快取)      │
└───────────────┘    └───────────────┘
```

## 📁 目錄結構

```
stock-tracker/
├── docker-compose.yml     # Docker 編排配置
├── Dockerfile            # Flask App 映像檔
├── README.md             # 本文件
├── app/
│   ├── app.py           # Flask 主程式
│   └── requirements.txt  # Python 依賴
├── frontend/
│   └── index.html       # 前端頁面
└── data/                 # 資料 volume
```

## 📊 技術指標說明

| 指標 | 說明 | 買入條件 | 賣出條件 |
|------|------|----------|----------|
| **MA20** | 20日均線 | 股價站上 MA20 | 股價跌破 MA20 |
| **RSI** | 相對強弱指標 | RSI < 30 (超賣) | RSI > 70 (超買) |
| **MACD** | 移動平均收斂 | MACD 上穿 Signal | MACD 下穿 Signal |
| **成交量** | 成交量 | 放量上漲 | 放量下跌 |

## 🔧 配置選項

### 環境變數

建立 `.env` 檔案：

```env
# 資料庫
DATABASE_URL=postgresql://stock:stock123@db:5432/stocktracker

# Redis
REDIS_URL=redis://redis:6379

# 時區
TZ=Asia/Taipei
```

### 調整排程

編輯 `app/app.py` 中的 `run_scheduler()` 函數：

```python
def run_scheduler():
    # 台股開盤前
    schedule.every().day.at("09:00").do(scheduled_update)
    # 台股收盤後
    schedule.every().day.at("13:30").do(scheduled_update)
    # 美股收盤後
    schedule.every().day.at("23:00").do(scheduled_update)
    
    while True:
        schedule.run_pending()
        time.sleep(60)
```

## 🎯 買賣建議邏輯

```
分數 >= 3:  STRONG_BUY  (強力買入)
分數 >= 1:  BUY         (買入)
分數 <= -3: STRONG_SELL (強力賣出)
分數 <= -1: SELL        (賣出)
其他:       HOLD        (持有)
```

評分標準：
- ✅ 股價 > MA20: +1 分
- ✅ RSI < 30: +2 分
- ✅ RSI > 70: -2 分
- ✅ MACD > Signal: +1 分
- ✅ 放量上漲: +1 分
- ✅ 10日漲幅 > 10%: +1 分

## 🛠️ 維護指令

```bash
# 查看服務狀態
docker-compose ps

# 重啟服務
docker-compose restart

# 查看日誌
docker-compose logs -f stock-tracker

# 更新系統
docker-compose pull
docker-compose up -d

# 停止服務
docker-compose down

# 清除所有資料 (慎用！)
docker-compose down -v
```

## 📱 API 接口

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/api/health` | 健康檢查 |
| GET | `/api/stocks` | 取得所有股票 |
| POST | `/api/stocks` | 新增股票 |
| GET | `/api/positions` | 取得所有部位 |
| POST | `/api/positions` | 新增部位 |
| GET | `/api/portfolio/summary` | 投資組合總覽 |
| POST | `/api/portfolio/update` | 更新所有部位 |
| GET | `/api/analyze/<symbol>` | 分析單一股票 |
| GET | `/api/recommendations` | 買賣建議 |

## 🔒 生產環境部署

### 使用 Nginx + SSL

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://stock-tracker:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 使用 systemd 開機啟動

建立 `/etc/systemd/system/stock-tracker.service`：

```ini
[Unit]
Description=Stock Tracker Service
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
WorkingDirectory=/path/to/stock-tracker
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

## 📝 更新日誌

### v1.0.0 (2026-02-11)
- ✨ 初始版本
- 📊 美觀的儀表板介面
- 📈 技術分析指標
- 🎯 買賣建議系統
- 🔄 每日自動更新

## 🤝 授權

MIT License

## 📧 聯繫

有問題請開 Issue 或聯繫維護者。

---

**Happy Investing! 🚀📈**
