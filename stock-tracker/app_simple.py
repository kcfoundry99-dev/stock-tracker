#!/usr/bin/env python3
"""
股票追蹤系統 - 簡化版 (不需要 Docker)
"""

from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
import sqlite3
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

app = Flask(__name__)
CORS(app)
DB_FILE = 'stocks.db'

# ============== Database ==============

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS stocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT UNIQUE,
        name TEXT,
        market TEXT DEFAULT 'TW'
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS positions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stock_id INTEGER,
        shares REAL,
        avg_cost REAL,
        current_price REAL,
        current_value REAL,
        profit_loss REAL,
        profit_loss_percent REAL,
        recommendation TEXT,
        last_updated TEXT,
        FOREIGN KEY (stock_id) REFERENCES stocks (id)
    )''')
    
    conn.commit()
    conn.close()

# ============== HTML Template ==============

HTML = '''
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📈 股票追蹤儀表板</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Noto Sans TC', sans-serif; }
        .gradient-bg { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); }
        .card { background: rgba(255,255,255,0.05); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); }
    </style>
</head>
<body class="gradient-bg min-h-screen text-white">
    <header class="border-b border-gray-700/50">
        <div class="container mx-auto px-4 py-4 flex justify-between items-center">
            <h1 class="text-2xl font-bold">📈 股票追蹤儀表板</h1>
            <button onclick="refreshAll()" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg">重新整理</button>
        </div>
    </header>
    
    <main class="container mx-auto px-4 py-6">
        <!-- Summary -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div class="card rounded-xl p-6">
                <div class="text-gray-400 text-sm">總市值</div>
                <div class="text-3xl font-bold mt-2" id="totalValue">-</div>
            </div>
            <div class="card rounded-xl p-6">
                <div class="text-gray-400 text-sm">總成本</div>
                <div class="text-3xl font-bold mt-2" id="totalCost">-</div>
            </div>
            <div class="card rounded-xl p-6">
                <div class="text-gray-400 text-sm">未實現損益</div>
                <div class="text-3xl font-bold mt-2" id="totalPL">-</div>
            </div>
            <div class="card rounded-xl p-6">
                <div class="text-gray-400 text-sm">報酬率</div>
                <div class="text-3xl font-bold mt-2" id="totalPct">-</div>
            </div>
        </div>
        
        <!-- Charts -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <div class="card rounded-xl p-6">
                <h3 class="text-lg font-semibold mb-4">📊 報酬率分布</h3>
                <div id="chart1" class="h-64"></div>
            </div>
            <div class="card rounded-xl p-6">
                <h3 class="text-lg font-semibold mb-4">🎯 買賣建議</h3>
                <div id="chart2" class="h-64"></div>
            </div>
        </div>
        
        <!-- Table -->
        <div class="card rounded-xl p-6 mb-8">
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-lg font-semibold">📋 持股明細</h3>
                <button onclick="addStock()" class="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg">+ 新增</button>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead>
                        <tr class="text-left text-gray-400 border-b border-gray-700">
                            <th class="pb-3">股票</th>
                            <th class="pb-3">股數</th>
                            <th class="pb-3">成本</th>
                            <th class="pb-3">現價</th>
                            <th class="pb-3">市值</th>
                            <th class="pb-3">損益</th>
                            <th class="pb-3">報酬率</th>
                            <th class="pb-3">建議</th>
                        </tr>
                    </thead>
                    <tbody id="tableBody"></tbody>
                </table>
            </div>
        </div>
    </main>
    
    <script>
        const API = '/api';
        
        async function loadPortfolio() {
            const r = await fetch(API + '/portfolio/summary');
            const data = await r.json();
            
            const fmt = n => new Intl.NumberFormat('zh-TW', {style:'currency', currency:'TWD', minimumFractionDigits:0}).format(n);
            
            document.getElementById('totalValue').textContent = fmt(data.total_value || 0);
            document.getElementById('totalCost').textContent = fmt(data.total_cost || 0);
            
            const pl = data.total_profit_loss || 0;
            const pct = data.total_profit_loss_percent || 0;
            
            document.getElementById('totalPL').textContent = (pl>=0?'+':'') + fmt(pl);
            document.getElementById('totalPL').className = 'text-3xl font-bold mt-2 ' + (pl>=0?'text-green-400':'text-red-400');
            
            document.getElementById('totalPct').textContent = (pct>=0?'+':'') + pct.toFixed(2) + '%';
            document.getElementById('totalPct').className = 'text-3xl font-bold mt-2 ' + (pct>=0?'text-green-400':'text-red-400');
            
            updateCharts(data);
            updateTable(data.positions || []);
        }
        
        function updateCharts(data) {
            const pos = (data.positions || []).filter(p => p.profit_loss_percent !== undefined)
                .sort((a,b) => b.profit_loss_percent - a.profit_loss_percent);
            
            new ApexCharts(document.querySelector("#chart1"), {
                series: [{ data: pos.slice(0,10).map(p => p.profit_loss_percent) }],
                chart: { type: 'bar', height: 250, background: 'transparent', foreColor: '#9ca3af' },
                plotOptions: { bar: { borderRadius: 4, horizontal: true, distributed: true } },
                colors: pos.slice(0,10).map(p => p.profit_loss_percent >= 0 ? '#10b981' : '#ef4444'),
                xaxis: { categories: pos.slice(0,10).map(p => p.stock?.symbol || '-'), labels: { formatter: v => v.toFixed(1)+'%' } },
                legend: { show: false },
                dataLabels: { enabled: true, formatter: v => v.toFixed(1)+'%' }
            }).render();
            
            const recs = {BUY:0, HOLD:0, SELL:0};
            (data.positions || []).forEach(p => { recs[p.recommendation] = (recs[p.recommendation]||0) + 1 });
            
            new ApexCharts(document.querySelector("#chart2"), {
                series: Object.values(recs),
                labels: Object.keys(recs).map(k => ({BUY:'買入',HOLD:'持有',SELL:'賣出'})[k]||k),
                chart: { type: 'donut', height: 250, background: 'transparent' },
                colors: ['#10b981', '#f59e0b', '#ef4444'],
                plotOptions: { pie: { donut: { size: '70%' } } },
                legend: { position: 'bottom' },
                dataLabels: { enabled: false }
            }).render();
        }
        
        function updateTable(positions) {
            const tbody = document.getElementById('tableBody');
            if (!positions.length) {
                tbody.innerHTML = '<tr><td colspan="8" class="py-8 text-center text-gray-500">尚無持股</td></tr>';
                return;
            }
            
            tbody.innerHTML = positions.map(p => {
                const pl = p.profit_loss_percent || 0;
                const recMap = {BUY:'買入',HOLD:'持有',SELL:'賣出','STRONG_BUY':'強力買入','STRONG_SELL':'強力賣出'};
                const recColor = {BUY:'bg-green-500/20 text-green-400',HOLD:'bg-yellow-500/20 text-yellow-400',SELL:'bg-red-500/20 text-red-400'}[p.recommendation]||'bg-gray-500/20';
                
                return `<tr class="border-b border-gray-800 hover:bg-white/5">
                    <td class="py-3"><div class="font-semibold">${p.stock?.symbol||'-'}</div><div class="text-sm text-gray-500">${p.stock?.name||''}</div></td>
                    <td class="py-3">${p.shares?.toLocaleString()}</td>
                    <td class="py-3">$${p.avg_cost?.toFixed(2)}</td>
                    <td class="py-3 font-semibold">$${p.current_price?.toFixed(2)}</td>
                    <td class="py-3">$${p.current_value?.toLocaleString()}</td>
                    <td class="py-3 ${pl>=0?'text-green-400':'text-red-400'}">${pl>=0?'+':''}${p.profit_loss?.toLocaleString(undefined,{minimumFractionDigits:0,maximimFractionDigits:0})}</td>
                    <td class="py-3 ${pl>=0?'text-green-400':'text-red-400'}">${pl>=0?'+':''}${pl.toFixed(2)}%</td>
                    <td class="py-3"><span class="px-2 py-1 rounded text-xs ${recColor}">${recMap[p.recommendation]||p.recommendation||'-'}</span></td>
                </tr>`;
            }).join('');
        }
        
        async function refreshAll() {
            await fetch(API+'/portfolio/update', {method:'POST'});
            loadPortfolio();
        }
        
        async function addStock() {
            const symbol = prompt('股票代碼 (例如: 2330 或 AAPL):');
            if (!symbol) return;
            const shares = parseFloat(prompt('股數:'));
            const cost = parseFloat(prompt('平均成本:'));
            
            await fetch(API+'/stocks', {method:'POST', headers:{'Content-Type':'application/json'},
                body: JSON.stringify({symbol: symbol.toUpperCase(), market: symbol.match(/^[0-9]+$/)?'TW':'US'})});
            await fetch(API+'/positions', {method:'POST', headers:{'Content-Type':'application/json'},
                body: JSON.stringify({symbol: symbol.toUpperCase(), shares, avg_cost: cost})});
            
            refreshAll();
        }
        
        document.addEventListener('DOMContentLoaded', loadPortfolio);
        setInterval(refreshAll, 5*60*1000);
    </script>
