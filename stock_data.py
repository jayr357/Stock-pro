import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import traceback

class InvalidStockSymbolError(Exception):
    pass

def is_valid_symbol(symbol):
    logging.info(f"Checking validity of symbol: {symbol}")
    if len(symbol) == 0:
        logging.error(f"Invalid symbol: Empty string")
        return False
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        if not info:
            logging.error(f"Invalid symbol: {symbol} - No info available")
            return False
        if 'symbol' not in info:
            logging.error(f"Invalid symbol: {symbol} - Symbol not found in info")
            return False
        logging.info(f"Valid symbol: {symbol}")
        return True
    except Exception as e:
        logging.error(f"Error validating symbol {symbol}: {str(e)}")
        logging.error(traceback.format_exc())
        return False

def get_stock_data(symbol, period="1mo"):
    try:
        if not is_valid_symbol(symbol):
            raise InvalidStockSymbolError(f"Invalid stock symbol: {symbol}. Please enter a valid stock symbol.")
        
        stock = yf.Ticker(symbol)
        data = stock.history(period=period)
        if data.empty:
            raise InvalidStockSymbolError(f"No data available for symbol: {symbol}. Please enter a valid stock symbol.")
        return data
    except Exception as e:
        logging.error(f"Error for symbol {symbol}: {str(e)}")
        logging.error(traceback.format_exc())
        raise InvalidStockSymbolError(f"Error fetching data for symbol: {symbol}. Please try again or enter a different symbol.")

def get_stock_info(symbol):
    try:
        if not is_valid_symbol(symbol):
            raise InvalidStockSymbolError(f"Invalid stock symbol: {symbol}. Please enter a valid stock symbol.")
        
        stock = yf.Ticker(symbol)
        info = stock.info
        
        if not info:
            raise InvalidStockSymbolError(f"No information available for symbol: {symbol}. Please enter a valid stock symbol.")
        
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
    except Exception as e:
        logging.error(f"Error fetching stock info for {symbol}: {str(e)}")
        logging.error(traceback.format_exc())
        raise InvalidStockSymbolError(f"Error fetching information for symbol: {symbol}. Please try again or enter a different symbol.")

def calculate_support_resistance(data, window=14):
    rolling_min = data['Low'].rolling(window=window).min()
    rolling_max = data['High'].rolling(window=window).max()
    
    support = rolling_min.mean()
    resistance = rolling_max.mean()
    
    return support, resistance

def get_advanced_stock_data(symbol, period="1mo"):
    valid_periods = {
        "1m": ("1d", "1m"),
        "5m": ("5d", "5m"),
        "15m": ("7d", "15m"),
        "30m": ("60d", "30m"),
        "1hr": ("60d", "1h"),
        "24hr": ("60d", "1h"),
        "3month": ("3mo", "1d"),
        "1year": ("1y", "1d")
    }
    
    if period not in valid_periods:
        raise ValueError(f"Invalid period. Must be one of {list(valid_periods.keys())}")
    
    try:
        if not is_valid_symbol(symbol):
            raise InvalidStockSymbolError(f"Invalid stock symbol: {symbol}. Please enter a valid stock symbol.")
        
        stock = yf.Ticker(symbol)
        yf_period, interval = valid_periods[period]
        
        data = stock.history(period=yf_period, interval=interval)
        
        if data.empty:
            raise InvalidStockSymbolError(f"No data available for symbol: {symbol} with period {period}. Please try a different period or stock symbol.")
        
        support, resistance = calculate_support_resistance(data)
        
        data['Support'] = support
        data['Resistance'] = resistance
        
        return data
    except yf.exceptions.YFinanceException as yfe:
        logging.error(f"YFinance error for {symbol} with period {period}: {str(yfe)}")
        logging.error(traceback.format_exc())
        raise InvalidStockSymbolError(f"Error fetching data for symbol: {symbol} with period {period}. The data might not be available for this time frame.")
    except Exception as e:
        logging.error(f"Error fetching advanced stock data for {symbol} with period {period}: {str(e)}")
        logging.error(traceback.format_exc())
        raise InvalidStockSymbolError(f"Error fetching data for symbol: {symbol} with period {period}. Please try again or enter a different symbol.")

def get_sector_contribution(stock):
    return {
        'Product A': 30,
        'Product B': 25,
        'Product C': 20,
        'Other': 25
    }

__all__ = ['get_stock_data', 'get_stock_info', 'get_advanced_stock_data', 'InvalidStockSymbolError']
