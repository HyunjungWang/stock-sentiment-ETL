from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import psycopg2
import pandas as pd
import os
from airflow.providers.postgres.operators.postgres import PostgresOperator
import yfinance as yf 
DB_NAME = os.getenv('DB_NAME', 'stock_data')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASSWORD', 'password123')
DB_HOST = os.getenv('DB_HOST', 'stock_db')
DB_PORT = os.getenv('DB_PORT', '5432')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
POSTGRES_CONN_ID = 'postgres_default'
TICKERS = ['TSLA', 'NVDA', 'PLTR']

analyzer = SentimentIntensityAnalyzer()

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )

def analyze_sentiment_label(text):
    if not text: return 'Neutral'
    score = analyzer.polarity_scores(text)['compound']
    if score >= 0.05: return 'Positive'
    elif score <= -0.05: return 'Negative'
    return 'Neutral'

def fetch_and_load_prices(ticker):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        hist = yf.Ticker(ticker).history(period="7d")
        for date, row in hist.iterrows():
            cur.execute("""
                INSERT INTO stock_prices (stock_ticker, price_date, open_price, high_price, low_price, close_price, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (stock_ticker, price_date) DO NOTHING;
            """, (ticker, date.date(), row['Open'], row['High'], row['Low'], row['Close'], row['Volume']))
        conn.commit()
    finally:
        cur.close()
        conn.close()

def fetch_and_load_sentiment(ticker):
    url = f'https://newsapi.org/v2/everything?q={ticker}&apiKey={NEWS_API_KEY}&pageSize=10'
    response = requests.get(url).json()
    articles = response.get('articles', [])
    
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        for art in articles:
            title = art['title']
            sentiment = analyze_sentiment_label(title)
            cur.execute("""
                INSERT INTO stock_sentiment (stock_ticker, sentiment, source, content) 
                VALUES (%s, %s, %s, %s);
            """, (ticker, sentiment, 'NewsAPI', title))
        conn.commit()
    finally:
        cur.close()
        conn.close()

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2025, 12, 1),
}

with DAG(
    'stock_sentiment_etl_v3',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
    tags=['stock', 'sentiment']
) as dag:

    create_tables = PostgresOperator(
        task_id='create_tables',
        postgres_conn_id=POSTGRES_CONN_ID,
        sql='''
            CREATE TABLE IF NOT EXISTS stock_sentiment (
                id SERIAL PRIMARY KEY,
                stock_ticker VARCHAR(10),
                sentiment VARCHAR(10),
                source VARCHAR(50),
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS stock_prices (
                stock_ticker VARCHAR(10),
                price_date DATE,
                open_price NUMERIC,
                high_price NUMERIC,
                low_price NUMERIC,
                close_price NUMERIC,
                volume BIGINT,
                PRIMARY KEY (stock_ticker, price_date)
            );
        '''
    )

    for ticker in TICKERS:
        p_task = PythonOperator(
            task_id=f'fetch_price_{ticker.lower()}',
            python_callable=fetch_and_load_prices,
            op_kwargs={'ticker': ticker}
        )

        s_task = PythonOperator(
            task_id=f'fetch_sentiment_{ticker.lower()}',
            python_callable=fetch_and_load_sentiment,
            op_kwargs={'ticker': ticker}
        )

        create_tables >> [p_task, s_task]