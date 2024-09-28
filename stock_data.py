import yfinance as yf
import pandas as pd
import numpy as np

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
    print(f"Debug: get_advanced_stock_data called with symbol={symbol}, period={period}")
    data = get_stock_data(symbol, period)
    print(f"Debug: get_stock_data returned data: {data is not None}")
    if data is None:
        print("Debug: data is None, returning None")
        return None
    if not data.empty:
        try:
            print("Debug: Calculating MACD")
            macd_data = calculate_macd(data)
            data['MACD'] = macd_data['MACD']
            data['Signal'] = macd_data['Signal']
            data['Histogram'] = macd_data['Histogram']
            
            print("Debug: Calculating RSI")
            data['RSI'] = calculate_rsi(data)
            
            print("Debug: Calculating Bollinger Bands")
            bb_data = calculate_bollinger_bands(data)
            data['BB_Upper'] = bb_data['BB_Upper']
            data['BB_Middle'] = bb_data['BB_Middle']
            data['BB_Lower'] = bb_data['BB_Lower']
            
            print("Debug: Calculating Fibonacci Retracement")
            fib_data = calculate_fibonacci_retracement(data)
            for col in fib_data.columns:
                data[col] = fib_data[col]
            
            print("Debug: Calculating SMAs")
            data['SMA_50'] = calculate_sma(data, 50)
            data['SMA_200'] = calculate_sma(data, 200)
            
            print("Debug: Detecting SMA Crossover")
            data['SMA_Crossover'] = detect_sma_crossover(data)
            
            print("Debug: Advanced indicators calculation completed")
            print("Debug: Data shape:", data.shape)
            print("Debug: Data columns:", data.columns)
            print("Debug: First few rows of data:")
            print(data.head())
            
            return data
        except Exception as e:
            print(f"Error calculating advanced indicators: {e}")
            return data
    else:
        print("Error: No data available for the given symbol and period")
        return None
