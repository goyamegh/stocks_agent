import pandas as pd
import numpy as np

def compute_RSI(data, period=14):
    """
    Computes the Relative Strength Index (RSI) for the data provided.
    'data' must be a pandas DataFrame with a column named "Close".
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
    A dummy function for computing news sentiment.
    In a real scenario, you might use NLP techniques (e.g., VADER, TextBlob, or a transformer model)
    to compute sentiment scores from headline strings.
    
    For demonstration, let's assume:
      - If news headlines exist and mention positive keywords, assign +0.5.
      - If they are negative, assign -0.5.
      - Otherwise, 0.
    
    Here, we simply return 0.5 if any headline exists.
    """
    if news and isinstance(news, list) and len(news) > 0:
        # A real implementation would analyze each headline's sentiment.
        return 0.5  
    else:
        return 0.0

def improved_recommendation(data, news):
    """
    Combines several technical signals from yfinance data along with a news sentiment score
    to produce a recommendation: "Buy", "Sell", or "Hold" for short term trading.
    
    Signals included:
      - RSI: Oversold (<30, +signal) or overbought (>70, -signal)
      - Moving Average Crossover: A short-term (10-day) MA versus a medium-term (20-day) MA
      - Momentum: % change over the last 5 days as an indication of recent performance
      - Volume Spike: If the latest volume is significantly higher than the 20-day average
      - News: A simple sentiment offset calculated from recent news headlines
    """
    technical_score = 0

    # 1. RSI Signal
    rsi_value = compute_RSI(data, period=14)
    print(f"RSI: {rsi_value:.2f}")
    if rsi_value < 30:
        technical_score += 1  # Oversold -> potential buy signal
    elif rsi_value > 70:
        technical_score -= 1  # Overbought -> potential sell signal

    # 2. Moving Averages Signal (10-day vs. 20-day)
    if len(data) >= 20:
        short_ma = data['Close'].rolling(window=10).mean().iloc[-1]
        long_ma = data['Close'].rolling(window=20).mean().iloc[-1]
        print(f"Short MA (10 days): {short_ma:.2f}, Long MA (20 days): {long_ma:.2f}")
        if short_ma > long_ma:
            technical_score += 1  # Uptrend signal
        else:
            technical_score -= 1  # Downtrend signal

    # 3. Momentum Signal (5-Day Price Change)
    if len(data) >= 5:
        momentum = (data['Close'].iloc[-1] - data['Close'].iloc[-5]) / data['Close'].iloc[-5]
        print(f"5-Day Momentum: {momentum:.2%}")
        if momentum > 0.05:
            technical_score += 1  # Positive momentum
        elif momentum < -0.05:
            technical_score -= 1  # Negative momentum

    # 4. Volume Signal (Recent Volume Spike)
    if len(data) >= 20:
        current_volume = data['Volume'].iloc[-1]
        avg_volume = data['Volume'].rolling(window=20).mean().iloc[-1]
        print(f"Current Volume: {current_volume:,}, 20-Day Avg Volume: {int(avg_volume):,}")
        if current_volume > 1.5 * avg_volume:
            technical_score += 1

    # 5. News Sentiment Signal
    news_sentiment = compute_news_sentiment(news)
    print(f"News Sentiment Score: {news_sentiment}")
    
    # Combine both signals
    overall_score = technical_score + news_sentiment
    print(f"Overall Combined Score: {overall_score}")

    # Recommendation thresholds (these thresholds can be fine-tuned via backtesting)
    if overall_score >= 2:
        return "Buy"
    elif overall_score <= -2:
        return "Sell"
    else:
        return "Hold"

# --- Example Run ---
if __name__ == "__main__":
    # For demonstration, create some dummy historical data.
    # In practice, you'll fetch this using yfinance.
    dates = pd.date_range("2023-08-01", "2023-08-31")
    # Create a simple upward-trending price series
    dummy_data = pd.DataFrame({
        'Close': np.linspace(100, 110, len(dates)),
        'Volume': np.random.randint(100000, 200000, len(dates))
    }, index=dates)
    
    # Dummy news headlines – in practice you'll pull these from finnhub.
    dummy_news = [
        {"headline": "Company posts record quarterly earnings"},
        {"headline": "Analysts upgrade outlook on stock"}
    ]
    
    recommendation = improved_recommendation(dummy_data, dummy_news)
    print("Final Recommendation:", recommendation) 