import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import json
import requests
from imessage_sender import send_imessage  # Import the iMessage sender function
from google_news import fetch_google_news_summary  # Import the Google Custom Search news summary function
from bedrock_claude import summarize_news_with_claude  # Import the Claude summarizer function

# Replace with your actual Finnhub API key (free tier available) -- for reference only
FINNHUB_API_KEY = ""
FINNHUB_BASE_URL = "https://finnhub.io/api/v1"

def fetch_stock_data(ticker, period="1y"):
    """
    Fetch stock data for the given ticker symbol using yfinance.
    For NSE stocks (tickers ending in '.NS'), using yf.download avoids the region issue.
    """
    try:
        data = yf.download(ticker, period=period, progress=False)
        # if data.empty:
        #     print(f"[WARNING] No data returned for ticker '{ticker}'. Check the ticker symbol and region settings.")
        # else:
        #     print(f"[DEBUG] Successfully fetched data for ticker '{ticker}', retrieved {len(data)} rows.")
        return data
    except Exception as err:
        print(f"[ERROR] Exception occurred while fetching data for ticker '{ticker}': {err}")
        raise

def fetch_stock_news(ticker):
    """
    (Deprecated for now)
    Fetch the latest news for the given ticker symbol from the Finnhub API.
    For NSE stocks, the symbol is prefixed with "NSE:" for Finnhub.
    """
    if ticker.endswith(".NS"):
        symbol = f"NSE:{ticker.replace('.NS', '')}"
    else:
        symbol = ticker

    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    url = f"{FINNHUB_BASE_URL}/company-news"
    params = {
        'symbol': symbol,
        'from': yesterday.strftime("%Y-%m-%d"),
        'to': today.strftime("%Y-%m-%d"),
        'token': FINNHUB_API_KEY
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        news_data = response.json()
        return news_data
    except Exception as e:
        print(f"Error fetching news for {ticker}: {str(e)}")
        return []

# ----------------- Improved Recommendation and Analysis -----------------

def compute_RSI(data, period=14):
    """
    Computes the Relative Strength Index (RSI) for the provided data.
    'data' is a pandas DataFrame with a "Close" column.
    """
    delta = data['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def compute_news_sentiment(news):
    """
    Dummy sentiment function.
    Returns +0.5 if any news headlines exist; otherwise, returns 0.0.
    """
    if news and isinstance(news, list) and len(news) > 0:
        return 0.5  
    else:
        return 0.0

def improved_recommendation(data, news):
    """
    Combines several technical signals and news sentiment to produce a recommendation.
    
    Signals:
      - RSI: Oversold (<30, +signal) or overbought (>70, -signal)
      - Moving Average Crossover: 10-day vs. 20-day MA
      - Momentum: % change over the last 5 days
      - Volume Spike: Current volume > 1.5x the 20-day average
      - News Sentiment: Dummy sentiment score
     
    Returns a tuple: (recommendation, rsi_value)
    """
    technical_score = 0

    # RSI signal
    rsi_value = compute_RSI(data, period=14)
    if rsi_value < 30:
        technical_score += 1
    elif rsi_value > 70:
        technical_score -= 1

    # Moving Averages signal (10-day vs. 20-day)
    if len(data) >= 20:
        short_ma = data['Close'].rolling(window=10).mean().iloc[-1]
        long_ma = data['Close'].rolling(window=20).mean().iloc[-1]
        if short_ma > long_ma:
            technical_score += 1
        else:
            technical_score -= 1

    # Momentum signal (5-day price change)
    if len(data) >= 5:
        momentum = (data['Close'].iloc[-1] - data['Close'].iloc[-5]) / data['Close'].iloc[-5]
        if momentum > 0.05:
            technical_score += 1
        elif momentum < -0.05:
            technical_score -= 1

    # Volume Spike signal
    if len(data) >= 20:
        current_volume = data['Volume'].iloc[-1]
        avg_volume = data['Volume'].rolling(window=20).mean().iloc[-1]
        if current_volume > 1.5 * avg_volume:
            technical_score += 1

    # News Sentiment signal
    news_sentiment = compute_news_sentiment(news)

    overall_score = technical_score + news_sentiment

    if overall_score >= 2:
        recommendation = "Buy"
    elif overall_score <= -2:
        recommendation = "Sell"
    else:
        recommendation = "Hold"

    return recommendation, rsi_value

def analyze_stock(data):
    """
    Computes analysis metrics over the yfinance data.
    
    Returns a dictionary containing:
         - current_price
         - price_change: Difference between the current price and the price 1 year ago
         - percent_change: Percentage change over the past year
         - high_52week: Highest price over the past year
         - low_52week:  Lowest price over the past year
         - avg_volume:  Average volume over the past year
    """
    if data.empty:
        raise ValueError("No data available for analysis")
    current_price = data['Close'].iloc[-1]
    start_price = data['Close'].iloc[0]
    price_change = current_price - start_price
    percent_change = (price_change / start_price) * 100 if start_price != 0 else 0
    high_52week = data['High'].max()
    low_52week = data['Low'].min()
    avg_volume = data['Volume'].mean()

    return {
        'current_price': round(current_price, 2),
        'price_change': round(price_change, 2),
        'percent_change': round(percent_change, 2),
        'high_52week': round(high_52week, 2),
        'low_52week': round(low_52week, 2),
        'avg_volume': int(avg_volume)
    }

# -----------------------------------------------------------------------

def main(tickers, mobile_number, exchange=None, google_api_key=None, google_cx=None):
    print("Welcome to the Stock Market Agent!")
    
    # Determine the currency symbol based on the exchange.
    currency_mapping = {
         'nse': "₹",
         'nasdaq': "$",
         'nyse': "$",
         'lse': "£"
    }
    currency_symbol = currency_mapping.get(exchange.lower() if exchange else "", "$")
    
    report = ""
    for ticker in tickers:
        ticker = ticker.strip()
        # If exchange is NSE, append .NS if not already included.
        if exchange and exchange.lower() == "nse":
            if not ticker.endswith(".NS"):
                ticker = f"{ticker}.NS"
            
        try:
            data = fetch_stock_data(ticker)
            # Commenting out the Finnhub API news call:
            # news = fetch_stock_news(ticker)

            # Fetch detailed news articles using the Google Custom Search API.
            # def fetch_google_news_summary(query, api_key, cx, num=3, model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0", temperature=0.7):
            news_summaries = fetch_google_news_summary(ticker, google_api_key, google_cx, num=3)
            
            recommendation, rsi_value = improved_recommendation(data, news_summaries)
            analysis = analyze_stock(data)
            
            line = f"{ticker}:\n"
            line += f"Recommendation: {recommendation}, RSI: {rsi_value:.2f}\n"
            line += f"Current Price: {currency_symbol}{analysis['current_price']:.2f}\n"
            line += (f"52-Week Change: {currency_symbol}{analysis['price_change']:.2f} "
                     f"({analysis['percent_change']:.2f}%)\n")
            # For non-NSE stocks, include 52-week high and low.
            if not (exchange and exchange.lower() == "nse"):
                line += f"52-Week High: {currency_symbol}{analysis['high_52week']:.2f}\n"
                line += f"52-Week Low: {currency_symbol}{analysis['low_52week']:.2f}\n"
            line += f"Average Volume: {analysis['avg_volume']:,}\n"

            # Append the list of news summaries.
            if news_summaries:
                line += "News Summaries:\n"
                for i, summary in enumerate(news_summaries, start=1):
                    line += f"   {i}. {summary}\n"
            else:
                line += "News Summary: No relevant news found.\n"
            line += "\n"
            
            print(line.strip())
            report += line
        except Exception as e:
            error_message = f"{ticker}: Error - {str(e)}\n"
            print(error_message.strip())
            report += error_message

    # Send the compiled report via iMessage if a mobile number is provided.
    if mobile_number:
        print("Sending report via iMessage...")
        if send_imessage(report, mobile_number):
            print("Report sent successfully via iMessage.")
        else:
            print("Failed to send report via iMessage. Please check your iMessage configuration.")
    else:
        print("No mobile number provided. Skipping iMessage sending.")

if __name__ == "__main__":
    # Read configuration from the provided file.
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            config = json.load(f)
        tickers = config.get('tickers', [])
        mobile_number = config.get('mobile_number', None)
        exchange = config.get('exchange', None)
        google_api_key = config.get('google_api_key', None)
        google_cx = config.get('google_cx', None)
    else:
        # Defaults if no config provided:
        tickers = ['RELIANCE', 'ITC', 'TCS', 'HDFCBANK', 'INFY']
        mobile_number = None
        exchange = None
        google_api_key = None
        google_cx = None

    main(tickers, mobile_number, exchange, google_api_key, google_cx) 