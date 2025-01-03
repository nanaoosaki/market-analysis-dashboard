import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import seaborn as sns
import yfinance as yf
from datetime import datetime, timedelta
import streamlit as st

class InvestmentScenarioAnalyzer:
    def __init__(self):
        self.etfs = {'SPY': 'S&P 500', 'QQQ': 'Nasdaq-100'}
        self.initial_lump_sum = 50000
        self.monthly_income = 15000
        self.monthly_investment = 7500  # $7.5K from monthly income
        self.prices_df = None
        self.returns_df = None
        self.monthly_returns = None
        
    def load_data(self, prices_data):
        """Load and prepare data from provided prices DataFrame"""
        try:
            self.prices = {}
            self.returns = {}
            
            # Validate input data silently
            if not isinstance(prices_data, dict) or not prices_data:
                st.error("Failed to load data. Please try again.")
                return
            
            # Process each ETF silently
            for etf in self.etfs:
                try:
                    if etf not in prices_data:
                        continue
                        
                    df = prices_data[etf].copy()
                    if not isinstance(df, pd.DataFrame):
                        continue
                    
                    # Convert timezone-aware timestamps to timezone-naive
                    df.index = df.index.tz_localize(None)
                        
                    # Use 'Close' or 'Adj Close' column
                    if 'Close' in df.columns:
                        self.prices[etf] = pd.Series(df['Close'].values, index=df.index)
                    elif 'Adj Close' in df.columns:
                        self.prices[etf] = pd.Series(df['Adj Close'].values, index=df.index)
                    else:
                        continue
                        
                    self.returns[etf] = self.prices[etf].pct_change()
                    
                except Exception:
                    continue
            
            # Check if we have any data to process
            if not self.prices:
                st.error("No data available. Please try again.")
                return
                
            # Align data on common dates silently
            self.prices_df = pd.DataFrame(self.prices)
            self.returns_df = pd.DataFrame(self.returns)
            
            self.prices_df = self.prices_df.dropna()
            self.returns_df = self.returns_df.dropna()
            
            if self.prices_df.empty:
                st.error("No valid data after processing. Please try again.")
                return
                
            # Resample to monthly for income investment analysis
            self.monthly_returns = self.returns_df.resample('ME').apply(
                lambda x: (1 + x).prod() - 1)
                
        except Exception:
            st.error("Error processing data. Please try again.")
    
    def analyze_tech_momentum(self, window=60):
        """Analyze tech momentum relative to broad market"""
        # Calculate relative strength of QQQ vs SPY
        qqq_spy_ratio = self.prices_df['QQQ'] / self.prices_df['SPY']
        tech_momentum = qqq_spy_ratio.pct_change(window, fill_method=None)
        
        # Define tech momentum regimes
        tech_strong = tech_momentum > tech_momentum.quantile(0.7)
        tech_weak = tech_momentum < tech_momentum.quantile(0.3)
        
        # Convert to DataFrame with same index
        regimes = pd.DataFrame(index=tech_momentum.index)
        regimes['strong'] = tech_strong
        regimes['weak'] = tech_weak
        
        return tech_momentum, regimes
    
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