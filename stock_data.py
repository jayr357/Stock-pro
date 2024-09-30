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
        
        if not info:
            raise ValueError(f"Invalid stock symbol: {symbol}")
        
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
    except ValueError as ve:
        print(f"Error fetching stock info: {ve}")
        return None
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
        if period in ["1m", "5m", "15m", "1h"]:
            if period == "1m":
                start_date = end_date - timedelta(days=7)
            elif period == "5m":
                start_date = end_date - timedelta(days=60)
            elif period == "15m":
                start_date = end_date - timedelta(days=60)
            elif period == "1h":
                start_date = end_date - timedelta(days=730)
            data = stock.history(start=start_date, end=end_date, interval=period)
        elif period == "1d":
            start_date = end_date - timedelta(days=365)
            data = stock.history(start=start_date, end=end_date, interval="1d")
        elif period == "1w":
            start_date = end_date - timedelta(weeks=52)
            data = stock.history(start=start_date, end=end_date, interval="1wk")
        elif period == "1mo":
            start_date = end_date - timedelta(days=365*2)
            data = stock.history(start=start_date, end=end_date, interval="1mo")
        elif period == "3mo":
            start_date = end_date - timedelta(days=365*5)
            data = stock.history(start=start_date, end=end_date, interval="3mo")
        else:
            data = stock.history(period=period)
        
        if data.empty:
            print(f"No data available for {symbol} in the specified period.")
            return None
        
        # Convert relevant columns to numeric type
        numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in numeric_columns:
            data[col] = pd.to_numeric(data[col], errors='coerce')
        
        # Calculate advanced indicators
        macd_data = calculate_macd(data)
        data['MACD'] = macd_data['MACD'].astype(float)
        data['Signal'] = macd_data['Signal'].astype(float)
        data['Histogram'] = macd_data['Histogram'].astype(float)
        data['RSI'] = calculate_rsi(data).astype(float)
        
        bb_data = calculate_bollinger_bands(data)
        data['BB_Upper'] = bb_data['BB_Upper'].astype(float)
        data['BB_Middle'] = bb_data['BB_Middle'].astype(float)
        data['BB_Lower'] = bb_data['BB_Lower'].astype(float)
        
        fib_data = calculate_fibonacci_retracement(data)
        for col in fib_data.columns:
            data[col] = fib_data[col].astype(float)
        
        data['SMA_50'] = calculate_sma(data, 50).astype(float)
        data['SMA_200'] = calculate_sma(data, 200).astype(float)
        data['SMA_Crossover'] = detect_sma_crossover(data)
        
        return data
    except Exception as e:
        print(f"Error calculating advanced indicators: {e}")
        return None