import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

class InvalidStockSymbolError(Exception):
    pass

def is_valid_symbol(symbol):
    # Add more comprehensive checks here
    return symbol.isalpha() and len(symbol) > 0 and not any(symbol.upper() == invalid for invalid in ['E.G.', 'INVALID', '123'])

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
        raise InvalidStockSymbolError(f"Error fetching data for symbol: {symbol}. Please try again or enter a different symbol.")

def get_stock_info(symbol):
    try:
        if not is_valid_symbol(symbol):
            raise InvalidStockSymbolError(f"Invalid stock symbol: {symbol}. Please enter a valid stock symbol.")
        
        stock = yf.Ticker(symbol)
        info = stock.info
        
        if not info or 'symbol' not in info or 'shortName' not in info:
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
        raise InvalidStockSymbolError(f"Error fetching information for symbol: {symbol}. Please try again or enter a different symbol.")

def get_advanced_stock_data(symbol, period="1mo"):
    valid_periods = {
        "1m": "1m",
        "5m": "5m",
        "30min": "30m",
        "1hr": "1h",
        "5hr": "5h",
        "1day": "1d",
        "3month": "3mo",
        "1year": "1y"
    }
    
    if period not in valid_periods:
        raise ValueError(f"Invalid period. Must be one of {list(valid_periods.keys())}")
    
    try:
        if not is_valid_symbol(symbol):
            raise InvalidStockSymbolError(f"Invalid stock symbol: {symbol}. Please enter a valid stock symbol.")
        
        stock = yf.Ticker(symbol)
        
        # For periods less than 1 day, we need to fetch intraday data
        if period in ["1m", "5m", "30min", "1hr", "5hr"]:
            end_date = datetime.now()
            if period == "5hr":
                start_date = end_date - timedelta(hours=5)
            else:
                start_date = end_date - timedelta(days=1)  # yfinance allows max 1 day for intraday data
            
            data = stock.history(start=start_date, end=end_date, interval=valid_periods[period])
        else:
            data = stock.history(period=valid_periods[period])
        
        if data.empty:
            raise InvalidStockSymbolError(f"No data available for symbol: {symbol}. Please enter a valid stock symbol.")
        
        return data
    except Exception as e:
        logging.error(f"Error fetching advanced stock data for {symbol}: {str(e)}")
        raise InvalidStockSymbolError(f"Error fetching data for symbol: {symbol}. Please try again or enter a different symbol.")

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
