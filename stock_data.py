import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

class InvalidStockSymbolError(Exception):
    pass

def get_stock_data(symbol, period="1mo"):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period=period)
        if data.empty:
            raise InvalidStockSymbolError(f"No data available for symbol: {symbol}")
        return data
    except Exception as e:
        logging.error(f"YFinance error for symbol {symbol}: {str(e)}")
        raise InvalidStockSymbolError(f"Invalid stock symbol: {symbol}")

def get_stock_info(symbol):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        
        if not info or 'symbol' not in info or 'shortName' not in info:
            raise InvalidStockSymbolError(f"Invalid or non-existent stock symbol: {symbol}")
        
        sector_contribution = get_sector_contribution(stock)
        return {
            'longName': info.get('longName', 'N/A'),
            'marketCap': float(info.get('marketCap', 0)),
            'trailingPE': info.get('trailingPE', 'N/A'),
            'trailingEps': info.get('trailingEps', 'N/A'),
            'dividendYield': info.get('dividendYield', 'N/A'),
            'currentPrice': info.get('currentPrice', 'N/A'),
            'percentChange': info.get('regularMarketChangePercent', 'N/A'),
            'longBusinessSummary': info.get('longBusinessSummary', 'N/A'),
            'founded': info.get('founded', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'sector': info.get('sector', 'N/A'),
            'website': info.get('website', 'N/A'),
            'fullTimeEmployees': info.get('fullTimeEmployees', 'N/A'),
            'products': info.get('products', 'N/A'),
            'sector_contribution': sector_contribution
        }
    except yf.exceptions.YFinanceException as yfe:
        logging.error(f"YFinance error for {symbol}: {str(yfe)}")
        raise InvalidStockSymbolError(f"Error fetching data for stock symbol: {symbol}. {str(yfe)}")
    except Exception as e:
        logging.error(f"Error fetching stock info for {symbol}: {str(e)}")
        raise InvalidStockSymbolError(f"Invalid stock symbol: {symbol}")

def get_advanced_stock_data(symbol, period="1mo"):
    valid_periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
    if period not in valid_periods:
        raise ValueError(f"Invalid period. Must be one of {valid_periods}")
    
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period=period)
        
        if data.empty:
            raise InvalidStockSymbolError(f"No data available for symbol: {symbol}")
        
        # Calculate additional indicators
        data['SMA_50'] = data['Close'].rolling(window=50).mean()
        data['SMA_200'] = data['Close'].rolling(window=200).mean()
        
        # MACD
        data['EMA_12'] = data['Close'].ewm(span=12, adjust=False).mean()
        data['EMA_26'] = data['Close'].ewm(span=26, adjust=False).mean()
        data['MACD'] = data['EMA_12'] - data['EMA_26']
        data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
        data['Histogram'] = data['MACD'] - data['Signal']
        
        # RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        data['BB_Middle'] = data['Close'].rolling(window=20).mean()
        data['BB_Upper'] = data['BB_Middle'] + 2 * data['Close'].rolling(window=20).std()
        data['BB_Lower'] = data['BB_Middle'] - 2 * data['Close'].rolling(window=20).std()
        
        # Fibonacci Retracement
        high = data['High'].max()
        low = data['Low'].min()
        diff = high - low
        data['Fib_0'] = low
        data['Fib_24'] = low + 0.236 * diff
        data['Fib_38'] = low + 0.382 * diff
        data['Fib_50'] = low + 0.5 * diff
        data['Fib_62'] = low + 0.618 * diff
        data['Fib_100'] = high
        
        # SMA Crossover
        data['SMA_Crossover'] = np.where(data['SMA_50'] > data['SMA_200'], 1, 0)
        data['SMA_Crossover'] = np.where(data['SMA_50'] < data['SMA_200'], -1, data['SMA_Crossover'])
        
        return data
    except yf.exceptions.YFinanceException as yfe:
        logging.error(f"YFinance error for {symbol}: {str(yfe)}")
        raise InvalidStockSymbolError(f"Error fetching data for stock symbol: {symbol}. {str(yfe)}")
    except Exception as e:
        logging.error(f"Error fetching advanced stock data for {symbol}: {str(e)}")
        raise InvalidStockSymbolError(f"Invalid stock symbol: {symbol}")

def get_sector_contribution(stock):
    # This is a placeholder function. In a real-world scenario, you'd fetch this data from a reliable source.
    return {
        'Product A': 30,
        'Product B': 25,
        'Product C': 20,
        'Other': 25
    }

# Ensure all necessary functions are exported
__all__ = ['get_stock_data', 'get_stock_info', 'get_advanced_stock_data', 'InvalidStockSymbolError']
