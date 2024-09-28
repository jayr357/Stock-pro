import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from stock_data import get_advanced_stock_data, get_stock_info
from news_scraper import get_news_articles
from database import initialize_db, save_stock_to_db, get_user_stocks, remove_stock_from_db
from utils import convert_to_csv

# Initialize the database
initialize_db()

st.set_page_config(page_title="Stock Data Visualization", page_icon="assets/favicon.svg", layout="wide")

st.title("Stock Data Retrieval and Visualization Tool")

# Create tabs for different sections
tab1, tab2 = st.tabs(["Stock Analysis", "Watchlist"])

with tab1:
    # User input for stock symbol
    stock_symbol = st.text_input("Enter a stock symbol (e.g., AAPL):", value="AAPL").upper()

    if stock_symbol:
        # Fetch stock data
        stock_data = get_advanced_stock_data(stock_symbol)
        stock_info = get_stock_info(stock_symbol)

        if stock_data is not None and stock_info is not None:
            # Display stock name and symbol
            st.header(f"{stock_symbol} - {stock_info['longName']}")

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
                try:
                    # Convert all relevant columns to float
                    numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'MACD', 'Signal', 'Histogram', 'RSI', 'BB_Upper', 'BB_Middle', 'BB_Lower', 'SMA_50', 'SMA_200']
                    for col in numeric_columns:
                        if col in chart_data.columns:
                            chart_data[col] = pd.to_numeric(chart_data[col], errors='coerce')

                    # Convert Fibonacci columns to float
                    fib_columns = [col for col in chart_data.columns if col.startswith('Fib_')]
                    for col in fib_columns:
                        chart_data[col] = pd.to_numeric(chart_data[col], errors='coerce')

                    fig = make_subplots(rows=5, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.5, 0.1, 0.1, 0.1, 0.1])

                    # Candlestick chart
                    fig.add_trace(go.Candlestick(
                        x=chart_data.index,
                        open=chart_data['Open'],
                        high=chart_data['High'],
                        low=chart_data['Low'],
                        close=chart_data['Close'],
                        name="Price"
                    ), row=1, col=1)

                    # Bollinger Bands
                    fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['BB_Upper'], name="BB Upper", line=dict(color="rgba(173, 204, 255, 0.7)", width=1)), row=1, col=1)
                    fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['BB_Middle'], name="BB Middle", line=dict(color="rgba(173, 204, 255, 0.7)", width=1)), row=1, col=1)
                    fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['BB_Lower'], name="BB Lower", line=dict(color="rgba(173, 204, 255, 0.7)", width=1)), row=1, col=1)

                    # Fibonacci Retracement
                    fib_colors = ['rgba(128, 0, 128, 0.3)', 'rgba(0, 0, 255, 0.3)', 'rgba(0, 128, 0, 0.3)', 'rgba(255, 165, 0, 0.3)', 'rgba(255, 0, 0, 0.3)']
                    for i, level in enumerate([0.236, 0.382, 0.5, 0.618, 1]):
                        fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data[f'Fib_{int(level*100)}'], name=f"Fib {level}", line=dict(color=fib_colors[i], width=1, dash='dash')), row=1, col=1)

                    # SMA
                    fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['SMA_50'], name="50-day SMA", line=dict(color="#00FFFF", width=1)), row=1, col=1)
                    fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['SMA_200'], name="200-day SMA", line=dict(color="#FF1493", width=1)), row=1, col=1)

                    # SMA Crossover
                    crossover_points = chart_data[chart_data['SMA_Crossover']]
                    fig.add_trace(go.Scatter(x=crossover_points.index, y=crossover_points['Close'], mode='markers', name="SMA Crossover", marker=dict(symbol='star', size=15, color='#FFFF00', line=dict(width=2, color='#000000'))), row=1, col=1)

                    # Volume
                    fig.add_trace(go.Bar(x=chart_data.index, y=chart_data['Volume'], name="Volume", marker_color='#00CED1'), row=2, col=1)

                    # MACD
                    fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['MACD'], name="MACD", line=dict(color="#00FA9A")), row=3, col=1)
                    fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['Signal'], name="Signal", line=dict(color="#FF69B4")), row=3, col=1)
                    fig.add_trace(go.Bar(x=chart_data.index, y=chart_data['Histogram'], name="Histogram", marker_color='#1E90FF'), row=3, col=1)

                    # RSI
                    fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['RSI'], name="RSI", line=dict(color="#FFA500")), row=4, col=1)
                    fig.add_hline(y=70, line_dash="dash", line_color="#FF0000", row=4, col=1)
                    fig.add_hline(y=30, line_dash="dash", line_color="#00FF00", row=4, col=1)

                    fig.update_layout(
                        height=1200,
                        title=f"{stock_symbol} Stock Price and Indicators",
                        xaxis_title="Date",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='#FFFFFF',
                        title_font_color='#FFFFFF',
                        legend_title_font_color='#FFFFFF',
                        legend_font_color='#FFFFFF',
                        xaxis=dict(linecolor='#FF00FF', gridcolor='#333333'),
                        yaxis=dict(linecolor='#FF00FF', gridcolor='#333333')
                    )

                    fig.update_xaxes(rangeslider_visible=False)
                    st.plotly_chart(fig, use_container_width=True)

                    # Display correlation matrix
                    st.subheader("Correlation Matrix")
                    correlation_matrix = chart_data[['Close', 'Volume', 'MACD', 'RSI', 'SMA_50', 'SMA_200', 'BB_Upper', 'BB_Lower']].corr()
                    fig_corr = go.Figure(data=go.Heatmap(z=correlation_matrix.values,
                                                         x=correlation_matrix.index,
                                                         y=correlation_matrix.columns,
                                                         colorscale='Viridis'))
                    fig_corr.update_layout(height=600, width=800)
                    st.plotly_chart(fig_corr)

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
            if st.button("Add to Watchlist"):
                save_stock_to_db(stock_symbol)
                st.success(f"Added {stock_symbol} to your watchlist!")

            # Display news articles
            st.subheader("Recent News Articles")
            news_articles = get_news_articles(stock_symbol)
            for article in news_articles[:5]:  # Display top 5 articles
                st.markdown(f"[{article['title']}]({article['url']})")
                st.write(article['description'])
                st.write("---")

            # Company Overview and Description (moved to the end)
            st.subheader("Company Overview")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"| **Founded**: {stock_info['founded']} |")
                st.markdown("| **Target Markets**: |")
                st.markdown(f"| - {stock_info['sector']} |")
                st.markdown(f"| - {stock_info['industry']} |")
                st.markdown("| **Sales Channels**: |")
                st.markdown("| - Retail stores |")
                st.markdown("| - Online |")
                st.markdown("| - Direct sales |")
                st.markdown("| - Third-party carriers, retailers |")

            with col2:
                products = stock_info['products'].split(',')[:5] if isinstance(stock_info['products'], str) else ['N/A']
                st.markdown("| **Main Products**: |")
                for product in products:
                    st.markdown(f"| - {product.strip()} |")
                
                st.markdown("| **Software Ecosystem**: |")
                st.markdown("| - N/A |")
                st.markdown("| - N/A |")
                st.markdown("| - N/A |")
                
                st.markdown("| **Additional Services**: |")
                st.markdown(f"| - Website: {stock_info['website']} |")
                st.markdown(f"| - Employees: {stock_info['fullTimeEmployees']} |")
                st.markdown("| - N/A |")

            # Sector Contribution Pie Chart
            if 'sector_contribution' in stock_info and stock_info['sector_contribution']:
                st.subheader("Sector Contribution")
                fig_sector = go.Figure(data=[go.Pie(labels=list(stock_info['sector_contribution'].keys()),
                                                    values=list(stock_info['sector_contribution'].values()))])
                fig_sector.update_layout(height=400, width=600)
                st.plotly_chart(fig_sector)

            st.subheader("Company Description")
            st.write(stock_info['longBusinessSummary'])

        else:
            st.error("Unable to fetch stock data. Please check the stock symbol and try again.")

