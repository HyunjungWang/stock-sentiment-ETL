# Stock Sentiment Analysis & Visualization
This project analyzes stock-related news articles, performs sentiment analysis, fetches stock prices, stores the results in a PostgreSQL database, and provides an interactive data visualization dashboard using Streamlit. The project also leverages Airflow to automate the ETL pipeline.


Table of Contents
1. [Overview](#overview)
2. [Technologies](#technologies)
3. [Setup](#setup)
4. [ETL](#etl)
5. [Visualization](#visualization)


## Overview
This project involves multiple components that interact together:

- News Article Sentiment Analysis: Fetches news articles about a specific stock using an external API (NewsAPI), performs sentiment analysis on these articles, and categorizes them into positive, negative, or neutral sentiments.

- PostgreSQL Database: Sentiment data and stock price information are stored in a PostgreSQL database for easy retrieval and further analysis.

- Stock Market Price: Fetches stock market prices using the Yahoo Finance API.

- Streamlit Dashboard: An interactive dashboard built using Streamlit visualizes sentiment analysis results and stock price trends.

- ETL Pipeline with Apache Airflow: Airflow orchestrates the extraction, transformation, and loading (ETL) process, fetching news articles, performing sentiment analysis, and storing the results in the database.

## Technologies
- **Backend**: Python (requests, psycopg2, pandas, yfinance, vaderSentiment)
- **ETL Tool**: Apache Airflow
- **Database**: PostgreSQL
- **Visualization**: Streamlit, Matplotlib
- **Infrastructure**: Docker, Docker Compose
- **API**: NewsAPI

## 🐳 Setup with Docker (Recommended)
The easiest way to run this project is using **Docker Compose**. It sets up the Database, Airflow, and Streamlit environment automatically.

### 1. Prerequisites
- [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/) installed.

### 2. Environment Variables
Create a `.env` file in the root directory and add your API key:
```ini
NEWS_API_KEY=your_news_api_key_here
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow
POSTGRES_DB=airflow
```
### 3. Run the containers

```
# Build and start all services
docker-compose up -d
```

### 4. Access the Services
4. Access the Services
- Airflow Web UI: http://localhost:8080 (Default Login: airflow / airflow)

- Streamlit Dashboard: http://localhost:8501



## ETL Pipeline (Airflow)
The ETL pipeline is managed by Airflow, orchestrating the following automated tasks:

1. **Extract** 
   - Fetches the latest news articles related to the ticker via **NewsAPI**.
   - Retrieves historical stock price data (last 5 days) via **yfinance**.

2. **Transform** 
   - Analyzes news headlines and snippets using the **VADER** sentiment tool.
   - Calculates sentiment scores and labels them as **Positive**, **Negative**, or **Neutral**.

3. **Load** 
   - Cleans and formats the data for database compatibility.
   - Inserts processed results into `stock_sentiment` and `stock_prices` tables in **PostgreSQL**.

4. **Airflow DAG**:
  ![Image](https://github.com/user-attachments/assets/3effedd8-cbb9-4597-a282-ea6f1154406b)

## Visualization
Start Streamlit Dashboard: After the ETL process loads data into the PostgreSQL database, you can run the Streamlit dashboard to visualize the data:
```
streamlit run dashboard.py
```
---
![Image](https://github.com/user-attachments/assets/429d58e8-8777-4cf6-b078-04c3816ce87a)

---
### 1. Sentiment Pie Chart

The **Sentiment Pie Chart** displays the sentiment distribution of news articles related to the selected stock ticker. It shows three types of sentiments:

- **Positive**: Articles that express a positive outlook on the stock.
- **Neutral**: Articles with a neutral sentiment, without a clear positive or negative bias.
- **Negative**: Articles that express a negative view on the stock.

#### How to interpret:
- A larger segment in the pie chart indicates a dominant sentiment from the news articles, giving you an overall sense of how the news is affecting the stock sentiment.
  
For example, if the pie chart shows 60% positive sentiment, this means that 60% of the articles analyzed are positive about the stock.

### 2. Stock Price Table

The **Stock Price Table** shows the most recent stock prices, including the following data points:

- **Date**: The date the stock data was recorded.
- **Open**: The opening price of the stock for the day.
- **High**: The highest price the stock reached during the day.
- **Low**: The lowest price the stock reached during the day.
- **Close**: The final price at which the stock closed for the day.

#### How to interpret:
- This table helps you track the stock's historical performance in terms of daily price movements.
- You can analyze the daily volatility by looking at the difference between the `High` and `Low` prices, or see if the stock is generally trending upwards or downwards by comparing the `Open` and `Close` values.

### 3. Stock Closing Price Line Chart

The **Stock Closing Price Line Chart** visualizes the trend of the stock's **closing price** over time. It shows how the stock price has evolved over the past few days.

#### How to interpret:
- The line chart displays the stock's closing price for each trading day. You can visually analyze the trend (whether the stock price is increasing, decreasing, or staying stable).
- The x-axis represents the **date**, and the y-axis represents the **closing price** of the stock on that date.
- This chart is helpful in identifying patterns, such as upward or downward trends in the stock's performance, or to see how news and sentiment may have affected the price over time.

---

By using these visualizations together, you can gain insights into both the market sentiment (through the pie chart) and the stock's performance (through the table and line chart), which helps in making more informed decisions.
