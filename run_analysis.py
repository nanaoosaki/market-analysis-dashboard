import sys
import os
import subprocess
from pathlib import Path
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

def ensure_venv():
    """Ensure we're running in the virtual environment"""
    if not hasattr(sys, 'real_prefix') and not sys.base_prefix != sys.prefix:
        venv_path = Path('py310')
        if not venv_path.exists():
            print("Creating virtual environment...")
            subprocess.run([sys.executable, '-m', 'venv', 'py310'])
        
        if os.name == 'nt':  # Windows
            python_path = venv_path / 'Scripts' / 'python.exe'
        else:  # Unix
            python_path = venv_path / 'bin' / 'python'
        
        print("Activating virtual environment and restarting...")
        os.execv(str(python_path), [str(python_path), __file__])

def verify_data(ticker, data_path):
    """Verify downloaded data for completeness and quality"""
    price_path = data_path / 'price' / 'daily_prices.csv'
    volume_path = data_path / 'volume' / 'daily_volume.csv'
    
    if not price_path.exists() or not volume_path.exists():
        print(f"Missing data files for {ticker}")
        return False
    
    try:
        # Load and verify price data
        price_df = pd.read_csv(price_path, index_col=0, parse_dates=True)
        volume_df = pd.read_csv(volume_path, index_col=0, parse_dates=True)
        
        # Check for minimum required columns
        required_price_cols = ['Open', 'High', 'Low', 'Close', 'Adj Close']
        if not all(col in price_df.columns for col in required_price_cols):
            print(f"Missing required price columns for {ticker}")
            return False
            
        # Check for data quality
        if price_df.empty or volume_df.empty:
            print(f"Empty data for {ticker}")
            return False
            
        # Check for excessive missing values (>10%)
        missing_threshold = 0.10
        if price_df.isnull().mean().max() > missing_threshold:
            print(f"Too many missing values in price data for {ticker}")
            return False
            
        # Verify date range
        date_range = (datetime.now() - timedelta(days=365*30)).date()
        earliest_date = price_df.index[0].date()
        
        if earliest_date > date_range:
            print(f"Insufficient historical data for {ticker}. Got data from {earliest_date}, needed {date_range}")
            return False
            
        print(f"Data verification successful for {ticker}")
        print(f"Date range: {earliest_date} to {price_df.index[-1].date()}")
        print(f"Number of records: {len(price_df)}")
        return True
        
    except Exception as e:
        print(f"Error verifying data for {ticker}: {str(e)}")
        return False

def download_and_verify():
    """Download data and verify its integrity"""
    # Create data directories
    data_root = Path('data/raw')
    etfs = {
        'SPY': data_root / 'SPY',
        'QQQ': data_root / 'QQQ'
    }
    
    for path in etfs.values():
        path.mkdir(parents=True, exist_ok=True)
        (path / 'price').mkdir(exist_ok=True)
        (path / 'volume').mkdir(exist_ok=True)
    
    # Download and verify each ETF
    success = True
    for ticker, path in etfs.items():
        print(f"\nProcessing {ticker}...")
        
        # Try downloading up to 3 times
        for attempt in range(3):
            try:
                subprocess.run([sys.executable, 'scripts/download_etf_data.py'], check=True)
                
                if verify_data(ticker, path):
                    print(f"Successfully downloaded and verified {ticker}")
                    break
                else:
                    print(f"Attempt {attempt + 1}: Data verification failed for {ticker}")
                    if attempt < 2:  # Don't sleep on last attempt
                        print("Retrying in 5 seconds...")
                        import time
                        time.sleep(5)
            except subprocess.CalledProcessError as e:
                print(f"Error downloading {ticker}: {str(e)}")
                if attempt == 2:  # Last attempt
                    success = False
                    
    return success

def main():
    """Main analysis workflow"""
    ensure_venv()
    print("Running in virtual environment:", sys.prefix)
    
    # Step 1: Download and verify data
    if download_and_verify():
        print("\nData download and verification successful. Proceeding with analysis...")
        # Step 2: Run analysis
        subprocess.run([sys.executable, 'analysis/notebooks/initial_eda.py'])
    else:
        print("\nData download or verification failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 