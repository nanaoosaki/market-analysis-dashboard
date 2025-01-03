import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_etf_data(ticker):
    """Load price and volume data for an ETF"""
    base_path = Path(f'data/raw/{ticker}')
    
    price_df = pd.read_csv(f"{base_path}/price/daily_prices.csv", index_col=0, parse_dates=True)
    volume_df = pd.read_csv(f"{base_path}/volume/daily_volume.csv", index_col=0, parse_dates=True)
    
    return price_df, volume_df

def plot_price_history(price_df, ticker):
    """Plot price history with volume"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), height_ratios=[2, 1])
    
    # Plot adjusted close price
    ax1.plot(price_df.index, price_df['Adj Close'], label=f'{ticker} Price')
    ax1.set_title(f'{ticker} Price History')
    ax1.set_ylabel('Price ($)')
    ax1.legend()
    ax1.grid(True)
    
    # Plot returns distribution
    returns = price_df['Adj Close'].pct_change().dropna()
    sns.histplot(returns, bins=50, ax=ax2)
    ax2.set_title(f'{ticker} Daily Returns Distribution')
    ax2.set_xlabel('Daily Returns')
    
    plt.tight_layout()
    plt.savefig(f'analysis/notebooks/figures/{ticker}_price_history.png')
    plt.close()

def calculate_statistics(price_df, ticker):
    """Calculate basic statistics"""
    returns = price_df['Adj Close'].pct_change().dropna()
    
    stats = {
        'Mean Daily Return': returns.mean(),
        'Daily Volatility': returns.std(),
        'Annualized Volatility': returns.std() * np.sqrt(252),
        'Skewness': returns.skew(),
        'Kurtosis': returns.kurtosis(),
        'Sharpe Ratio': (returns.mean() / returns.std()) * np.sqrt(252),
        'Max Drawdown': (price_df['Adj Close'] / price_df['Adj Close'].cummax() - 1).min()
    }
    
    return pd.Series(stats, name=ticker)

def main():
    # Create figures directory
    Path('analysis/notebooks/figures').mkdir(parents=True, exist_ok=True)
    
    # Analyze each ETF
    etfs = ['SPY', 'QQQ']
    stats_list = []
    
    for ticker in etfs:
        print(f"\nAnalyzing {ticker}...")
        price_df, volume_df = load_etf_data(ticker)
        
        # Generate plots
        plot_price_history(price_df, ticker)
        
        # Calculate statistics
        stats = calculate_statistics(price_df, ticker)
        stats_list.append(stats)
        
        print(f"\n{ticker} Statistics:")
        print(stats)
    
    # Compare ETFs
    stats_df = pd.concat(stats_list, axis=1)
    stats_df.to_csv('analysis/notebooks/etf_comparison.csv')
    print("\nETF Comparison saved to etf_comparison.csv")

if __name__ == "__main__":
    main() 