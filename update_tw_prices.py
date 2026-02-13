#!/usr/bin/env python3
"""台股股價更新器 - 使用 curl 直接抓取 Yahoo Finance"""
import subprocess
import json
import re
from datetime import datetime

# 台股代碼
TICKER_MAP = {
    '元大台灣50': '0050.TW',
    '富邦台50': '006208.TW',
    '國泰臺灣加權正2': '00631L.TW',
    '國泰10Y+金融債': '00717B.TW',
    '富喬': '1815.TW',
    '超豐': '2441.TW',
    '泰鼎-KY': '4927.TW',
    '榮科': '4989.TW',
    '德宏': '5471.TW'
}

def get_price_yahoo(ticker):
    """從 Yahoo Finance 取得股價"""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=1d"
    try:
        result = subprocess.run(['curl', '-s', '-L', '-A', 'Mozilla/5.0', url], 
                              capture_output=True, text=True, timeout=10)
        data = json.loads(result.stdout)
        if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
            return data['chart']['result'][0]['meta']['regularMarketPrice']
    except:
        pass
    return None

def get_taiwan_stock_price():
    """取得台股股價"""
    print("=" * 50)
    print("📈 台股股價更新")
    print("=" * 50)
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    prices = {}
    for name, ticker in TICKER_MAP.items():
        price = get_price_yahoo(ticker)
        if price:
            prices[name] = round(price, 2)
            print(f"✅ {name}: ${price:.2f}")
        else:
            print(f"❌ {name}: 無法取得")
    
    # 輸出 Python 格式供 HTML 使用
    print("\n" + "=" * 50)
    print("更新到 HTML 檔案...")
    return prices

if __name__ == '__main__':
    get_taiwan_stock_price()
