import yfinance as yf
import pandas as pd

def get_stock_data(symbol, period="1mo"):
    """
    Fetch stock data for a given symbol and time period.
    """
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
