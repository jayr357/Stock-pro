import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_stock_data(symbol, period="1mo"):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period=period)
        return data
    except Exception as e:
        print(f"Error fetching stock data: {e}")
        return None

def get_stock_info(symbol):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        sector_contribution = get_sector_contribution(stock)
        return {
            'marketCap': float(info.get('marketCap', 0)),
            'trailingPE': info.get('trailingPE', 'N/A'),
            'trailingEps': info.get('trailingEps', 'N/A'),
            'dividendYield': info.get('dividendYield', 'N/A'),
            'currentPrice': info.get('currentPrice', 'N/A'),
            'percentChange': info.get('regularMarketChangePercent', 'N/A'),
            'longName': info.get('longName', 'N/A'),
            'longBusinessSummary': info.get('longBusinessSummary', 'N/A'),
            'founded': info.get('founded', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'sector': info.get('sector', 'N/A'),
            'website': info.get('website', 'N/A'),
            'fullTimeEmployees': info.get('fullTimeEmployees', 'N/A'),
            'products': info.get('products', 'N/A'),
            'sector_contribution': sector_contribution
        }
    except Exception as e:
        print(f"Error fetching stock info: {e}")
        return None

def get_sector_contribution(stock):
    try:
        # This is a placeholder function. In reality, you would need to
        # implement logic to fetch and calculate sector contribution data.
        # For now, we'll return some dummy data.
        return {
            'Technology': 0.4,
            'Consumer Cyclical': 0.3,
            'Healthcare': 0.2,
            'Financials': 0.1
        }
    except Exception as e:
        print(f"Error fetching sector contribution: {e}")
        return None

def calculate_macd(data):
    exp1 = data['Close'].ewm(span=12, adjust=False).mean()
    exp2 = data['Close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    histogram = macd - signal
    return pd.DataFrame({'MACD': macd, 'Signal': signal, 'Histogram': histogram})

def calculate_rsi(data, periods=14):
    close_delta = data['Close'].diff()
    up = close_delta.clip(lower=0)
    down = -1 * close_delta.clip(upper=0)
    ma_up = up.ewm(com=periods-1, adjust=False).mean()
    ma_down = down.ewm(com=periods-1, adjust=False).mean()
    rsi = ma_up / (ma_up + ma_down) * 100
    return rsi

def calculate_bollinger_bands(data, window=20):
    rolling_mean = data['Close'].rolling(window=window).mean()
    rolling_std = data['Close'].rolling(window=window).std()
    upper_band = rolling_mean + (rolling_std * 2)
    lower_band = rolling_mean - (rolling_std * 2)
    return pd.DataFrame({'BB_Middle': rolling_mean, 'BB_Upper': upper_band, 'BB_Lower': lower_band})

def calculate_fibonacci_retracement(data):
    high = data['High'].max()
    low = data['Low'].min()
    diff = high - low
    levels = [0, 0.236, 0.382, 0.5, 0.618, 1]
    retracements = [(high - (diff * level)) for level in levels]
    return pd.DataFrame({'Fib_' + str(int(level*100)): [ret] * len(data) for level, ret in zip(levels, retracements)})

def calculate_sma(data, window):
    return data['Close'].rolling(window=window).mean()

def detect_sma_crossover(data):
    crossover_points = ((data['SMA_50'] > data['SMA_200']) & (data['SMA_50'].shift(1) <= data['SMA_200'].shift(1))) | \
                       ((data['SMA_50'] < data['SMA_200']) & (data['SMA_50'].shift(1) >= data['SMA_200'].shift(1)))
    return crossover_points

def get_advanced_stock_data(symbol, period="1mo"):
    try:
        stock = yf.Ticker(symbol)
        
        end_date = datetime.now()
        if period == "1w":
            start_date = end_date - timedelta(days=7)
            data = stock.history(start=start_date, end=end_date, interval="1h")
        else:
            data = stock.history(period=period)
        
        if data.empty:
            print(f"No data available for {symbol} in the specified period.")
            return None
        
        # Calculate advanced indicators
        data['MACD'], data['Signal'], data['Histogram'] = calculate_macd(data).T.values
        data['RSI'] = calculate_rsi(data)
        bb_data = calculate_bollinger_bands(data)
        data['BB_Upper'] = bb_data['BB_Upper']
        data['BB_Middle'] = bb_data['BB_Middle']
        data['BB_Lower'] = bb_data['BB_Lower']
        fib_data = calculate_fibonacci_retracement(data)
        for col in fib_data.columns:
            data[col] = fib_data[col]
        data['SMA_50'] = calculate_sma(data, 50)
        data['SMA_200'] = calculate_sma(data, 200)
        data['SMA_Crossover'] = detect_sma_crossover(data)
        
        return data
    except Exception as e:
        print(f"Error calculating advanced indicators: {e}")
        return None
