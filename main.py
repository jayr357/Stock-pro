import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from stock_data import get_advanced_stock_data, get_stock_info
from news_scraper import get_news_articles
from database import initialize_db, save_stock_to_db, get_user_stocks
from utils import convert_to_csv

# Initialize the database
initialize_db()

st.set_page_config(page_title="Stock Data Visualization", page_icon="assets/favicon.svg", layout="wide")

st.title("Stock Data Retrieval and Visualization Tool")

# User input for stock symbol
stock_symbol = st.text_input("Enter a stock symbol (e.g., AAPL):", value="AAPL").upper()

if stock_symbol:
    # Fetch stock data
    stock_data = get_advanced_stock_data(stock_symbol)
    stock_info = get_stock_info(stock_symbol)

    if stock_data is not None and stock_info is not None:
        # Display financial metrics
        st.subheader("Financial Metrics")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Market Cap", f"${stock_info['marketCap']:,.0f}" if isinstance(stock_info['marketCap'], (int, float)) and stock_info['marketCap'] is not None else "N/A")
        col2.metric("P/E Ratio", f"{stock_info['trailingPE']:.2f}" if isinstance(stock_info['trailingPE'], (int, float)) else "N/A")
        col3.metric("EPS", f"${stock_info['trailingEps']:.2f}" if isinstance(stock_info['trailingEps'], (int, float)) else "N/A")
        col4.metric("Dividend Yield", f"{stock_info['dividendYield']*100:.2f}%" if isinstance(stock_info['dividendYield'], (int, float)) else "N/A")

        # Stock price chart with advanced indicators
        st.subheader("Stock Price Chart with Advanced Indicators")
        time_period = st.selectbox("Select time period", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"])
        chart_data = get_advanced_stock_data(stock_symbol, period=time_period)
        
        if chart_data is None or chart_data.empty:
            st.error(f"Unable to fetch data for {stock_symbol} for the selected time period. Please try a different time period or stock symbol.")
        else:
            print("Debug: chart_data shape:", chart_data.shape)
            print("Debug: chart_data columns:", chart_data.columns)
            print("Debug: chart_data types:", chart_data.dtypes)
            print("Debug: chart_data head:")
            print(chart_data.head())
            try:
                fig = make_subplots(rows=5, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.5, 0.1, 0.1, 0.1, 0.1])

                # Candlestick chart
                fig.add_trace(go.Candlestick(x=chart_data.index,
                                             open=chart_data['Open'],
                                             high=chart_data['High'],
                                             low=chart_data['Low'],
                                             close=chart_data['Close'],
                                             name="Price"), row=1, col=1)

                # Bollinger Bands
                fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['BB_Upper'], name="BB Upper", line=dict(color="gray", width=1)), row=1, col=1)
                fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['BB_Middle'], name="BB Middle", line=dict(color="gray", width=1)), row=1, col=1)
                fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['BB_Lower'], name="BB Lower", line=dict(color="gray", width=1)), row=1, col=1)

                # Fibonacci Retracement
                fib_colors = ['purple', 'blue', 'green', 'orange', 'red']
                for i, level in enumerate([0.236, 0.382, 0.5, 0.618, 1]):
                    fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data[f'Fib_{int(level*100)}'], name=f"Fib {level}", line=dict(color=fib_colors[i], width=1, dash='dash')), row=1, col=1)

                # SMA
                fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['SMA_50'], name="50-day SMA", line=dict(color="blue", width=1)), row=1, col=1)
                fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['SMA_200'], name="200-day SMA", line=dict(color="red", width=1)), row=1, col=1)

                # SMA Crossover
                crossover_points = chart_data[chart_data['SMA_Crossover']]
                fig.add_trace(go.Scatter(x=crossover_points.index, y=crossover_points['Close'], mode='markers', name="SMA Crossover", marker=dict(symbol='star', size=10, color='yellow', line=dict(width=2, color='black'))), row=1, col=1)

                # Volume
                fig.add_trace(go.Bar(x=chart_data.index, y=chart_data['Volume'], name="Volume"), row=2, col=1)

                # MACD
                fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['MACD'], name="MACD"), row=3, col=1)
                fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['Signal'], name="Signal"), row=3, col=1)
                fig.add_trace(go.Bar(x=chart_data.index, y=chart_data['Histogram'], name="Histogram"), row=3, col=1)

                # RSI
                fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['RSI'], name="RSI"), row=4, col=1)
                fig.add_hline(y=70, line_dash="dash", line_color="red", row="4", col="1")
                fig.add_hline(y=30, line_dash="dash", line_color="green", row="4", col="1")

                fig.update_layout(height=1200, title=f"{stock_symbol} Stock Price and Indicators", xaxis_title="Date")
                fig.update_xaxes(rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)

                # Display correlation matrix
                st.subheader("Correlation Matrix")
                correlation_matrix = chart_data[['Close', 'Volume', 'MACD', 'RSI', 'SMA_50', 'SMA_200']].corr()
                st.plotly_chart(go.Figure(data=go.Heatmap(z=correlation_matrix.values,
                                                          x=correlation_matrix.index,
                                                          y=correlation_matrix.columns,
                                                          colorscale='Viridis')))

            except Exception as e:
                st.error(f"Error creating chart: {str(e)}")
                print(f"Debug: Error creating chart: {str(e)}")
                print("Debug: chart_data columns:", chart_data.columns)
                print("Debug: First few rows of chart_data:")
                print(chart_data.head())

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
st.sidebar.info("This app allows you to retrieve and visualize stock data, track stocks, and view related news articles. It includes advanced financial indicators such as MACD, RSI, Bollinger Bands, Moving Averages, Fibonacci Retracement, and SMA Crossover.")

