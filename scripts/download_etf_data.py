import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os
from pathlib import Path

def download_etf_data():
    """Download ETF data for major market indices"""
    
    # Set date range (30 years)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365*30)
    
    # ETF tickers with descriptions
    etfs = {
        'SPY': 'S&P 500 Index',
        'VTI': 'Total US Stock Market',
        'DIA': 'Dow Jones Industrial Average',
        'IWM': 'Russell 2000 Small-Cap',
        'MDY': 'S&P MidCap 400',
        'QQQ': 'Nasdaq-100'
    }
    
    for ticker, description in etfs.items():
        print(f"\nDownloading {ticker} ({description}) data...")
        try:
            # Create directories if they don't exist
            data_dir = Path(f'data/raw/{ticker}')
            data_dir.joinpath('price').mkdir(parents=True, exist_ok=True)
            data_dir.joinpath('volume').mkdir(parents=True, exist_ok=True)
            
            # Download data using yfinance
            etf = yf.Ticker(ticker)
            df = etf.history(start=start_date, end=end_date, interval="1d")
            
            if df.empty:
                print(f"No data received for {ticker}")
                continue
            
            # Debug information
            print(f"Available columns: {df.columns.tolist()}")
            
            # Save price data (handle different column names)
            price_cols = []
            for col in ['Open', 'High', 'Low', 'Close', 'Adj Close']:
                if col in df.columns:
                    price_cols.append(col)
                elif col == 'Adj Close' and 'Adj_Close' in df.columns:
                    price_cols.append('Adj_Close')
                    
            if price_cols:
                df[price_cols].to_csv(data_dir / 'price' / 'daily_prices.csv')
                print(f"Saved price data with columns: {price_cols}")
            else:
                print(f"Warning: No price columns found in data")
            
            # Save volume data
            if 'Volume' in df.columns:
                df[['Volume']].to_csv(data_dir / 'volume' / 'daily_volume.csv')
                print("Saved volume data")
            else:
                print("Warning: No volume data found")
            
            print(f"Successfully downloaded {ticker} data")
            print(f"Date range: {df.index[0].date()} to {df.index[-1].date()}")
            print(f"Number of records: {len(df)}")
            
        except Exception as e:
            print(f"Error downloading {ticker}: {str(e)}")
            print("Full error details:")
            import traceback
            print(traceback.format_exc())

if __name__ == "__main__":
    download_etf_data() 