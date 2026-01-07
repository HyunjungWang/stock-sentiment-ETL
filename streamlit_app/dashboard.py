import streamlit as st
import psycopg2
import matplotlib.pyplot as plt
import pandas as pd
import os  
from datetime import datetime


DB_NAME = os.getenv('DB_NAME', 'stock_data')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASSWORD', 'password123')
DB_HOST = os.getenv('DB_HOST', 'db')  
DB_PORT = os.getenv('DB_PORT', '5432')

def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )

def get_sentiment_counts(stock_ticker, source):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT sentiment, COUNT(*) 
            FROM stock_sentiment 
            WHERE stock_ticker = %s AND source = %s
            GROUP BY sentiment;
        """
        cursor.execute(query, (stock_ticker, source))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return dict(results)
    except Exception as e:
        st.error(f"Sentiment DB Error: {e}")
        return {}

def get_price_data(stock_ticker):
    try:
        conn = get_connection()
        query = """
            SELECT price_date, open_price, high_price, low_price, close_price
            FROM stock_prices
            WHERE stock_ticker = %s
            ORDER BY price_date ASC;
        """
        df = pd.read_sql_query(query, conn, params=(stock_ticker,))
        conn.close()
        return df
    except Exception as e:
        st.error(f"Price DB Error: {e}")
        return pd.DataFrame()

st.set_page_config(page_title="Stock Sentiment Dashboard", layout="centered")
st.title("📊 Stock Sentiment Dashboard")

stock_ticker = st.selectbox("Choose a stock:", ["TSLA", "NVDA", "PLTR"])

newsapi_sentiments = get_sentiment_counts(stock_ticker, "NewsAPI")
stock_prices = get_price_data(stock_ticker)

st.subheader(f"Sentiment from NewsAPI for {stock_ticker}")
if newsapi_sentiments:
    extraction_date = datetime.now().strftime('%Y-%m-%d')
    st.write(f"Sentiment Data Extracted on: {extraction_date}")

    fig, ax = plt.subplots(figsize=(6, 1.8))
    labels = newsapi_sentiments.keys()
    sizes = newsapi_sentiments.values()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    ax.axis('equal')
    st.pyplot(fig)
else:
    st.warning(f"No sentiment data found for {stock_ticker} from NewsAPI.")

st.markdown("---")
col1, spacer, col2 = st.columns([1, 0.1, 1])
with col1:
    st.subheader(f"Stock Prices for {stock_ticker}")
    if not stock_prices.empty:
        st.dataframe(stock_prices, use_container_width=True)
    else:
        st.info("No price data table available.")

with col2:
    st.subheader(f"Closing Price Trend")
    if not stock_prices.empty:
        fig, ax = plt.subplots(figsize=(11, 6))
        ax.plot(stock_prices['price_date'], stock_prices['close_price'], marker='o', linestyle='-', color='b')
        ax.set_xlabel('Date')
        ax.set_ylabel('Close Price')
        ax.grid(True)
        st.pyplot(fig)
    else:
        st.info("No price trend chart available.")