"""
A minimal script to fetch historical NSE data using NSEpy for a hard-coded 5-day range.

Before running, make sure you have NSEpy installed:
    pip install nsepy
"""

from datetime import date
from nsepy import get_history

if __name__ == "__main__":
    # Use SBIN (State Bank of India) as an example symbol.
    symbol = "SBIN"
    
    # Hard-coded date range: 5 trading days in the past (Monday to Friday)
    start_date = date(2023, 8, 14)  # Monday, August 14, 2023
    end_date = date(2023, 8, 18)    # Friday, August 18, 2023
    
    print(f"Fetching data for {symbol} from {start_date} to {end_date}")
    
    # Fetch historical stock data using NSEpy.
    data = get_history(symbol=symbol, start=start_date, end=end_date)
    
    print("Data columns:", data.columns.tolist())
    print("Number of rows fetched:", len(data))
    
    if not data.empty:
        print(data.head())
    else:
        print("No data returned. Verify that the date range covers valid trading days and that the market was open.") 