with tab2:
    st.header("Your Watchlist")
    
    # Add multiple stocks to watchlist
    new_stocks = st.text_input("Add multiple stocks (comma-separated)", "")
    if st.button("Add Stocks"):
        new_stock_list = [stock.strip().upper() for stock in new_stocks.split(',') if stock.strip()]
        for new_stock in new_stock_list:
            save_stock_to_db(new_stock)
        st.success(f"Added {len(new_stock_list)} stocks to your watchlist!")
        st.rerun()

    # Display watchlist
    user_stocks = get_user_stocks()
    if user_stocks:
        for stock in user_stocks:
            stock_info = get_stock_info(stock)
            if stock_info:
                col1, col2, col3 = st.columns([3, 2, 1])
                col1.subheader(f"{stock} - {stock_info['longName']}")
                col2.metric("Price", f"${stock_info['currentPrice']:.2f}", f"{stock_info['percentChange']:.2f}%")
                if col3.button("Remove", key=f"remove_{stock}"):
                    remove_stock_from_db(stock)
                    st.success(f"Removed {stock} from your watchlist!")
                    st.rerun()
                
                # Additional stock information
                st.write(f"Sector: {stock_info['sector']}")
                st.write(f"Industry: {stock_info['industry']}")
                st.write(f"Market Cap: ${stock_info['marketCap']:,.0f}")
                st.write(f"52 Week High: ${stock_info.get('fiftyTwoWeekHigh', 'N/A')}")
                st.write(f"52 Week Low: ${stock_info.get('fiftyTwoWeekLow', 'N/A')}")
                st.write("---")
    else:
        st.write("Your watchlist is empty. Add stocks to track them.")

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