# Explanation of indicators
st.sidebar.title("Indicator Explanations")
st.sidebar.markdown("""
**Bollinger Bands:** These consist of a middle band being an N-period simple moving average (SMA), an upper band at K times an N-period standard deviation above the middle band, and a lower band at K times an N-period standard deviation below the middle band. Bollinger Bands help determine overbought and oversold conditions.

**MACD (Moving Average Convergence Divergence):** This indicator is calculated by subtracting the 26-period Exponential Moving Average (EMA) from the 12-period EMA. The MACD line is often displayed with a 9-day EMA of the MACD itself, called the "signal line". MACD helps to identify trending and momentum.

**RSI (Relative Strength Index):** This momentum indicator measures the magnitude of recent price changes to evaluate overbought or oversold conditions. It is displayed as an oscillator (a line graph that moves between two extremes) and can have a reading from 0 to 100. Traditional interpretation and usage of the RSI are that values of 70 or above indicate that a security is becoming overbought or overvalued, and may be primed for a trend reversal or corrective pullback in price. An RSI reading of 30 or below indicates an oversold or undervalued condition.

**Moving Averages:** These are used to smooth out price data and identify trends. The 50-day and 200-day simple moving averages are commonly used for medium-term and long-term trend analysis, respectively.

**Fibonacci Retracement:** This tool is based on the idea that markets will retrace a predictable portion of a move, after which they will continue to move in the original direction. The common Fibonacci retracement levels are 23.6%, 38.2%, 50%, 61.8%, and 100%.

**SMA Crossover:** This occurs when a shorter-term SMA (e.g., 50-day) crosses above or below a longer-term SMA (e.g., 200-day). A "golden cross" occurs when the shorter-term SMA crosses above the longer-term SMA, often considered a bullish signal. A "death cross" occurs when the shorter-term SMA crosses below the longer-term SMA, often considered a bearish signal.

**Correlation Matrix:** This heatmap shows the correlation between different indicators and the stock price. It helps in understanding how different metrics relate to each other and the overall stock performance.
""")
