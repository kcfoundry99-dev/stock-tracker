#!/usr/bin/env python3
"""
US Stock Professional Analysis Server - 台股風格
"""

import yfinance as yf
from flask import Flask, jsonify
import pandas as pd
import schedule
import time
import threading
from datetime import datetime

app = Flask(__name__)

USD_TO_TWD = 31.5

HOLDINGS = {
    'NVDA': {'shares': 150, 'avg_cost': 174.73},
    'AVGO': {'shares': 46, 'avg_cost': 345.39},
    'TSM': {'shares': 70, 'avg_cost': 284.22},
    'GOOG': {'shares': 37, 'avg_cost': 247.11},
    'AMAT': {'shares': 20, 'avg_cost': 163.00},
    'AMD': {'shares': 50, 'avg_cost': 152.56},
    'ASML': {'shares': 3, 'avg_cost': 703.00},
    'MSFT': {'shares': 7, 'avg_cost': 489.35},
    'META': {'shares': 6, 'avg_cost': 643.81},
    'AMZN': {'shares': 20, 'avg_cost': 220.01},
    'CRWD': {'shares': 5, 'avg_cost': 427.00},
    'PLTR': {'shares': 35, 'avg_cost': 175.13},
    'ITA': {'shares': 20, 'avg_cost': 194.24},
    'CAVA': {'shares': 40, 'avg_cost': 62.50},
    'COIN': {'shares': 43, 'avg_cost': 303.37},
    'CRWV': {'shares': 55, 'avg_cost': 105.17},
    'EOSE': {'shares': 200, 'avg_cost': 11.99},
    'GCL': {'shares': 2000, 'avg_cost': 1.07},
    'HIMS': {'shares': 100, 'avg_cost': 48.10},
    'ONDS': {'shares': 350, 'avg_cost': 8.82},
    'SNPS': {'shares': 30, 'avg_cost': 429.06},
    'SOFI': {'shares': 170, 'avg_cost': 24.40},
    'BABA': {'shares': 20, 'avg_cost': 169.25},
    'CHYM': {'shares': 150, 'avg_cost': 20.40},
    'TSLA': {'shares': 50, 'avg_cost': 411.84}
}

current_prices = {}
last_updated = None
analysis_data = {'analysis': {}, 'news': [], 'last_updated': None}

NEWS_DB = {
    'NVDA': [
        {'title': '輝達發布全新 AI 晶片架構', 'sentiment': 'bullish', 'term': 'long', 'reason': '新一代 AI 晶片將鞏固市場領導地位'},
        {'title': 'Blackwell 架構獲大客戶訂單', 'sentiment': 'bullish', 'term': 'short', 'reason': '短期營收將顯著成長'},
    ],
    'AVGO': [
        {'title': '博通 AI 晶片需求強勁', 'sentiment': 'bullish', 'term': 'long', 'reason': '資料中心需求持續成長'},
    ],
    'TSM': [
        {'title': '台積電上調 2024 年展望', 'sentiment': 'bullish', 'term': 'long', 'reason': 'AI 晶片需求帶動先進製程'},
        {'title': '3nm 良率超預期', 'sentiment': 'bullish', 'term': 'short', 'reason': '短期產能利用率提升'},
    ],
    'MSFT': [
        {'title': 'Azure 雲端成長加速', 'sentiment': 'bullish', 'term': 'long', 'reason': 'AI 服務帶動雲端需求'},
    ],
    'GOOG': [
        {'title': 'Google AI 模型效能提升', 'sentiment': 'bullish', 'term': 'long', 'reason': '搜尋與雲端雙引擎'},
    ],
    'AMD': [
        {'title': 'MI300X 獲大型企業採用', 'sentiment': 'bullish', 'term': 'long', 'reason': 'AI 加速器市佔提升'},
    ],
    'META': [
        {'title': 'Reels 廣告成長強勁', 'sentiment': 'bullish', 'term': 'short', 'reason': '短影音廣告營收增加'},
    ],
    'PLTR': [
        {'title': '政府合約擴大', 'sentiment': 'bullish', 'term': 'long', 'reason': 'AI 平台獲國防訂單'},
    ],
    'TSLA': [
        {'title': 'Cybertruck 開始交車', 'sentiment': 'bullish', 'term': 'short', 'reason': '新產品週期啟動'},
    ],
    'ASML': [
        {'title': 'EUV 設備需求強勁', 'sentiment': 'bullish', 'term': 'long', 'reason': '晶圓廠擴產帶動'},
    ],
    'COIN': [
        {'title': '比特幣 ETF 帶動交易量', 'sentiment': 'bullish', 'term': 'short', 'reason': '手續費收入增加'},
    ],
}

