import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import seaborn as sns

def analyze_lead_lag(returns_data, max_lags=5):
    """Analyze lead-lag relationships between ETFs"""
    correlations = {}
    
    # Calculate lagged correlations
    for lag in range(-max_lags, max_lags + 1):
        if lag < 0:
            correlations[lag] = returns_data.shift(-lag).corr()['SPY']
        else:
            correlations[lag] = returns_data.shift(lag).corr()['SPY']
    
    return pd.DataFrame(correlations)

def main():
    # Load data
    etfs = ['SPY', 'QQQ', 'VTI', 'DIA', 'IWM', 'MDY']
    returns = {}
    
    for etf in etfs:
        df = pd.read_csv(f'data/raw/{etf}/price/daily_prices.csv', index_col=0, parse_dates=True)
        returns[etf] = df['Close'].pct_change()
    
    returns_df = pd.DataFrame(returns)
    
    # Calculate lead-lag correlations
    lag_corr = analyze_lead_lag(returns_df)
    
    # Plot lead-lag relationships
    plt.figure(figsize=(15, 8))
    for col in lag_corr.columns:
        if col != 'SPY':  # Skip SPY vs SPY
            plt.plot(lag_corr.index, lag_corr[col], label=col, marker='o')
    
    plt.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
    plt.title('Lead-Lag Relationships with S&P 500 (SPY)')
    plt.xlabel('Lag (Days) - Negative means ETF leads SPY')
    plt.ylabel('Correlation')
    plt.legend()
    plt.grid(True)
    plt.savefig('analysis/figures/lead_lag_analysis.png')
    plt.close()
    
    # Print findings
    print("\nLead-Lag Analysis:")
    print("Negative lag: Other ETF leads SPY")
    print("Positive lag: SPY leads Other ETF")
    print("\nCorrelations at different lags:")
    print(lag_corr.round(4))

if __name__ == "__main__":
    main() 