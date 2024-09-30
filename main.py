import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from stock_data import get_stock_data, get_stock_info, get_advanced_stock_data, InvalidStockSymbolError
from news_scraper import get_news_articles
from database import initialize_db, save_stock_to_db, get_user_stocks, remove_stock_from_db
from utils import convert_to_csv
from economic_data import get_economic_indicators, get_relevant_economic_indicators
from sentiment_analysis import analyze_news_sentiment
from fredapi import Fred
import random
import socket
import traceback
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the database
initialize_db()

st.set_page_config(page_title="Stock Data Visualization", page_icon="assets/favicon.svg", layout="wide")

st.title("Stock Data Retrieval and Visualization Tool")

# Create tabs for different sections
tab1, tab2, tab3 = st.tabs(["Stock Analysis", "Economic Indicators", "Watchlist"])

with tab1:
    # User input for stock symbol
    default_stocks = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META']
    stock_symbol = st.text_input("Enter a stock symbol:", value="").upper()
    
    logging.info(f"Initial stock_symbol input: {stock_symbol}")
    
    if not stock_symbol:
        stock_symbol = random.choice(default_stocks)
        logging.info(f"Randomly selected stock_symbol: {stock_symbol}")
    
    if stock_symbol:
        try:
            logging.info(f"Fetching data for stock_symbol: {stock_symbol}")
            # Fetch stock data
            stock_data = get_advanced_stock_data(stock_symbol)
            stock_info = get_stock_info(stock_symbol)
            
            logging.info(f"Data fetched for stock_symbol: {stock_symbol}")

            if stock_data is not None and stock_info is not None:
                # Display stock name and symbol
                st.header(f"{stock_symbol} - {stock_info['longName']}")

                # Rest of the code remains unchanged
                # ...

        except InvalidStockSymbolError as ise:
            st.error(str(ise))
            logging.error(f"Invalid stock symbol: {stock_symbol}")
        except socket.error as se:
            st.error(f"Network error occurred: {str(se)}")
            logging.error(f"Socket error: {str(se)}")
            logging.error(f"Traceback: {traceback.format_exc()}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")
            logging.error(f"Unexpected error: {str(e)}")
            logging.error(f"Traceback: {traceback.format_exc()}")

# Rest of the main.py file remains unchanged
# ...
