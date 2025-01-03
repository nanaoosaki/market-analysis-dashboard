import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import seaborn as sns

class SectorRotationAnalyzer:
    def __init__(self):
        self.etfs = {'SPY': 'S&P 500', 'QQQ': 'Nasdaq-100'}
        
    def load_data(self):
        """Load and prepare data"""
        self.prices = {}
        self.returns = {}
        
        for etf in self.etfs:
            df = pd.read_csv(f'data/raw/{etf}/price/daily_prices.csv', 
                           index_col=0, parse_dates=True)
            self.prices[etf] = df['Close']
            self.returns[etf] = df['Close'].pct_change()
            
        self.prices_df = pd.DataFrame(self.prices)
        self.returns_df = pd.DataFrame(self.returns)
    
    def analyze_tech_momentum(self, window=60):
        """Analyze tech momentum relative to broad market"""
        # Calculate relative strength of QQQ vs SPY
        qqq_spy_ratio = self.prices_df['QQQ'] / self.prices_df['SPY']
        tech_momentum = qqq_spy_ratio.pct_change(window)
        
        # Define tech momentum regimes
        tech_strong = tech_momentum > tech_momentum.quantile(0.7)  # Top 30%
        tech_weak = tech_momentum < tech_momentum.quantile(0.3)    # Bottom 30%
        
        return tech_momentum, tech_strong, tech_weak
    
    def calculate_regime_performance(self, tech_strong, tech_weak):
        """Calculate performance in different regimes"""
        # Portfolio weights in different regimes
        weights = pd.DataFrame(index=self.returns_df.index, columns=['SPY', 'QQQ'])
        
        # Tech Strong: 70% QQQ, 30% SPY
        weights.loc[tech_strong, 'QQQ'] = 0.7
        weights.loc[tech_strong, 'SPY'] = 0.3
        
        # Tech Weak: 30% QQQ, 70% SPY
        weights.loc[tech_weak, 'QQQ'] = 0.3
        weights.loc[tech_weak, 'SPY'] = 0.7
        
        # Neutral: 50-50
        neutral = ~(tech_strong | tech_weak)
        weights.loc[neutral, 'QQQ'] = 0.5
        weights.loc[neutral, 'SPY'] = 0.5
        
        # Calculate portfolio returns
        portfolio_returns = (weights * self.returns_df).sum(axis=1)
        
        # Calculate regime-specific statistics
        stats = {
            'Tech Strong': {
                'Returns': self.returns_df[tech_strong],
                'Weights': weights[tech_strong]
            },
            'Tech Weak': {
                'Returns': self.returns_df[tech_weak],
                'Weights': weights[tech_weak]
            },
            'Neutral': {
                'Returns': self.returns_df[neutral],
                'Weights': weights[neutral]
            }
        }
        
        return portfolio_returns, stats
    
    def plot_regime_analysis(self, tech_momentum, portfolio_returns):
        """Plot regime analysis results"""
        # Plot 1: Tech Momentum Indicator
        plt.figure(figsize=(15, 10))
        plt.subplot(2, 1, 1)
        plt.plot(tech_momentum.index, tech_momentum, label='QQQ/SPY Momentum')
        plt.axhline(y=tech_momentum.quantile(0.7), color='g', linestyle='--', 
                   label='Strong Tech Regime')
        plt.axhline(y=tech_momentum.quantile(0.3), color='r', linestyle='--', 
                   label='Weak Tech Regime')
        plt.title('Tech Momentum Indicator (QQQ/SPY Relative Strength)')
        plt.legend()
        plt.grid(True)
        
        # Plot 2: Cumulative Returns
        plt.subplot(2, 1, 2)
        cum_returns = {
            'Dynamic Portfolio': (1 + portfolio_returns).cumprod(),
            'SPY': (1 + self.returns_df['SPY']).cumprod(),
            'QQQ': (1 + self.returns_df['QQQ']).cumprod()
        }
        
        for name, returns in cum_returns.items():
            plt.plot(returns.index, returns, label=name)
            
        plt.title('Cumulative Returns Comparison')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig('analysis/figures/regime_analysis.png')
        plt.close()

def main():
    # Create output directory
    Path('analysis/figures').mkdir(parents=True, exist_ok=True)
    
    # Initialize and run analysis
    analyzer = SectorRotationAnalyzer()
    analyzer.load_data()
    
    # Analyze tech momentum
    tech_momentum, tech_strong, tech_weak = analyzer.analyze_tech_momentum()
    
    # Calculate regime performance
    portfolio_returns, regime_stats = analyzer.calculate_regime_performance(
        tech_strong, tech_weak)
    
    # Print regime statistics
    print("\nRegime Analysis:")
    for regime, data in regime_stats.items():
        returns = data['Returns']
        print(f"\n{regime} Regime:")
        print(f"Average Returns:")
        print(returns.mean().round(4))
        print(f"Volatility:")
        print(returns.std().round(4))
        print(f"Average Weights:")
        print(data['Weights'].mean().round(4))
    
    # Plot analysis
    analyzer.plot_regime_analysis(tech_momentum, portfolio_returns)
    
    print("\nAnalysis complete. Results saved in analysis/figures/")

if __name__ == "__main__":
    main() 