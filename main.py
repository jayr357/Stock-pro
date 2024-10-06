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
import socket
import traceback
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

initialize_db()

st.set_page_config(page_title="Stock Data Visualization", page_icon="assets/favicon.svg", layout="wide")

st.title("Stock Data Retrieval and Visualization Tool")

tab1, tab2, tab3 = st.tabs(["Stock Analysis", "Economic Indicators", "Watchlist"])

with tab1:
    stock_symbol = st.text_input("Enter a stock symbol:").upper()
    
    if stock_symbol:
        try:
            logging.info(f"Fetching data for stock_symbol: {stock_symbol}")
            stock_info = get_stock_info(stock_symbol)
            
            logging.info(f"Data fetched for stock_symbol: {stock_symbol}")

            if stock_info is not None:
                st.header(f"{stock_symbol} - {stock_info['longName']}")

                st.subheader("Financial Metrics")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Market Cap", f"${stock_info['marketCap']:,.0f}" if isinstance(stock_info['marketCap'], (int, float)) and stock_info['marketCap'] is not None else "N/A")
                col2.metric("P/E Ratio", f"{stock_info['trailingPE']:.2f}" if isinstance(stock_info['trailingPE'], (int, float)) else "N/A")
                col3.metric("EPS", f"${stock_info['trailingEps']:.2f}" if isinstance(stock_info['trailingEps'], (int, float)) else "N/A")
                col4.metric("Dividend Yield", f"{stock_info['dividendYield']*100:.2f}%" if isinstance(stock_info['dividendYield'], (int, float)) else "N/A")

                st.subheader("Stock Price Chart")
                time_period = st.selectbox("Select time period", ["1m", "5m", "15m", "30m", "1hr", "24hr", "3month", "1year"])
                try:
                    chart_data = get_advanced_stock_data(stock_symbol, period=time_period)
                    
                    show_support = st.checkbox("Show Support Line", value=True)
                    show_resistance = st.checkbox("Show Resistance Line", value=True)
                    
                    if chart_data is not None and not chart_data.empty:
                        fig = go.Figure()
                        fig.add_trace(go.Candlestick(
                            x=chart_data.index,
                            open=chart_data['Open'],
                            high=chart_data['High'],
                            low=chart_data['Low'],
                            close=chart_data['Close'],
                            name="Price"
                        ))

                        if show_support:
                            fig.add_hline(y=chart_data['Support'].iloc[0], line_dash="dash", line_color="green", annotation_text="Support")
                        if show_resistance:
                            fig.add_hline(y=chart_data['Resistance'].iloc[0], line_dash="dash", line_color="red", annotation_text="Resistance")

                        fig.update_layout(height=600, title=f"{stock_symbol} Stock Price")
                        st.plotly_chart(fig, use_container_width=True)

                        csv = convert_to_csv(chart_data)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name=f"{stock_symbol}_stock_data.csv",
                            mime="text/csv"
                        )
                    else:
                        st.warning(f"No data available for {stock_symbol} with the selected time period.")
                except InvalidStockSymbolError as ise:
                    st.error(f"Error: {str(ise)}")
                    logging.error(f"Error fetching chart data: {str(ise)}")
                except Exception as e:
                    st.error(f"An unexpected error occurred while fetching chart data: {str(e)}")
                    logging.error(f"Unexpected error fetching chart data: {str(e)}")
                    logging.error(traceback.format_exc())

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

        except InvalidStockSymbolError as ise:
            st.error(f"Error: {str(ise)} Examples of valid symbols: AAPL (Apple), GOOGL (Alphabet), MSFT (Microsoft).")
            logging.error(f"Invalid stock symbol: {stock_symbol}")
        except socket.error as se:
            st.error(f"Network error occurred: {str(se)}")
            logging.error(f"Socket error: {str(se)}")
            logging.error(f"Traceback: {traceback.format_exc()}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")
            logging.error(f"Unexpected error: {str(e)}")
            logging.error(f"Traceback: {traceback.format_exc()}")

# Rest of the code remains the same...
