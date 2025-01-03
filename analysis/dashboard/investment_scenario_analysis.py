import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import seaborn as sns
import yfinance as yf
from datetime import datetime, timedelta

class InvestmentScenarioAnalyzer:
    def __init__(self):
        """Initialize the analyzer with default parameters"""
        self.etfs = {'SPY': 'S&P 500', 'QQQ': 'Nasdaq-100'}
        self.initial_lump_sum = 50000
        self.monthly_income = 15000
        self.monthly_investment = 7500  # $7.5K from monthly income
        self.prices_df = None
        self.returns_df = None
        self.monthly_returns = None
        self.prices = {}
        self.returns = {}
    
    def __str__(self):
        """Override string representation to prevent debug output"""
        return "Investment Scenario Analyzer"
        
    def __repr__(self):
        """Override repr to prevent debug output"""
        return self.__str__()
        
    def load_data(self, prices_data):
        """Load and prepare data from provided prices DataFrame"""
        if not isinstance(prices_data, dict) or not prices_data:
            return
        
        try:
            for etf in self.etfs:
                if etf not in prices_data:
                    continue
                    
                df = prices_data[etf].copy()
                if not isinstance(df, pd.DataFrame):
                    continue
                
                # Convert timezone-aware timestamps to timezone-naive
                df.index = df.index.tz_localize(None)
                    
                # Use 'Close' or 'Adj Close' column silently
                if 'Close' in df.columns:
                    self.prices[etf] = pd.Series(df['Close'].values, index=df.index, name=etf)
                elif 'Adj Close' in df.columns:
                    self.prices[etf] = pd.Series(df['Adj Close'].values, index=df.index, name=etf)
                else:
                    continue
                    
                self.returns[etf] = self.prices[etf].pct_change()
            
            if not self.prices:
                return
                
            # Process data frames silently
            self.prices_df = pd.DataFrame(self.prices)
            self.returns_df = pd.DataFrame(self.returns)
            
            self.prices_df = self.prices_df.dropna()
            self.returns_df = self.returns_df.dropna()
            
            if self.prices_df.empty:
                return
                
            # Calculate monthly returns silently
            self.monthly_returns = self.returns_df.resample('ME').apply(
                lambda x: (1 + x).prod() - 1)
                
        except Exception:
            pass
    
    def analyze_tech_momentum(self, window=60):
        """Analyze tech momentum relative to broad market"""
        try:
            print("\nDebug - analyze_tech_momentum start:")
            print("prices_df type:", type(self.prices_df))
            print("prices_df shape:", self.prices_df.shape if self.prices_df is not None else None)
            print("prices_df head:", self.prices_df.head() if self.prices_df is not None else None)
            print("prices_df columns:", self.prices_df.columns if self.prices_df is not None else None)
            
            if self.prices_df is None or self.prices_df.empty:
                print("No price data available")
                return None, None
                
            # Calculate relative strength of QQQ vs SPY
            qqq_spy_ratio = self.prices_df['QQQ'] / self.prices_df['SPY']
            tech_momentum = qqq_spy_ratio.pct_change(window, fill_method=None)
            
            print("\nDebug - After calculations:")
            print("qqq_spy_ratio shape:", qqq_spy_ratio.shape)
            print("qqq_spy_ratio head:", qqq_spy_ratio.head())
            print("tech_momentum shape:", tech_momentum.shape)
            print("tech_momentum head:", tech_momentum.head())
            print("tech_momentum NaN count:", tech_momentum.isna().sum())
            
            # Define tech momentum regimes
            tech_strong = tech_momentum > tech_momentum.quantile(0.7)
            tech_weak = tech_momentum < tech_momentum.quantile(0.3)
            
            print("\nDebug - Regime thresholds:")
            print("Strong threshold:", tech_momentum.quantile(0.7))
            print("Weak threshold:", tech_momentum.quantile(0.3))
            
            # Convert to DataFrame with same index
            regimes = pd.DataFrame(index=tech_momentum.index)
            regimes['strong'] = tech_strong
            regimes['weak'] = tech_weak
            
            print("\nDebug - Final regimes:")
            print("regimes shape:", regimes.shape)
            print("regimes head:", regimes.head())
            print("strong periods:", tech_strong.sum())
            print("weak periods:", tech_weak.sum())
            
            return tech_momentum, regimes
            
        except Exception as e:
            print(f"Error in analyze_tech_momentum: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return None, None
    
    def simulate_lump_sum_investment(self):
        """Simulate lump sum investment strategy"""
        # Get tech regime signals
        tech_momentum, regimes = self.analyze_tech_momentum()
        
        # Initialize portfolio weights
        weights = pd.DataFrame(0.5, index=self.returns_df.index, columns=['SPY', 'QQQ'])
        
        # Set weights based on regimes where signals exist
        mask = ~regimes.isna().all(axis=1)
        weights.loc[regimes.loc[mask, 'strong'], 'QQQ'] = 0.7
        weights.loc[regimes.loc[mask, 'strong'], 'SPY'] = 0.3
        weights.loc[regimes.loc[mask, 'weak'], 'QQQ'] = 0.3
        weights.loc[regimes.loc[mask, 'weak'], 'SPY'] = 0.7
        
        # Calculate portfolio returns
        portfolio_returns = (weights * self.returns_df).sum(axis=1)
        portfolio_value = self.initial_lump_sum * (1 + portfolio_returns).cumprod()
        
        return portfolio_value, weights
    
    def simulate_monthly_investment(self):
        """Simulate monthly investment strategy"""
        # Monthly tech regime signals
        tech_momentum, regimes = self.analyze_tech_momentum()
        monthly_regimes = regimes.resample('ME').last()
        
        # Align indices
        common_dates = self.monthly_returns.index.intersection(monthly_regimes.index)
        monthly_returns_aligned = self.monthly_returns.loc[common_dates]
        monthly_regimes_aligned = monthly_regimes.loc[common_dates]
        
        # Initialize monthly portfolio with default weights
        monthly_weights = pd.DataFrame(0.5, index=monthly_returns_aligned.index, 
                                     columns=['SPY', 'QQQ'])
        
        # Set weights based on regimes where signals exist
        mask = ~monthly_regimes_aligned.isna().all(axis=1)
        monthly_weights.loc[monthly_regimes_aligned.loc[mask, 'strong'], 'QQQ'] = 0.7
        monthly_weights.loc[monthly_regimes_aligned.loc[mask, 'strong'], 'SPY'] = 0.3
        monthly_weights.loc[monthly_regimes_aligned.loc[mask, 'weak'], 'QQQ'] = 0.3
        monthly_weights.loc[monthly_regimes_aligned.loc[mask, 'weak'], 'SPY'] = 0.7
        
        # Calculate monthly portfolio value with regular contributions
        portfolio_value = pd.Series(0, index=monthly_returns_aligned.index)
        current_value = 0
        
        for date in monthly_returns_aligned.index:
            # Add monthly investment
            current_value += self.monthly_investment
            
            # Apply monthly returns
            returns = (monthly_weights.loc[date] * monthly_returns_aligned.loc[date]).sum()
            current_value *= (1 + returns)
            
            portfolio_value[date] = current_value
        
        return portfolio_value, monthly_weights 