import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from stock_data import get_stock_data, get_stock_info
from news_scraper import get_news_articles
from database import initialize_db, save_stock_to_db, get_user_stocks
from utils import convert_to_csv

# Initialize the database
initialize_db()

st.set_page_config(page_title="Stock Data Visualization", page_icon="assets/favicon.svg")

st.title("Stock Data Retrieval and Visualization Tool")

# User input for stock symbol
stock_symbol = st.text_input("Enter a stock symbol (e.g., AAPL):", value="AAPL").upper()

if stock_symbol:
    # Fetch stock data
    stock_data = get_stock_data(stock_symbol)
    stock_info = get_stock_info(stock_symbol)

    if stock_data is not None and stock_info is not None:
        # Display financial metrics
        st.subheader("Financial Metrics")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Market Cap", f"${stock_info['marketCap']:,.0f}" if isinstance(stock_info['marketCap'], (int, float)) else "N/A")
        col2.metric("P/E Ratio", f"{stock_info['trailingPE']:.2f}" if isinstance(stock_info['trailingPE'], (int, float)) else "N/A")
        col3.metric("EPS", f"${stock_info['trailingEps']:.2f}" if isinstance(stock_info['trailingEps'], (int, float)) else "N/A")
        col4.metric("Dividend Yield", f"{stock_info['dividendYield']*100:.2f}%" if isinstance(stock_info['dividendYield'], (int, float)) else "N/A")

        # Stock price chart
        st.subheader("Stock Price Chart")
        time_period = st.selectbox("Select time period", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"])
        chart_data = get_stock_data(stock_symbol, period=time_period)
        
        fig = go.Figure(data=[go.Candlestick(x=chart_data.index,
                                             open=chart_data['Open'],
                                             high=chart_data['High'],
                                             low=chart_data['Low'],
                                             close=chart_data['Close'])])
        fig.update_layout(title=f"{stock_symbol} Stock Price", xaxis_title="Date", yaxis_title="Price")
        st.plotly_chart(fig)

        # Download CSV
        csv = convert_to_csv(stock_data)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"{stock_symbol}_stock_data.csv",
            mime="text/csv"
        )

        # Save stock to database
        if st.button("Track this stock"):
            save_stock_to_db(stock_symbol)
            st.success(f"Added {stock_symbol} to your tracked stocks!")

        # Display user's tracked stocks
        user_stocks = get_user_stocks()
        if user_stocks:
            st.subheader("Your Tracked Stocks")
            st.write(", ".join(user_stocks))

        # Display news articles
        st.subheader("Recent News Articles")
        news_articles = get_news_articles(stock_symbol)
        for article in news_articles[:5]:  # Display top 5 articles
            st.markdown(f"[{article['title']}]({article['url']})")
            st.write(article['description'])
            st.write("---")
    else:
        st.error("Unable to fetch stock data. Please check the stock symbol and try again.")

# Add some information about the app
st.sidebar.title("About")
st.sidebar.info("This app allows you to retrieve and visualize stock data, track stocks, and view related news articles.")