</body>
</html>
'''

# ============== Analysis ==============

def calculate_indicators(df):
    if df is None or len(df) < 20:
        return df
    
    df['MA20'] = df['Close'].rolling(20).mean()
    df['MA60'] = df['Close'].rolling(60).mean()
    
    exp1, exp2 = df['Close'].ewm(span=12, adjust=False).mean(), df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    delta = df['Close'].diff()
    gain, loss = delta.where(delta > 0, 0).rolling(14).mean(), (-delta.where(delta < 0, 0)).rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + gain / loss))
    
    return df

def get_recommendation(df, price):
    if df is None or len(df) < 1:
        return 'HOLD'
    
    score = 0
    latest = df.iloc[-1]
    
    if price > latest.get('MA20', price): score += 1
    else: score -= 1
    
    rsi = latest.get('RSI', 50)
    if rsi < 30: score += 2
    elif rsi > 70: score -= 2
    elif rsi < 50: score -= 1
    else: score += 1
    
    if latest.get('MACD', 0) > latest.get('Signal', 0): score += 1
    else: score -= 1
    
    if score >= 3: return 'STRONG_BUY'
    if score >= 1: return 'BUY'
    if score <= -3: return 'STRONG_SELL'
    if score <= -1: return 'SELL'
    return 'HOLD'

def update_price(symbol, market='TW'):
    try:
        ticker = f"{symbol}.TW" if market == 'TW' else symbol
        stock = yf.Ticker(ticker)
        price = stock.info.get('currentPrice', stock.info.get('regularMarketPrice'))
        if price:
            return price
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
    return None

# ============== API Routes ==============

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'time': datetime.now().isoformat()})

@app.route('/api/stocks', methods=['GET', 'POST'])
def stocks():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    if request.method == 'POST':
        data = request.json
        c.execute('INSERT OR IGNORE INTO stocks (symbol, name, market) VALUES (?, ?, ?)',
                  (data['symbol'], data.get('name', ''), data.get('market', 'TW')))
        conn.commit()
        return jsonify({'status': 'ok'}), 201
    
    c.execute('SELECT * FROM stocks')
    stocks = [{'id': r[0], 'symbol': r[1], 'name': r[2], 'market': r[3]} for r in c.fetchall()]
    conn.close()
    return jsonify({'stocks': stocks})

@app.route('/api/positions', methods=['GET', 'POST'])
def positions():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    if request.method == 'POST':
        data = request.json
        c.execute('SELECT id FROM stocks WHERE symbol = ?', (data['symbol'],))
        stock = c.fetchone()
        if stock:
            c.execute('INSERT INTO positions (stock_id, shares, avg_cost) VALUES (?, ?, ?)',
                      (stock[0], data['shares'], data['avg_cost']))
            conn.commit()
        conn.close()
        return jsonify({'status': 'ok'}), 201
    
    c.execute('''SELECT p.*, s.symbol, s.name, s.market 
                 FROM positions p JOIN stocks s ON p.stock_id = s.id''')
    positions = [{
        'id': r[0], 'shares': r[2], 'avg_cost': r[3], 'current_price': r[4],
        'current_value': r[5], 'profit_loss': r[6], 'profit_loss_percent': r[7],
        'recommendation': r[8], 'stock': {'symbol': r[10], 'name': r[11], 'market': r[12]}
    } for r in c.fetchall()]
    conn.close()
    return jsonify({'positions': positions})

@app.route('/api/portfolio/summary')
def portfolio_summary():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''SELECT p.*, s.symbol, s.name, s.market FROM positions p 
                 JOIN stocks s ON p.stock_id = s.id''')
    positions = c.fetchall()
    conn.close()
    
    if not positions:
        return jsonify({'total_value': 0, 'total_cost': 0, 'positions': []})
    
    total_value = sum(r[5] or 0 for r in positions)
    total_cost = sum(r[2] * r[3] for r in positions)
    total_pl = total_value - total_cost
    total_pl_pct = (total_pl / total_cost * 100) if total_cost > 0 else 0
    
    return jsonify({
        'total_value': total_value,
        'total_cost': total_cost,
        'total_profit_loss': total_pl,
        'total_profit_loss_percent': total_pl_pct,
        'positions': [{
            'id': r[0], 'shares': r[2], 'avg_cost': r[3], 'current_price': r[4],
            'current_value': r[5], 'profit_loss': r[6], 'profit_loss_percent': r[7],
            'recommendation': r[8], 'stock': {'symbol': r[10], 'name': r[11], 'market': r[12]}
        } for r in positions]
    })

