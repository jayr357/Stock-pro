import os
from fredapi import Fred
from datetime import datetime, timedelta

# Initialize FRED API client
fred = Fred(api_key=os.environ['FRED_API_KEY'])

def get_economic_indicators(indicators, start_date=None, end_date=None):
    """
    Fetch economic indicators from FRED.
    
    :param indicators: List of indicator codes to fetch
    :param start_date: Start date for data (default: 1 year ago)
    :param end_date: End date for data (default: today)
    :return: Dictionary of indicator data
    """
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    indicator_data = {}
    for indicator in indicators:
        try:
            data = fred.get_series(indicator, start_date, end_date)
            indicator_data[indicator] = data
        except Exception as e:
            print(f"Error fetching {indicator}: {str(e)}")
    
    return indicator_data

def get_relevant_economic_indicators(stock_symbol):
    """
    Get relevant economic indicators based on the stock's sector.
    
    :param stock_symbol: Stock symbol to determine relevant indicators
    :return: List of relevant indicator codes
    """
    # This is a simplified example. In a real-world scenario, you'd have a more comprehensive
    # mapping of stocks to relevant economic indicators based on their sector, industry, etc.
    sector_indicators = {
        'Technology': ['CPIAUCSL', 'UMCSENT', 'UNRATE'],
        'Finance': ['DFF', 'T10Y2Y', 'MORTGAGE30US'],
        'Energy': ['DCOILWTICO', 'TOTALSA', 'IPG211111CN'],
        'Healthcare': ['CPIMEDSL', 'RXPUSW', 'HLTHFCSA'],
        'Consumer': ['CPIAUCSL', 'PCE', 'UMCSENT'],
    }
    
    # For this example, we'll return a default set of indicators
    # In a real implementation, you'd determine the stock's sector and return the appropriate indicators
    return sector_indicators.get('Consumer', ['CPIAUCSL', 'UNRATE', 'GDP'])
