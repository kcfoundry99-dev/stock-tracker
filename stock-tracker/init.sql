-- 初始化資料庫
-- PostgreSQL init script

-- 建立股票基本資料
INSERT INTO stocks (symbol, name, market, sector, industry) VALUES
('2330', '台積電', 'TW', 'Technology', 'Semiconductors'),
('2454', '聯發科', 'TW', 'Technology', 'Semiconductors'),
('2303', '聯電', 'TW', 'Technology', 'Semiconductors'),
('2317', '鴻海', 'TW', 'Technology', 'Electronics Manufacturing'),
('2376', '技嘉', 'TW', 'Technology', 'Computer Hardware'),
('2377', '微星', 'TW', 'Technology', 'Computer Hardware'),
('2382', '廣達', 'TW', 'Technology', 'Electronics Manufacturing'),
('2395', '研華', 'TW', 'Technology', 'Industrial Electronics'),
('3008', '大立光', 'TW', 'Technology', 'Optoelectronics'),
('3034', '聯詠', 'TW', 'Technology', 'Semiconductors'),
('3673', 'TPK-KY', 'TW', 'Technology', 'Electronics'),
('3704', '合庫金', 'TW', 'Finance', 'Banking'),
('5880', '合庫金', 'TW', 'Finance', 'Banking'),
('AAPL', 'Apple Inc.', 'US', 'Technology', 'Consumer Electronics'),
('MSFT', 'Microsoft Corporation', 'US', 'Technology', 'Software'),
('GOOGL', 'Alphabet Inc.', 'US', 'Technology', 'Internet Services'),
('NVDA', 'NVIDIA Corporation', 'US', 'Technology', 'Semiconductors'),
('TSLA', 'Tesla Inc.', 'US', 'Consumer Discretionary', 'Automotive');

-- 建立持股部位 (範例資料)
INSERT INTO positions (stock_id, shares, avg_cost, current_price, current_value, total_cost, profit_loss, profit_loss_percent, recommendation, last_updated) VALUES
(1, 1000, 550.00, 590.00, 590000, 550000, 40000, 7.27, 'BUY', NOW()),
(2, 500, 850.00, 920.00, 460000, 425000, 35000, 8.24, 'BUY', NOW()),
(3, 2000, 45.00, 52.30, 104600, 90000, 14600, 16.22, 'STRONG_BUY', NOW()),
(4, 800, 98.00, 105.50, 84400, 78400, 6000, 7.65, 'HOLD', NOW()),
(5, 300, 105.00, 95.50, 28650, 31500, -2850, -9.05, 'SELL', NOW()),
(6, 400, 115.00, 128.50, 51400, 46000, 5400, 11.74, 'STRONG_BUY', NOW()),
(7, 600, 72.00, 68.40, 41040, 43200, -2160, -5.00, 'HOLD', NOW()),
(8, 200, 385.00, 420.00, 84000, 77000, 7000, 9.09, 'BUY', NOW()),
(9, 100, 2450.00, 2380.00, 238000, 245000, -7000, -2.86, 'HOLD', NOW()),
(10, 300, 485.00, 510.00, 153000, 145500, 7500, 5.15, 'BUY', NOW()),
(14, 50, 150.00, 175.50, 8775, 7500, 1275, 17.00, 'STRONG_BUY', NOW()),
(15, 30, 350.00, 378.90, 11367, 10500, 867, 8.26, 'BUY', NOW()),
(16, 20, 135.00, 148.50, 2970, 2700, 270, 10.00, 'HOLD', NOW()),
(17, 20, 450.00, 495.80, 9916, 9000, 916, 10.18, 'STRONG_BUY', NOW()),
(18, 15, 250.00, 215.30, 3229.50, 3750, -520.50, -13.88, 'STRONG_SELL', NOW());

-- 建立分析結果
INSERT INTO analysis_results (stock_id, analysis_type, result_data, recommendation, confidence, created_at) VALUES
(1, 'technical', '{"rsi": 62, "ma20": 585, "macd": 2.5, "signal": 2.3}', 'BUY', 0.72, NOW()),
(2, 'technical', '{"rsi": 55, "ma20": 900, "macd": 8.5, "signal": 7.2}', 'BUY', 0.68, NOW()),
(3, 'technical', '{"rsi": 48, "ma20": 50, "macd": 1.2, "signal": 0.8}', 'STRONG_BUY', 0.75, NOW()),
(5, 'technical', '{"rsi": 38, "ma20": 100, "macd": -1.5, "signal": -0.8}', 'SELL', 0.70, NOW()),
(18, 'technical', '{"rsi": 32, "ma20": 230, "macd": -8.5, "signal": -5.2}', 'STRONG_SELL', 0.82, NOW());