@app.route('/api/portfolio/update', methods=['POST'])
def update_portfolio():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT p.id, s.symbol, s.market FROM positions p JOIN stocks s ON p.stock_id = s.id')
    positions = c.fetchall()
    
    for pos_id, symbol, market in positions:
        price = update_price(symbol, market)
        if price:
            c.execute('SELECT shares, avg_cost FROM positions WHERE id = ?', (pos_id,))
            shares, avg_cost = c.fetchone()
            value = shares * price
            cost = shares * avg_cost
            pl = value - cost
            pl_pct = (pl / cost * 100) if cost > 0 else 0
            
            # Get recommendation
            ticker = f"{symbol}.TW" if market == 'TW' else symbol
            try:
                df = yf.Ticker(ticker).history(period='1y')
                df = calculate_indicators(df)
                rec = get_recommendation(df, price)
            except:
                rec = 'HOLD'
            
            c.execute('''UPDATE positions SET current_price=?, current_value=?, 
                          profit_loss=?, profit_loss_percent=?, recommendation=?, last_updated=? 
                          WHERE id=?''',
                      (price, value, pl, pl_pct, rec, datetime.now().isoformat(), pos_id))
    
    conn.commit()
    conn.close()
    return jsonify({'status': 'updated'})

if __name__ == '__main__':
    init_db()
    print("🚀 股票追蹤系統已啟動!")
    print("📊 請打開瀏覽器: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
