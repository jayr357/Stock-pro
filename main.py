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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

initialize_db()

st.set_page_config(page_title="Stock Data Visualization", page_icon="assets/favicon.svg", layout="wide")

st.title("Stock Data Retrieval and Visualization Tool")

tab1, tab2, tab3 = st.tabs(["Stock Analysis", "Economic Indicators", "Watchlist"])

with tab1:
    default_stocks = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META']
    stock_symbol = st.text_input("Enter a stock symbol:", value="").upper()
    
    logging.info(f"Initial stock_symbol input: {stock_symbol}")
    
    if not stock_symbol:
        stock_symbol = random.choice(default_stocks)
        logging.info(f"Randomly selected stock_symbol: {stock_symbol}")
    
    if stock_symbol:
        try:
            logging.info(f"Fetching data for stock_symbol: {stock_symbol}")
            stock_data = get_advanced_stock_data(stock_symbol)
            stock_info = get_stock_info(stock_symbol)
            
            logging.info(f"Data fetched for stock_symbol: {stock_symbol}")

            if stock_data is not None and stock_info is not None:
                st.header(f"{stock_symbol} - {stock_info['longName']}")

                st.subheader("Financial Metrics")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Market Cap", f"${stock_info['marketCap']:,.0f}" if isinstance(stock_info['marketCap'], (int, float)) and stock_info['marketCap'] is not None else "N/A")
                col2.metric("P/E Ratio", f"{stock_info['trailingPE']:.2f}" if isinstance(stock_info['trailingPE'], (int, float)) else "N/A")
                col3.metric("EPS", f"${stock_info['trailingEps']:.2f}" if isinstance(stock_info['trailingEps'], (int, float)) else "N/A")
                col4.metric("Dividend Yield", f"{stock_info['dividendYield']*100:.2f}%" if isinstance(stock_info['dividendYield'], (int, float)) else "N/A")

                st.subheader("Stock Price Chart with Advanced Indicators")
                time_period = st.selectbox("Select time period", ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"])
                chart_data = get_advanced_stock_data(stock_symbol, period=time_period)
                
                if chart_data is not None and not chart_data.empty:
                    fig = make_subplots(rows=5, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.5, 0.1, 0.1, 0.1, 0.1])

                    fig.add_trace(go.Candlestick(
                        x=chart_data.index,
                        open=chart_data['Open'],
                        high=chart_data['High'],
                        low=chart_data['Low'],
                        close=chart_data['Close'],
                        name="Price"
                    ), row=1, col=1)

                    fig.update_layout(height=1200, title=f"{stock_symbol} Stock Price and Indicators")
                    st.plotly_chart(fig, use_container_width=True)

                st.subheader("Correlation Matrix")
                correlation_matrix = chart_data[['Close', 'Volume', 'MACD', 'RSI', 'SMA_50', 'SMA_200', 'BB_Upper', 'BB_Lower']].corr()
                fig_corr = go.Figure(data=go.Heatmap(z=correlation_matrix.values,
                                                     x=correlation_matrix.index,
                                                     y=correlation_matrix.columns,
                                                     colorscale='Viridis'))
                fig_corr.update_layout(height=600, width=800)
                st.plotly_chart(fig_corr)

                csv = convert_to_csv(stock_data)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"{stock_symbol}_stock_data.csv",
                    mime="text/csv"
                )

                if st.button("Add to Watchlist"):
                    save_stock_to_db(stock_symbol)
                    st.success(f"Added {stock_symbol} to your watchlist!")

                st.subheader("Recent News Articles with Sentiment Analysis")
                news_articles = get_news_articles(stock_symbol)
                news_articles_with_sentiment = analyze_news_sentiment(news_articles)
                for article in news_articles_with_sentiment[:5]:
                    st.markdown(f"[{article['title']}]({article['url']})")
                    st.write(article['description'])
                    if 'sentiment' in article:
                        sentiment = article['sentiment']
                        st.write(f"Sentiment: Positive: {sentiment['pos']:.2f}, Negative: {sentiment['neg']:.2f}, Neutral: {sentiment['neu']:.2f}")
                        st.progress(sentiment['compound'] + 1, text="Sentiment Score")
                    st.write("---")

            else:
                st.error(f"Unable to fetch data for {stock_symbol}. Please check the stock symbol and try again.")

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

with tab2:
    st.header("Economic Indicators")
    
    try:
        indicators = get_relevant_economic_indicators(stock_symbol)
        fred = Fred(api_key=st.secrets["FRED_API_KEY"])
        indicator_data = get_economic_indicators(indicators)
        
        for indicator, data in indicator_data.items():
            st.subheader(f"{indicator} - {fred.get_series_info(indicator).title}")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=data.index, y=data.values, mode='lines', name=indicator))
            fig.update_layout(height=400, title=f"{indicator} Over Time")
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"An error occurred while fetching economic indicators: {str(e)}")
        logging.error(f"Error in economic indicators: {str(e)}")
        logging.error(f"Traceback: {traceback.format_exc()}")

with tab3:
    st.header("Your Watchlist")
    
    new_stocks = st.text_input("Add multiple stocks (comma-separated)", "e.g., TSLA, NVDA, JPM, DIS, NFLX")
    if st.button("Add Stocks"):
        new_stock_list = [stock.strip().upper() for stock in new_stocks.split(',') if stock.strip()]
        for new_stock in new_stock_list:
            save_stock_to_db(new_stock)
        st.success(f"Added {len(new_stock_list)} stocks to your watchlist!")
        st.rerun()

    user_stocks = get_user_stocks()
    if user_stocks:
        for stock in user_stocks:
            try:
                stock_info = get_stock_info(stock)
                if stock_info:
                    col1, col2, col3 = st.columns([3, 2, 1])
                    col1.subheader(f"{stock} - {stock_info['longName']}")
                    
                    current_price = stock_info.get('currentPrice', 'N/A')
                    percent_change = stock_info.get('percentChange', 'N/A')
                    
                    price_display = f"${current_price:.2f}" if isinstance(current_price, (int, float)) else str(current_price)
                    change_display = f"{percent_change:.2f}%" if isinstance(percent_change, (int, float)) else str(percent_change)
                    
                    col2.metric("Price", price_display, change_display)
                    
                    if col3.button("Remove", key=f"remove_{stock}"):
                        remove_stock_from_db(stock)
                        st.success(f"Removed {stock} from your watchlist!")
                        st.rerun()
                    
                    st.write(f"Sector: {stock_info.get('sector', 'N/A')}")
                    st.write(f"Industry: {stock_info.get('industry', 'N/A')}")
                    st.write("---")
            except InvalidStockSymbolError as ise:
                st.error(f"Error fetching data for {stock}: {str(ise)}")
                logging.error(f"Invalid stock symbol in watchlist: {stock}")
    else:
        st.write("Your watchlist is empty. Add stocks to track them.")

st.sidebar.title("About")
st.sidebar.info("This app allows you to retrieve and visualize stock data, track stocks, view related news articles with sentiment analysis, and analyze economic indicators.")

st.sidebar.title("User Guide")
if st.sidebar.button("View User Guide"):
    with open("Dear_user.py", "r") as f:
        user_guide = f.read()
    st.sidebar.text_area("Dear User", user_guide, height=300)
