import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np
from scipy import stats

class MarketAnalyzer:
    def __init__(self):
        self.etfs = {
            'SPY': 'S&P 500 Index',
            'QQQ': 'Nasdaq-100',
            'VTI': 'Total US Market',
            'DIA': 'Dow Jones',
            'IWM': 'Russell 2000',
            'MDY': 'S&P MidCap 400'
        }
        self.data = {}
        self.returns = {}
        
        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
    def load_data(self):
        """Load price data for all ETFs"""
        for ticker in self.etfs:
            try:
                price_path = Path(f'data/raw/{ticker}/price/daily_prices.csv')
                df = pd.read_csv(price_path, index_col=0, parse_dates=True)
                self.data[ticker] = df
                # Calculate returns
                self.returns[ticker] = df['Close'].pct_change()
            except Exception as e:
                print(f"Error loading {ticker}: {str(e)}")
    
    def plot_correlation_matrix(self):
        """Plot correlation matrix of ETF returns"""
        returns_df = pd.DataFrame(self.returns)
        corr = returns_df.corr()
        
        plt.figure(figsize=(12, 8))
        sns.heatmap(corr, annot=True, cmap='coolwarm', center=0)
        plt.title('ETF Returns Correlation Matrix')
        plt.tight_layout()
        plt.savefig('analysis/figures/correlation_matrix.png')
        plt.close()
        
        return corr
    
    def plot_performance_comparison(self):
        """Plot normalized price performance"""
        plt.figure(figsize=(15, 8))
        
        for ticker, df in self.data.items():
            normalized = df['Close'] / df['Close'].iloc[0] * 100
            plt.plot(normalized.index, normalized, label=f"{ticker} ({self.etfs[ticker]})")
        
        plt.title('ETF Performance Comparison (Normalized to 100)')
        plt.xlabel('Date')
        plt.ylabel('Normalized Price')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig('analysis/figures/performance_comparison.png')
        plt.close()
    
    def calculate_risk_metrics(self):
        """Calculate risk-adjusted return metrics"""
        risk_free_rate = 0.03  # Assuming 3% risk-free rate
        metrics = []
        
        for ticker, returns in self.returns.items():
            annual_return = returns.mean() * 252
            annual_vol = returns.std() * np.sqrt(252)
            sharpe = (annual_return - risk_free_rate) / annual_vol
            max_drawdown = (self.data[ticker]['Close'] / self.data[ticker]['Close'].cummax() - 1).min()
            
            metrics.append({
                'ETF': ticker,
                'Description': self.etfs[ticker],
                'Annual Return': annual_return,
                'Annual Volatility': annual_vol,
                'Sharpe Ratio': sharpe,
                'Max Drawdown': max_drawdown,
                'Skewness': returns.skew(),
                'Kurtosis': returns.kurtosis()
            })
        
        return pd.DataFrame(metrics).set_index('ETF')
    
    def plot_rolling_metrics(self, window=252):
        """Plot rolling volatility and correlation"""
        returns_df = pd.DataFrame(self.returns)
        
        # Rolling volatility
        plt.figure(figsize=(15, 8))
        rolling_vol = returns_df.rolling(window).std() * np.sqrt(252)
        for col in rolling_vol.columns:
            plt.plot(rolling_vol.index, rolling_vol[col], label=col)
        
        plt.title(f'{window}-Day Rolling Volatility')
        plt.xlabel('Date')
        plt.ylabel('Annualized Volatility')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig('analysis/figures/rolling_volatility.png')
        plt.close()
        
        # Rolling correlation with SPY
        plt.figure(figsize=(15, 8))
        spy_returns = returns_df['SPY']
        for col in returns_df.columns:
            if col != 'SPY':
                roll_corr = returns_df[col].rolling(window).corr(spy_returns)
                plt.plot(roll_corr.index, roll_corr, label=f'{col} vs SPY')
        
        plt.title(f'{window}-Day Rolling Correlation with S&P 500')
        plt.xlabel('Date')
        plt.ylabel('Correlation')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig('analysis/figures/rolling_correlation.png')
        plt.close()

def main():
    # Create output directory
    Path('analysis/figures').mkdir(parents=True, exist_ok=True)
    
    # Initialize and run analysis
    analyzer = MarketAnalyzer()
    analyzer.load_data()
    
    # 1. Correlation Analysis
    print("\nCorrelation Analysis:")
    corr = analyzer.plot_correlation_matrix()
    print(corr)
    
    # 2. Performance Comparison
    print("\nGenerating performance comparison plot...")
    analyzer.plot_performance_comparison()
    
    # 3. Risk Metrics
    print("\nRisk-Adjusted Return Metrics:")
    metrics = analyzer.calculate_risk_metrics()
    print(metrics)
    metrics.to_csv('analysis/figures/risk_metrics.csv')
    
    # 4. Rolling Analysis
    print("\nGenerating rolling metrics plots...")
    analyzer.plot_rolling_metrics()
    
    print("\nAnalysis complete. Results saved in analysis/figures/")

if __name__ == "__main__":
    main() 