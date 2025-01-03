import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))
from analysis.notebooks.investment_scenario_analysis import InvestmentScenarioAnalyzer

def test_data_download():
    """Test downloading and processing ETF data"""
    print("\n=== Testing Data Download ===")
    
    # Set date range (shorter period for testing)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365*5)  # 5 years for testing
    
    # ETF tickers
    etfs = ['SPY', 'QQQ']
    prices_data = {}
    
    print(f"\nDownloading data from {start_date} to {end_date}")
    
    # Download data
    for ticker in etfs:
        try:
            print(f"\nProcessing {ticker}...")
            etf = yf.Ticker(ticker)
            df = etf.history(start=start_date, end=end_date, interval="1d")
            
            if df.empty:
                print(f"No data received for {ticker}")
                continue
                
            print(f"Downloaded data shape: {df.shape}")
            print(f"Columns: {df.columns.tolist()}")
            print(f"Index type: {type(df.index)}")
            print(f"First few index values: {df.index[:5].tolist()}")
            
            prices_data[ticker] = df
            print(f"Successfully downloaded data for {ticker}")
            
        except Exception as e:
            print(f"Error downloading {ticker}: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            continue
    
    return prices_data

def test_data_processing(prices_data):
    """Test processing the downloaded data"""
    print("\n=== Testing Data Processing ===")
    
    try:
        analyzer = InvestmentScenarioAnalyzer()
        
        # Test data loading
        print("\nTesting data loading...")
        analyzer.load_data(prices_data)
        
        # Test price history plotting data
        print("\nTesting price history data...")
        if analyzer.prices_df is not None:
            print(f"Price data shape: {analyzer.prices_df.shape}")
            print(f"Price data columns: {analyzer.prices_df.columns.tolist()}")
            print(f"First few rows of price data:")
            print(analyzer.prices_df.head())
        else:
            print("No price data available")
        
        # Test rolling correlation data
        print("\nTesting rolling correlation...")
        if analyzer.returns_df is not None:
            rolling_corr = analyzer.returns_df['SPY'].rolling(60).corr(analyzer.returns_df['QQQ'])
            print(f"Rolling correlation shape: {rolling_corr.shape}")
            print(f"First few correlation values:")
            print(rolling_corr.head())
        else:
            print("No returns data available")
            
        return analyzer
        
    except Exception as e:
        print(f"Error in data processing: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None

def main():
    """Run all tests"""
    # Test data download
    prices_data = test_data_download()
    
    if not prices_data:
        print("Failed to download data")
        return
        
    # Test data processing
    analyzer = test_data_processing(prices_data)
    
    if analyzer is None:
        print("Failed to process data")
        return
        
    print("\nAll tests completed successfully!")

if __name__ == "__main__":
    main() 