import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from yfinance.exceptions import YFinanceException

class InvalidStockSymbolError(Exception):
    pass

def get_stock_data(symbol, period="1mo"):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period=period)
        if data.empty:
            raise InvalidStockSymbolError(f"No data available for symbol: {symbol}")
        return data
    except YFinanceException as e:
        logging.error(f"YFinance error for symbol {symbol}: {str(e)}")
        raise InvalidStockSymbolError(f"Invalid stock symbol: {symbol}")
    except Exception as e:
        logging.error(f"Error fetching stock data for {symbol}: {str(e)}")
        raise

def get_stock_info(symbol):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        
        if not info or 'symbol' not in info:
            raise InvalidStockSymbolError(f"Invalid stock symbol: {symbol}")
        
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
    except YFinanceException as e:
        logging.error(f"YFinance error for symbol {symbol}: {str(e)}")
        raise InvalidStockSymbolError(f"Invalid stock symbol: {symbol}")
    except Exception as e:
        logging.error(f"Error fetching stock info for {symbol}: {str(e)}")
        raise

# Rest of the file remains unchanged
