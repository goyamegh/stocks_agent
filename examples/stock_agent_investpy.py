import investpy
import pandas as pd
from datetime import datetime, timedelta

def fetch_stock_data_investpy(stock_name, from_date, to_date):
    """
    Fetch historical stock data for an Indian stock using investpy.
    
    Parameters:
      - stock_name: The full name of the stock as recognized by Investing.com
      - from_date: Start date as datetime object
      - to_date: End date as datetime object
    """
    try:
        # Convert dates to dd/mm/yyyy format as required by investpy
        from_date_str = from_date.strftime("%d/%m/%Y")
        to_date_str = to_date.strftime("%d/%m/%Y")
        
        data = investpy.get_stock_historical_data(
            stock=stock_name,
            country='india',
            from_date=from_date_str,
            to_date=to_date_str
        )
        return data
    except Exception as e:
        print(f"Error fetching data for {stock_name}: {e}")
        return pd.DataFrame()

# Dictionary mapping ticker symbols to their exact names in investpy
STOCK_NAMES = {
    "SBIN": "SBI",  # Changed from "State Bank Of India" to "SBI"
    "RELIANCE": "Reliance Industries Ltd",
    "TCS": "Tata Consultancy Services Ltd",
    "HDFCBANK": "HDFC Bank Ltd",
    "INFY": "Infosys Ltd"
}

if __name__ == "__main__":
    symbol = "SBIN"
    stock_name = STOCK_NAMES.get(symbol, symbol)
    
    # Use the same date range as in your NSEpy test
    start_date = datetime(2023, 8, 14)
    end_date = datetime(2023, 8, 18)
    
    print(f"Fetching data for {stock_name} from {start_date.date()} to {end_date.date()}")
    data = fetch_stock_data_investpy(stock_name, start_date, end_date)
    
    print("Data columns:", data.columns.tolist())
    print("Number of rows fetched:", len(data))
    
    if not data.empty:
        print("\nFirst few rows of data:")
        print(data.head())
    else:
        print("No data returned. Please check the stock name and dates.") 