def get_stock_analysis(ticker):
    analysis = {'short_term': 'neutral', 'long_term': 'neutral', 'confidence_short': 50, 'confidence_long': 50, 'rsi': 50, 'ma20': 0, 'support': 0, 'resistance': 0}
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="60d")
        if len(hist) > 20:
            ma20 = hist['Close'].rolling(20).mean().iloc[-1]
            ma50 = hist['Close'].rolling(50).mean().iloc[-1]
            current = hist['Close'].iloc[-1]
            delta = hist['Close'].diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs.iloc[-1])) if rs.iloc[-1] > 0 else 50
            analysis['rsi'] = round(rsi, 1)
            analysis['ma20'] = round(ma20, 2)
            analysis['support'] = round(hist['Low'].tail(20).min(), 2)
            analysis['resistance'] = round(hist['High'].tail(20).max(), 2)
            if current > ma20 and rsi < 70:
                analysis['short_term'] = 'bullish'
                analysis['confidence_short'] = 70
            elif current < ma20 or rsi > 80:
                analysis['short_term'] = 'bearish'
                analysis['confidence_short'] = 70
            elif rsi < 30:
                analysis['short_term'] = 'bullish'
                analysis['confidence_short'] = 75
            if current > ma50:
                analysis['long_term'] = 'bullish'
                analysis['confidence_long'] = 75
            else:
                analysis['long_term'] = 'bearish'
                analysis['confidence_long'] = 70
    except:
        pass
    return analysis

def fetch_prices():
    global current_prices, last_updated
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Fetching prices...")
    tickers = list(HOLDINGS.keys())
    try:
        data = yf.download(tickers, period="1d", progress=False, group_by='ticker')
        for ticker in tickers:
            try:
                if len(tickers) == 1:
                    price = data['Close'].iloc[-1]
                else:
                    price = data[ticker]['Close'].iloc[-1]
                current_prices[ticker] = float(price) if pd.notna(price) else HOLDINGS[ticker]['avg_cost']
            except:
                current_prices[ticker] = HOLDINGS[ticker]['avg_cost']
        last_updated = datetime.now()
        print(f"Updated {len(current_prices)} stocks")
    except Exception as e:
        print(f"Price update failed: {e}")

def fetch_news_and_analysis():
    global analysis_data
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Fetching analysis...")
    all_news = []
    for ticker in HOLDINGS.keys():
        analysis = get_stock_analysis(ticker)
        analysis_data['analysis'][ticker] = analysis
        for n in NEWS_DB.get(ticker, []):
            all_news.append({'ticker': ticker, **n})
    all_news.sort(key=lambda x: (0 if x['sentiment'] == 'bullish' else 1))
    analysis_data['news'] = all_news[:25]
    analysis_data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def calculate_portfolio():
    total_value = 0
    total_cost = 0
    holdings_data = []
    for ticker, info in HOLDINGS.items():
        shares = info['shares']
        avg_cost = info['avg_cost']
        current_price = current_prices.get(ticker, avg_cost)
        market_value = shares * current_price
        cost_basis = shares * avg_cost
        gain_loss = market_value - cost_basis
        gain_loss_pct = (gain_loss / cost_basis) * 100 if cost_basis > 0 else 0
        total_value += market_value
        total_cost += cost_basis
        holdings_data.append({
            'ticker': ticker, 'shares': shares, 'avg_cost': avg_cost,
            'current_price': round(current_price, 2), 'cost_basis': round(cost_basis, 2),
            'market_value': round(market_value, 2), 'gain_loss': round(gain_loss, 2),
            'gain_loss_pct': round(gain_loss_pct, 2)
        })
    total_gain_loss = total_value - total_cost
    total_gain_loss_pct = (total_gain_loss / total_cost) * 100 if total_cost > 0 else 0
    holdings_data.sort(key=lambda x: x['gain_loss_pct'])
    return {
        'total_value_usd': round(total_value, 2), 'total_value_twd': round(total_value * USD_TO_TWD, 0),
        'total_cost': round(total_cost, 2), 'total_gain_loss': round(total_gain_loss, 2),
        'total_gain_loss_pct': round(total_gain_loss_pct, 2),
        'last_updated': last_updated.strftime('%Y-%m-%d %H:%M:%S') if last_updated else None,
        'holdings': holdings_data
    }

