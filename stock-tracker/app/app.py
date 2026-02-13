"""
股票追蹤與分析系統 - Flask Backend
Stock Tracker & Analysis System
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import json
import os
import logging
from threading import Thread
import schedule
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://stock:stock123@localhost:5432/stocktracker')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

db = SQLAlchemy(app)

# ============== Database Models ==============

class Stock(db.Model):
    """股票基本資料"""
    __tablename__ = 'stocks'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(200))
    market = db.Column(db.String(50))  # TW, US, HK, JP
    sector = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    positions = db.relationship('Position', backref='stock', lazy=True)
    prices = db.relationship('Price', backref='stock', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'name': self.name,
            'market': self.market,
            'sector': self.sector,
            'industry': self.industry,
        }

class Position(db.Model):
    """持股部位"""
    __tablename__ = 'positions'
    
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    shares = db.Column(db.Float, nullable=False)
    avg_cost = db.Column(db.Float, nullable=False)
    current_price = db.Column(db.Float)
    current_value = db.Column(db.Float)
    total_cost = db.Column(db.Float)
    profit_loss = db.Column(db.Float)
    profit_loss_percent = db.Column(db.Float)
    recommendation = db.Column(db.String(20))  # BUY, HOLD, SELL
    last_updated = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'stock': self.stock.to_dict() if self.stock else None,
            'shares': self.shares,
            'avg_cost': self.avg_cost,
            'current_price': self.current_price,
            'current_value': self.current_value,
            'profit_loss': self.profit_loss,
            'profit_loss_percent': self.profit_loss_percent,
            'recommendation': self.recommendation,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
        }

class Price(db.Model):
    """歷史價格"""
    __tablename__ = 'prices'
    
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    open = db.Column(db.Float)
    high = db.Column(db.Float)
    low = db.Column(db.Float)
    close = db.Column(db.Float)
    volume = db.Column(db.BigInteger)
    adjusted_close = db.Column(db.Float)
    
    __table_args__ = (
        db.UniqueConstraint('stock_id', 'date', name='unique_stock_date'),
    )

class AnalysisResult(db.Model):
    """分析結果"""
    __tablename__ = 'analysis_results'
    
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    analysis_type = db.Column(db.String(50))  # technical, fundamental, sentiment
    result_data = db.Column(db.JSON)
    recommendation = db.Column(db.String(20))
    confidence = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    stock = db.relationship('Stock')

# ============== Stock Data Service ==============

class StockDataService:
    """股票資料服務"""
    
    @staticmethod
    def get_price(symbol, market='TW'):
        """取得即時股價"""
        try:
            if market == 'TW':
                ticker = f"{symbol}.TW"
            elif market == 'US':
                ticker = symbol
            else:
                ticker = f"{symbol}.{market}"
            
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return {
                'symbol': symbol,
                'current_price': info.get('currentPrice', info.get('regularMarketPrice')),
                'previous_close': info.get('previousClose', info.get('regularMarketPreviousClose')),
                'open': info.get('open', info.get('regularMarketOpen')),
                'high': info.get('dayHigh', info.get('regularMarketDayHigh')),
                'low': info.get('dayLow', info.get('regularMarketDayLow')),
                'volume': info.get('volume', info.get('regularMarketVolume')),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'dividend_yield': info.get('dividendYield'),
            }
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return None
    
    @staticmethod
    def get_history(symbol, market='TW', period='1y'):
        """取得歷史股價"""
        try:
            if market == 'TW':
                ticker = f"{symbol}.TW"
            elif market == 'US':
                ticker = symbol
            else:
                ticker = f"{symbol}.{market}"
            
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)
            
            return df
        except Exception as e:
            logger.error(f"Error fetching history for {symbol}: {e}")
            return None
    
    @staticmethod
    def get_fundamental(symbol, market='TW'):
        """取得基本面資料"""
        try:
            if market == 'TW':
                ticker = f"{symbol}.TW"
            elif market == 'US':
                ticker = symbol
            else:
                ticker = f"{symbol}.{market}"
            
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return {
                'symbol': symbol,
                'company_name': info.get('longName', info.get('shortName')),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'peg_ratio': info.get('pegRatio'),
                'price_to_book': info.get('priceToBook'),
                'dividend_yield': info.get('dividendYield'),
                'eps': info.get('trailingEps'),
                'revenue_growth': info.get('revenueGrowth'),
                'profit_margin': info.get('profitMargin'),
                'roe': info.get('returnOnEquity'),
                'debt_to_equity': info.get('debtToEquity'),
                'current_ratio': info.get('currentRatio'),
                'free_cash_flow': info.get('freeCashflow'),
            }
        except Exception as e:
            logger.error(f"Error fetching fundamental for {symbol}: {e}")
            return None

# ============== Analysis Service ==============

class AnalysisService:
    """股票分析服務"""
    
    @staticmethod
    def calculate_technical_indicators(df):
        """計算技術指標"""
        if df is None or len(df) < 50:
            return None
        
        # 移動平均線
        df['MA5'] = df['Close'].rolling(window=5).mean()
        df['MA10'] = df['Close'].rolling(window=10).mean()
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA60'] = df['Close'].rolling(window=60).mean()
        
        # MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['Signal']
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # 布林通道
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        
        # 成交量
        df['Volume_MA20'] = df['Volume'].rolling(window=20).mean()
        
        return df
    
    @staticmethod
    def generate_recommendation(df, current_price):
        """產生買賣建議"""
        if df is None:
            return 'HOLD'
        
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        
        score = 0
        
        # 價格相對均線
        if current_price > latest.get('MA20', current_price):
            score += 1
        elif current_price < latest.get('MA20', current_price):
            score -= 1
        
        # RSI
        rsi = latest.get('RSI', 50)
        if rsi < 30:
            score += 2  # 超賣，可能反彈
        elif rsi > 70:
            score -= 2  # 超買，可能回調
        elif rsi < 50:
            score -= 1
        else:
            score += 1
        
        # MACD
        macd = latest.get('MACD', 0)
        signal = latest.get('Signal', 0)
        if macd > signal:
            score += 1
        else:
            score -= 1
        
        # 成交量
        if latest.get('Volume', 0) > latest.get('Volume_MA20', 0) * 1.5:
            score += 1
        
        # 價格動能
        price_change = (latest['Close'] - df.iloc[-10]['Close']) / df.iloc[-10]['Close'] * 100 if len(df) >= 10 else 0
        if price_change > 10:
            score += 1
        elif price_change < -10:
            score -= 1
        
        # 最終建議
        if score >= 3:
            return 'STRONG_BUY'
        elif score >= 1:
            return 'BUY'
        elif score <= -3:
            return 'STRONG_SELL'
        elif score <= -1:
            return 'SELL'
        else:
            return 'HOLD'
    
    @staticmethod
    def analyze_stock(symbol, market='TW'):
        """完整分析"""
        # 取得股價
        price_data = StockDataService.get_price(symbol, market)
        history = StockDataService.get_history(symbol, market, period='1y')
        fundamental = StockDataService.get_fundamental(symbol, market)
        
        if price_data is None:
            return None
        
        current_price = price_data.get('current_price', 0)
        
        # 計算技術指標
        df = AnalysisService.calculate_technical_indicators(history)
        
        # 產生建議
        recommendation = AnalysisService.generate_recommendation(df, current_price)
        
        # 分析資料
        if df is not None and len(df) > 0:
            latest = df.iloc[-1]
            technicals = {
                'current_price': current_price,
                'ma5': float(latest.get('MA5', current_price)),
                'ma20': float(latest.get('MA20', current_price)),
                'ma60': float(latest.get('MA60', current_price)),
                'rsi': float(latest.get('RSI', 50)),
                'macd': float(latest.get('MACD', 0)),
                'macd_signal': float(latest.get('Signal', 0)),
                'bb_upper': float(latest.get('BB_Upper', current_price)),
                'bb_lower': float(latest.get('BB_Lower', current_price)),
                'volume': int(latest.get('Volume', 0)),
                'volume_ma20': float(latest.get('Volume_MA20', 0)),
            }
        else:
            technicals = {'current_price': current_price}
        
        return {
            'symbol': symbol,
            'price': price_data,
            'technicals': technicals,
            'fundamental': fundamental,
            'recommendation': recommendation,
            'analyzed_at': datetime.utcnow().isoformat(),
        }

# ============== Portfolio Service ==============

class PortfolioService:
    """投資組合服務"""
    
    @staticmethod
    def update_position(position_id):
        """更新部位"""
        position = Position.query.get(position_id)
        if not position:
            return None
        
        stock = position.stock
        if not stock:
            return None
        
        price_data = StockDataService.get_price(stock.symbol, stock.market)
        if price_data is None:
            return None
        
        current_price = price_data.get('current_price', 0)
        
        # 計算部位價值
        current_value = position.shares * current_price
        total_cost = position.shares * position.avg_cost
        profit_loss = current_value - total_cost
        profit_loss_percent = (profit_loss / total_cost * 100) if total_cost > 0 else 0
        
        # 取得建議
        analysis = AnalysisService.analyze_stock(stock.symbol, stock.market)
        recommendation = analysis['recommendation'] if analysis else 'HOLD'
        
        # 更新資料庫
        position.current_price = current_price
        position.current_value = current_value
        position.profit_loss = profit_loss
        position.profit_loss_percent = profit_loss_percent
        position.recommendation = recommendation
        position.last_updated = datetime.utcnow()
        
        db.session.commit()
        
        return position.to_dict()
    
    @staticmethod
    def update_all_positions():
        """更新所有部位"""
        positions = Position.query.all()
        results = []
        
        for position in positions:
            result = PortfolioService.update_position(position.id)
            if result:
                results.append(result)
        
        logger.info(f"Updated {len(results)} positions")
        return results
    
    @staticmethod
    def get_portfolio_summary():
        """投資組合總覽"""
        positions = Position.query.all()
        
        total_value = sum(p.current_value or 0 for p in positions)
        total_cost = sum(p.shares * p.avg_cost for p in positions)
        total_profit_loss = total_value - total_cost
        total_profit_loss_percent = (total_profit_loss / total_cost * 100) if total_cost > 0 else 0
        
        # 按市場分類
        by_market = {}
        for position in positions:
            market = position.stock.market if position.stock else 'Unknown'
            if market not in by_market:
                by_market[market] = {'value': 0, 'count': 0}
            by_market[market]['value'] += position.current_value or 0
            by_market[market]['count'] += 1
        
        # 按建議分類
        by_recommendation = {}
        for position in positions:
            rec = position.recommendation or 'HOLD'
            if rec not in by_recommendation:
                by_recommendation[rec] = {'count': 0, 'value': 0}
            by_recommendation[rec]['count'] += 1
            by_recommendation[rec]['value'] += position.current_value or 0
        
        # 表現最好的前5名
        top_performers = sorted(
            positions,
            key=lambda x: x.profit_loss_percent or 0,
            reverse=True
        )[:5]
        
        # 需要減持的前5名
        bottom_performers = sorted(
            positions,
            key=lambda x: x.profit_loss_percent or 0
        )[:5]
        
        return {
            'total_value': total_value,
            'total_cost': total_cost,
            'total_profit_loss': total_profit_loss,
            'total_profit_loss_percent': total_profit_loss_percent,
            'positions_count': len(positions),
            'by_market': by_market,
            'by_recommendation': by_recommendation,
            'top_performers': [p.to_dict() for p in top_performers],
            'bottom_performers': [p.to_dict() for p in bottom_performers],
            'updated_at': datetime.utcnow().isoformat(),
        }

# ============== API Routes ==============

@app.route('/api/health', methods=['GET'])
def health():
    """健康檢查"""
    return jsonify({'status': 'ok', 'timestamp': datetime.utcnow().isoformat()})

@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    """取得所有股票"""
    stocks = Stock.query.all()
    return jsonify({'stocks': [s.to_dict() for s in stocks]})

@app.route('/api/stocks', methods=['POST'])
def add_stock():
    """新增股票"""
    data = request.json
    stock = Stock(
        symbol=data['symbol'],
        name=data.get('name'),
        market=data.get('market', 'TW'),
        sector=data.get('sector'),
        industry=data.get('industry'),
    )
    db.session.add(stock)
    db.session.commit()
    return jsonify(stock.to_dict()), 201

@app.route('/api/positions', methods=['GET'])
def get_positions():
    """取得所有部位"""
    positions = Position.query.all()
    return jsonify({'positions': [p.to_dict() for p in positions]})

@app.route('/api/positions', methods=['POST'])
def add_position():
    """新增部位"""
    data = request.json
    stock = Stock.query.filter_by(symbol=data['symbol']).first()
    if not stock:
        return jsonify({'error': 'Stock not found'}), 404
    
    position = Position(
        stock_id=stock.id,
        shares=data['shares'],
        avg_cost=data['avg_cost'],
        current_price=data.get('avg_cost'),
        current_value=data['shares'] * data['avg_cost'],
        total_cost=data['shares'] * data['avg_cost'],
        recommendation='HOLD',
    )
    db.session.add(position)
    db.session.commit()
    
    # 更新部位資料
    PortfolioService.update_position(position.id)
    
    return jsonify(position.to_dict()), 201

@app.route('/api/portfolio/summary', methods=['GET'])
def portfolio_summary():
    """投資組合總覽"""
    summary = PortfolioService.get_portfolio_summary()
    return jsonify(summary)

@app.route('/api/portfolio/update', methods=['POST'])
def update_portfolio():
    """更新投資組合"""
    results = PortfolioService.update_all_positions()
    return jsonify({'updated': len(results), 'positions': results})

@app.route('/api/analyze/<symbol>', methods=['GET'])
def analyze(symbol):
    """分析單一股票"""
    market = request.args.get('market', 'TW')
    analysis = AnalysisService.analyze_stock(symbol, market)
    
    if analysis is None:
        return jsonify({'error': 'Unable to fetch data'}), 404
    
    return jsonify(analysis)

@app.route('/api/recommendations', methods=['GET'])
def recommendations():
    """取得買賣建議"""
    positions = Position.query.all()
    
    buy = [p.to_dict() for p in positions if p.recommendation in ['STRONG_BUY', 'BUY']]
    hold = [p.to_dict() for p in positions if p.recommendation == 'HOLD']
    sell = [p.to_dict() for p in positions if p.recommendation in ['STRONG_SELL', 'SELL']]
    
    return jsonify({
        'buy': buy,
        'hold': hold,
        'sell': sell,
        'summary': {
            'buy_count': len(buy),
            'hold_count': len(hold),
            'sell_count': len(sell),
        }
    })

# ============== Scheduler ==============

def scheduled_update():
    """排程更新"""
    logger.info("Running scheduled portfolio update...")
    try:
        PortfolioService.update_all_positions()
        logger.info("Scheduled update completed")
    except Exception as e:
        logger.error(f"Scheduled update failed: {e}")

def run_scheduler():
    """執行排程"""
    # 每天 9:00 更新（台股開盤前）
    schedule.every().day.at("09:00").do(scheduled_update)
    # 每天 13:30 更新（台股收盤後）
    schedule.every().day.at("13:30").do(scheduled_update)
    # 每天 23:00 更新（美股收盤後）
    schedule.every().day.at("23:00").do(scheduled_update)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

# ============== Init Database ==============

def init_db():
    """初始化資料庫"""
    with app.app_context():
        db.create_all()
        logger.info("Database initialized")

# ============== Main ==============

if __name__ == '__main__':
    init_db()
    
    # 啟動排程執行緒
    scheduler_thread = Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    # 啟動 Flask
    app.run(host='0.0.0.0', port=5000, debug=False)
