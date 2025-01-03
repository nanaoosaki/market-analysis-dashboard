import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import seaborn as sns

class EnhancedMarketAnalyzer:
    def __init__(self):
        self.etfs = {
            'SPY': 'S&P 500 Index',
            'QQQ': 'Nasdaq-100',
            'VTI': 'Total US Market',
            'DIA': 'Dow Jones',
            'IWM': 'Russell 2000',
            'MDY': 'S&P MidCap 400'
        }
        self.market_periods = {
            'Financial Crisis': ('2008-01-01', '2009-03-31'),
            'Post Crisis Recovery': ('2009-04-01', '2013-12-31'),
            'Pre-Covid Bull': ('2014-01-01', '2019-12-31'),
            'Covid Crash': ('2020-01-01', '2020-03-31'),
            'Post-Covid Recovery': ('2020-04-01', '2021-12-31'),
            'Recent Period': ('2022-01-01', '2024-01-01')
        }
        
    def load_data(self):
        """Load and prepare data"""
        self.returns = {}
        self.prices = {}
        
        for etf in self.etfs:
            df = pd.read_csv(f'data/raw/{etf}/price/daily_prices.csv', 
                           index_col=0, parse_dates=True)
            self.prices[etf] = df['Close']
            self.returns[etf] = df['Close'].pct_change()
            
        self.returns_df = pd.DataFrame(self.returns)
        self.prices_df = pd.DataFrame(self.prices)
    
    def analyze_market_periods(self):
        """Analyze different market periods"""
        period_stats = {}
        
        for period_name, (start_date, end_date) in self.market_periods.items():
            period_returns = self.returns_df.loc[start_date:end_date]
            period_prices = self.prices_df.loc[start_date:end_date]
            
            # Calculate period statistics
            stats = {
                'Total Return': (period_prices.iloc[-1] / period_prices.iloc[0] - 1),
                'Annualized Vol': period_returns.std() * np.sqrt(252),
                'Correlation with SPY': period_returns.corr()['SPY'],
                'Max Drawdown': (period_prices / period_prices.cummax() - 1).min()
            }
            period_stats[period_name] = pd.DataFrame(stats)
        
        return period_stats
    
    def analyze_market_conditions(self):
        """Analyze bull vs bear market conditions"""
        # Define bull/bear based on 200-day moving average
        spy_ma200 = self.prices_df['SPY'].rolling(window=200).mean()
        bull_market = self.prices_df['SPY'] > spy_ma200
        
        # Calculate conditional correlations
        bull_corr = self.returns_df[bull_market].corr()
        bear_corr = self.returns_df[~bull_market].corr()
        
        return {
            'Bull Market Correlations': bull_corr,
            'Bear Market Correlations': bear_corr
        }
    
    def plot_period_performance(self):
        """Plot performance during different market periods"""
        for period_name, (start_date, end_date) in self.market_periods.items():
            period_prices = self.prices_df.loc[start_date:end_date]
            normalized = period_prices / period_prices.iloc[0] * 100
            
            plt.figure(figsize=(15, 8))
            for col in normalized.columns:
                plt.plot(normalized.index, normalized[col], 
                        label=f"{col} ({self.etfs[col]})")
            
            plt.title(f'ETF Performance - {period_name}')
            plt.xlabel('Date')
            plt.ylabel('Normalized Price (100 = Start of Period)')
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(f'analysis/figures/performance_{period_name.lower().replace(" ", "_")}.png')
            plt.close()

def main():
    # Create output directory
    Path('analysis/figures').mkdir(parents=True, exist_ok=True)
    
    # Initialize and run analysis
    analyzer = EnhancedMarketAnalyzer()
    analyzer.load_data()
    
    # 1. Analyze specific market periods
    print("\nAnalysis by Market Period:")
    period_stats = analyzer.analyze_market_periods()
    for period, stats in period_stats.items():
        print(f"\n{period}:")
        print(stats.round(4))
        
        # Save to CSV
        stats.to_csv(f'analysis/figures/stats_{period.lower().replace(" ", "_")}.csv')
    
    # 2. Plot period-specific performance
    print("\nGenerating period-specific performance plots...")
    analyzer.plot_period_performance()
    
    # 3. Analyze bull vs bear markets
    print("\nBull vs Bear Market Analysis:")
    market_conditions = analyzer.analyze_market_conditions()
    
    print("\nBull Market Correlations:")
    print(market_conditions['Bull Market Correlations'].round(4))
    print("\nBear Market Correlations:")
    print(market_conditions['Bear Market Correlations'].round(4))
    
    # Save conditional correlations
    for condition, corr in market_conditions.items():
        corr.to_csv(f'analysis/figures/{condition.lower().replace(" ", "_")}.csv')
    
    print("\nAnalysis complete. Results saved in analysis/figures/")

if __name__ == "__main__":
    main() 