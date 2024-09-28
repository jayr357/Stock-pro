import yfinance as yf
import pandas as pd
import numpy as np

def get_stock_data(symbol, period="1mo"):
    if period == "7d":
        # Use '5d' and fetch a bit more data to cover 7 days
        data = yf.Ticker(symbol).history(period="8d")
        # Keep only the last 7 days of data
        return data.tail(7)
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period=period)
        return data
    except Exception as e:
        print(f"Error fetching stock data: {e}")
        return None

def get_stock_info(symbol):
    """
    Fetch stock information for a given symbol.
    """
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        return {
            'marketCap': float(info.get('marketCap', 0)),
            'trailingPE': info.get('trailingPE', 'N/A'),
            'trailingEps': info.get('trailingEps', 'N/A'),
            'dividendYield': info.get('dividendYield', 'N/A')
        }
    except Exception as e:
        print(f"Error fetching stock info: {e}")
        return None

def calculate_macd(data):
    """
    Calculate the Moving Average Convergence Divergence (MACD) indicator.
    """
    exp1 = data['Close'].ewm(span=12, adjust=False).mean()
    exp2 = data['Close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    histogram = macd - signal
    return pd.DataFrame({'MACD': macd, 'Signal': signal, 'Histogram': histogram})

def calculate_rsi(data, periods=14):
    """
    Calculate the Relative Strength Index (RSI) indicator.
    """
    close_delta = data['Close'].diff()
    up = close_delta.clip(lower=0)
    down = -1 * close_delta.clip(upper=0)
    ma_up = up.ewm(com=periods-1, adjust=False).mean()
    ma_down = down.ewm(com=periods-1, adjust=False).mean()
    rsi = ma_up / (ma_up + ma_down) * 100
    return rsi

def calculate_bollinger_bands(data, window=20):
    """
    Calculate Bollinger Bands.
    """
    rolling_mean = data['Close'].rolling(window=window).mean()
    rolling_std = data['Close'].rolling(window=window).std()
    upper_band = rolling_mean + (rolling_std * 2)
    lower_band = rolling_mean - (rolling_std * 2)
    return pd.DataFrame({'Middle Band': rolling_mean, 'Upper Band': upper_band, 'Lower Band': lower_band})

def get_advanced_stock_data(symbol, period="1mo"):
    """
    Get stock data with advanced indicators.
    """
    data = get_stock_data(symbol, period)
    if data is not None and not data.empty:
        data['MACD'] = calculate_macd(data)['MACD']
        data['RSI'] = calculate_rsi(data)
        bb = calculate_bollinger_bands(data)
        data['BB_Upper'] = bb['Upper Band']
        data['BB_Middle'] = bb['Middle Band']
        data['BB_Lower'] = bb['Lower Band']
    return data
