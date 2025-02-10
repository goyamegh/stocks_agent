import yfinance as yf
from datetime import datetime

if __name__ == "__main__":
    symbol = "SBIN.NS"  # Note the .NS suffix for NSE stocks
    
    # Hard-coded dates: 5 trading days in the past
    start_date = "2023-08-14"
    end_date = "2023-08-18"
    
    print(f"Fetching data for {symbol} from {start_date} to {end_date}")
    
    stock = yf.Ticker(symbol)
    data = stock.history(start=start_date, end=end_date)
    
    print("Data columns:", data.columns.tolist())
    print("Number of rows fetched:", len(data))
    
    if not data.empty:
        print(data.head())
    else:
        print("No data returned. Check the ticker or dates.") 