@app.route('/')
def index():
    portfolio = calculate_portfolio()
    analysis = analysis_data.get('analysis', {})
    news = analysis_data.get('news', [])
    bullish_news = [n for n in news if n['sentiment'] == 'bullish']
    
    # Stats
    short_bull = len([s for s in analysis.values() if s.get('short_term') == 'bullish'])
    short_bear = len([s for s in analysis.values() if s.get('short_term') == 'bearish'])
    long_bull = len([s for s in analysis.values() if s.get('long_term') == 'bullish'])
    long_bear = len([s for s in analysis.values() if s.get('long_term') == 'bearish'])
    
    # Top/Bottom movers
    top_gainers = sorted(portfolio['holdings'], key=lambda x: x['gain_loss_pct'], reverse=True)[:5]
    top_losers = sorted(portfolio['holdings'], key=lambda x: x['gain_loss_pct'])[:5]
    
    # Table rows
    table_rows = ''
    for h in portfolio['holdings']:
        ticker = h['ticker']
        a = analysis.get(ticker, {})
        short = a.get('short_term', 'neutral')
        long = a.get('long_term', 'neutral')
        short_emoji = '🟢' if short == 'bullish' else ('🔴' if short == 'bearish' else '⚪')
        long_emoji = '🟢' if long == 'bullish' else ('🔴' if long == 'bearish' else '⚪')
        gain_class = 'pos' if h['gain_loss'] >= 0 else 'neg'
        
        table_rows += f'''<tr>
            <td class="name">{ticker}</td>
            <td>{h['shares']}</td>
            <td>${h['avg_cost']:.2f}</td>
            <td>${h['current_price']:.2f}</td>
            <td>${h['market_value']:,.0f}</td>
            <td><span class="gain-loss {gain_class}">${h['gain_loss']:+,.0f}</span></td>
            <td><span class="gain-loss {gain_class}">{h['gain_loss_pct']:+.1f}%</span></td>
            <td>{a.get('ma20', '-'):.2f}</td>
            <td>{a.get('rsi', '-'):.0f}</td>
            <td style="text-align:center;">{short_emoji}</td>
            <td style="text-align:center;">{long_emoji}</td>
        </tr>'''
    
    # Top/Bottom movers HTML
    movers_html = ''
    for m in top_gainers:
        movers_html += f'''<div class="mover-item">
            <span class="mover-name">{m['ticker']}</span>
            <span class="positive">+{m['gain_loss_pct']:.1f}%</span>
        </div>'''
    losers_html = ''
    for m in top_losers:
        losers_html += f'''<div class="mover-item">
            <span class="mover-name">{m['ticker']}</span>
            <span class="negative">{m['gain_loss_pct']:.1f}%</span>
        </div>'''
    
    # News items
    news_html = ''
    for n in news:
        impact = 'up' if n['sentiment'] == 'bullish' else 'down'
        news_html += f'''<div class="news-item {n['sentiment']}">
            <div class="news-header">
                <span class="related-stock">{n['ticker']}</span>
                <span class="news-impact {impact}">{'利多' if impact == 'up' else '利空'}</span>
            </div>
            <div class="news-title">{n['title']}</div>
            <div class="news-reason">💡 {n['reason']}</div>
            <div class="news-footer">
                <span>⏱️ {'短期' if n['term'] == 'short' else '長期'}影響</span>
            </div>
        </div>'''
    
    # Chart data
    chart_labels = ','.join([f"'{h['ticker']}'" for h in portfolio['holdings']])
    chart_values = ','.join([str(h['market_value']) for h in portfolio['holdings']])
    chart_colors = ','.join(['#00e676' if h['gain_loss'] >= 0 else '#ff1744' for h in portfolio['holdings']])
    
    return f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>美股投資組合 + 即時新聞</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh; padding: 20px; color: #fff;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{
            background: rgba(255,255,255,0.1); backdrop-filter: blur(10px);
            border-radius: 20px; padding: 30px; margin-bottom: 20px;
            border: 1px solid rgba(255,255,255,0.2);
        }}
        .header h1 {{
            font-size: 36px;
            background: linear-gradient(90deg, #00c853, #00e676);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .last-updated {{ color: rgba(255,255,255,0.7); margin-top: 8px; }}
        
        .tabs {{ display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 20px; }}
        .tab {{
            background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2);
            color: white; padding: 12px 24px; border-radius: 12px;
            cursor: pointer; transition: all 0.3s;
        }}
        .tab:hover {{ background: rgba(255,255,255,0.2); }}
        .tab.active {{ background: linear-gradient(135deg, #00c853, #00e676); border-color: transparent; }}
        
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 20px; }}
        .stat-card {{
            background: rgba(255,255,255,0.1); backdrop-filter: blur(10px);
            border-radius: 16px; padding: 24px; text-align: center;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .stat-value {{ font-size: 32px; font-weight: bold; }}
        .stat-label {{ color: rgba(255,255,255,0.7); font-size: 14px; margin-top: 4px; }}
        .positive {{ color: #00e676; }}
        .negative {{ color: #ff1744; }}
        
        .card {{
            background: rgba(255,255,255,0.08); backdrop-filter: blur(10px);
            border-radius: 20px; padding: 30px; margin-bottom: 20px;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .card h2 {{ font-size: 22px; margin-bottom: 20px; color: #fff; display: flex; align-items: center; gap: 10px; }}
        .card h3 {{ font-size: 18px; margin-bottom: 15px; color: rgba(255,255,255,0.8); }}
        
        .table-wrapper {{ overflow-x: auto; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 14px 16px; text-align: right; border-bottom: 1px solid rgba(255,255,255,0.1); }}
        th {{ background: rgba(255,255,255,0.05); font-weight: 600; color: rgba(255,255,255,0.8); }}
        th:first-child, td:first-child {{ text-align: left; }}
        .name {{ font-weight: bold; color: #00c853; font-size: 16px; }}
        .gain-loss {{ padding: 4px 10px; border-radius: 6px; font-weight: 600; }}
        .gain-loss.pos {{ background: rgba(0,230,118,0.2); color: #00e676; }}
        .gain-loss.neg {{ background: rgba(255,23,68,0.2); color: #ff1744; }}
        
        .top-movers {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-bottom: 20px; }}
        .mover-card {{ background: rgba(255,255,255,0.08); border-radius: 16px; padding: 20px; border: 1px solid rgba(255,255,255,0.1); }}
        .mover-card h3 {{ font-size: 16px; margin-bottom: 16px; color: rgba(255,255,255,0.8); }}
        .mover-item {{ display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }}
        .mover-name {{ font-weight: 600; }}
        
        .chart-container {{ height: 350px; margin-top: 20px; }}
        
        .news-item {{
            background: rgba(255,255,255,0.05); border-radius: 12px; padding: 18px;
            border-left: 4px solid #00c853; margin-bottom: 12px;
            transition: all 0.3s;
        }}
        .news-item:hover {{ background: rgba(255,255,255,0.1); transform: translateX(5px); }}
        .news-item.bullish {{ border-left-color: #00e676; }}
        .news-item.bearish {{ border-left-color: #ff1744; }}
        .news-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 10px; }}
        .related-stock {{ font-size: 12px; color: rgba(255,255,255,0.6); background: rgba(0,200,83,0.2); padding: 4px 10px; border-radius: 6px; }}
        .news-impact {{ font-size: 12px; padding: 3px 8px; border-radius: 4px; }}
        .news-impact.up {{ background: rgba(0,230,118,0.3); color: #00e676; }}
        .news-impact.down {{ background: rgba(255,23,68,0.3); color: #ff1744; }}
        .news-title {{ font-size: 15px; font-weight: 600; color: #fff; line-height: 1.4; }}
        .news-reason {{ font-size: 13px; color: rgba(255,255,255,0.6); font-style: italic; margin-top: 8px; }}
        .news-footer {{ display: flex; gap: 15px; margin-top: 10px; color: rgba(255,255,255,0.5); font-size: 12px; }}
        
        @media (max-width: 768px) {{
            .header h1 {{ font-size: 24px; }}
            .stats {{ grid-template-columns: repeat(2, 1fr); }}
            th, td {{ padding: 10px 8px; font-size: 12px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🇺🇸 美股投資組合 + 即時分析</h1>
            <p class="last-updated">更新時間：{portfolio['last_updated']}</p>
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="showTab('portfolio')">💼 投資組合</button>
            <button class="tab" onclick="showTab('news')">📰 相關新聞</button>
        </div>
        
        <!-- 投資組合 -->
        <div id="portfolioSection">
            <div class="top-movers">
                <div class="mover-card">
                    <h3>🏆 最佳表現</h3>
                    {movers_html}
                </div>
                <div class="mover-card">
                    <h3>📉 跌幅最大</h3>
                    {losers_html}
                </div>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value positive">${portfolio['total_value_usd']:,.0f}</div>
                    <div class="stat-label">總市值 (USD)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value positive">${portfolio['total_value_twd']:,.0f}</div>
                    <div class="stat-label">總市值 (TWD)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value positive">${portfolio['total_gain_loss']:+,.0f}</div>
                    <div class="stat-label">未實現損益</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value positive">{portfolio['total_gain_loss_pct']:+.1f}%</div>
                    <div class="stat-label">報酬率</div>
                </div>
            </div>
            
            <div class="card">
                <h2>📊 持股明細 ({len(portfolio['holdings'])} 檔)</h2>
                <div class="table-wrapper">
                    <table>
                        <thead>
                            <tr>
                                <th>代號</th><th>股數</th><th>均價</th><th>現價</th><th>市值</th><th>未實現損益</th><th>報酬率</th>
                                <th>MA20</th><th>RSI</th><th style="text-align:center;">短期</th><th style="text-align:center;">長期</th>
                            </tr>
                        </thead>
                        <tbody>{table_rows}</tbody>
                    </table>
                </div>
            </div>
            
            <div class="card">
                <h2>📈 技術面摘要</h2>
                <div class="stats" style="grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));">
                    <div class="stat-card">
                        <div class="stat-value positive">{short_bull}</div>
                        <div class="stat-label">短期偏多</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value negative">{short_bear}</div>
                        <div class="stat-label">短期偏空</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value positive">{long_bull}</div>
                        <div class="stat-label">長期偏多</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value negative">{long_bear}</div>
                        <div class="stat-label">長期偏空</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2>🥧 投資配置</h2>
                <div class="chart-container"><canvas id="allocationChart"></canvas></div>
            </div>
        </div>
        
        <!-- 新聞區塊 -->
        <div id="newsSection" style="display:none;">
            <div class="card">
                <h2>📰 會影響持股的消息</h2>
                {news_html}
            </div>
        </div>
    </div>
    
    <script>
        function showTab(tab) {{
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById('portfolioSection').style.display = tab === 'portfolio' ? 'block' : 'none';
            document.getElementById('newsSection').style.display = tab === 'news' ? 'block' : 'none';
        }}
        
        // Chart
        const ctx = document.getElementById('allocationChart').getContext('2d');
        new Chart(ctx, {{
            type: 'doughnut',
            data: {{
                labels: [{chart_labels}],
                datasets: [{{
                    data: [{chart_values}],
                    backgroundColor: [{chart_colors}],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'right', labels: {{ color: '#fff' }} }}
                }}
            }}
        }});
    </script>
</body>
</html>
'''

@app.route('/api')
def api():
    return jsonify({**calculate_portfolio(), 'analysis': analysis_data.get('analysis', {}), 'news': analysis_data.get('news', [])})

def schedule_updates():
    fetch_prices()
    fetch_news_and_analysis()
    schedule.every(60).seconds.do(fetch_prices)
    schedule.every(180).seconds.do(fetch_news_and_analysis)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    fetch_prices()
    fetch_news_and_analysis()
    update_thread = threading.Thread(target=schedule_updates, daemon=True)
    update_thread.start()
    print("Server started: http://localhost:8888")
    app.run(host='0.0.0.0', port=8888, debug=False)
