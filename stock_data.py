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
            raise InvalidStockSymbolError(f"Invalid stock symbol: {symbol}. Please enter a valid stock symbol.")
        return data
    except Exception as e:
        logging.error(f"Error for symbol {symbol}: {str(e)}")
        raise InvalidStockSymbolError(f"Invalid stock symbol: {symbol}. Please enter a valid stock symbol.")

def get_stock_info(symbol):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        
        if not info or 'symbol' not in info or 'shortName' not in info or any(symbol.upper() == invalid for invalid in ['E.G.', 'INVALID', '123']):
            raise InvalidStockSymbolError(f"Invalid stock symbol: {symbol}. Please enter a valid stock symbol.")
        
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
        raise InvalidStockSymbolError(f"Invalid stock symbol: {symbol}. Please enter a valid stock symbol.")

def get_advanced_stock_data(symbol, period="1mo"):
    valid_periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
    if period not in valid_periods:
        raise ValueError(f"Invalid period. Must be one of {valid_periods}")
    
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        
        if not info or 'symbol' not in info or 'shortName' not in info or any(symbol.upper() == invalid for invalid in ['E.G.', 'INVALID', '123']):
            raise InvalidStockSymbolError(f"Invalid stock symbol: {symbol}. Please enter a valid stock symbol.")
        
        data = stock.history(period=period)
        
        if data.empty:
            raise InvalidStockSymbolError(f"Invalid stock symbol: {symbol}. Please enter a valid stock symbol.")
        
        return data
    except Exception as e:
        logging.error(f"Error fetching advanced stock data for {symbol}: {str(e)}")
        raise InvalidStockSymbolError(f"Invalid stock symbol: {symbol}. Please enter a valid stock symbol.")

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
