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
            # Debug: Print the type and structure of input data
            st.write("Type of prices_data:", type(prices_data))
            st.write("Keys in prices_data:", list(prices_data.keys()) if isinstance(prices_data, dict) else "Not a dictionary")
            
            self.prices = {}
            self.returns = {}
            
            # Validate input data
            if not isinstance(prices_data, dict):
                st.error(f"Expected prices_data to be a dictionary, got {type(prices_data)}")
                return
                
            if not prices_data:
                st.error("No data provided in prices_data")
                return
            
            # Add debug information for each ticker
            for ticker, df in prices_data.items():
                st.write(f"\nDebug info for {ticker}:")
                st.write(f"Type: {type(df)}")
                if isinstance(df, pd.DataFrame):
                    st.write(f"Shape: {df.shape}")
                    st.write(f"Columns: {df.columns.tolist()}")
                    st.write(f"Index type: {type(df.index)}")
                    st.write(f"Sample of index values: {df.index[:5].tolist()}")
            
            # Process each ETF
            for etf in self.etfs:
                try:
                    if etf not in prices_data:
                        st.error(f"No data found for {etf}")
                        continue
                        
                    df = prices_data[etf].copy()  # Make a copy to avoid modifying original
                    if not isinstance(df, pd.DataFrame):
                        st.error(f"Data for {etf} is not a DataFrame")
                        continue
                    
                    # Convert timezone-aware timestamps to timezone-naive
                    df.index = df.index.tz_localize(None)
                        
                    # Use 'Close' or 'Adj Close' column
                    if 'Close' in df.columns:
                        self.prices[etf] = pd.Series(df['Close'].values, index=df.index)
                    elif 'Adj Close' in df.columns:
                        self.prices[etf] = pd.Series(df['Adj Close'].values, index=df.index)
                    else:
                        st.error(f"No price data found for {etf}. Available columns: {df.columns.tolist()}")
                        continue
                        
                    self.returns[etf] = self.prices[etf].pct_change()
                    st.success(f"Successfully processed {etf}")
                    
                except Exception as e:
                    st.error(f"Error processing {etf}: {str(e)}")
                    import traceback
                    st.error(f"Traceback: {traceback.format_exc()}")
                    continue
            
            # Check if we have any data to process
            if not self.prices:
                st.error("No price data was loaded successfully")
                return
                
            # Align data on common dates
            st.write("\nCreating DataFrames...")
            self.prices_df = pd.DataFrame(self.prices)
            self.returns_df = pd.DataFrame(self.returns)
            
            st.write("Dropping NA values...")
            self.prices_df = self.prices_df.dropna()
            self.returns_df = self.returns_df.dropna()
            
            if self.prices_df.empty:
                st.error("No valid price data after alignment")
                return
                
            # Add debug information about final processed data
            st.write("\nFinal processed data:")
            st.write(f"Price data shape: {self.prices_df.shape}")
            st.write(f"Date range: {self.prices_df.index.min()} to {self.prices_df.index.max()}")
            st.write("First few rows of processed data:")
            st.write(self.prices_df.head())
            
            # Resample to monthly for income investment analysis
            st.write("\nResampling to monthly data...")
            self.monthly_returns = self.returns_df.resample('ME').apply(
                lambda x: (1 + x).prod() - 1)
                
        except Exception as e:
            st.error(f"Error in load_data: {str(e)}")
            import traceback
            st.error(f"Traceback: {traceback.format_exc()}")
    
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
    
    def plot_scenario_analysis(self, lump_sum_value, monthly_value):
        """Plot scenario analysis results"""
        plt.figure(figsize=(15, 10))
        
        # Plot 1: Lump Sum Investment Performance
        plt.subplot(2, 1, 1)
        plt.plot(lump_sum_value.index, lump_sum_value, 
                label='Dynamic Portfolio (Lump Sum $50K)')
        plt.title('Lump Sum Investment Performance')
        plt.ylabel('Portfolio Value ($)')
        plt.legend()
        plt.grid(True)
        
        # Plot 2: Monthly Investment Performance
        plt.subplot(2, 1, 2)
        plt.plot(monthly_value.index, monthly_value, 
                label='Dynamic Portfolio (Monthly $7.5K)')
        plt.title('Monthly Investment Performance')
        plt.ylabel('Portfolio Value ($)')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig('analysis/figures/investment_scenario_analysis.png')
        plt.close()

def main():
    # Create output directory
    Path('analysis/figures').mkdir(parents=True, exist_ok=True)
    
    # Initialize and run analysis
    analyzer = InvestmentScenarioAnalyzer()
    analyzer.load_data()
    
    # Simulate lump sum investment
    lump_sum_value, lump_sum_weights = analyzer.simulate_lump_sum_investment()
    
    # Simulate monthly investment
    monthly_value, monthly_weights = analyzer.simulate_monthly_investment()
    
    # Calculate performance metrics
    print("\nLump Sum Investment Analysis ($50K):")
    total_lump_sum_return = (lump_sum_value[-1] / analyzer.initial_lump_sum - 1) * 100
    annual_lump_sum_return = (
        (1 + total_lump_sum_return/100) ** (252/len(lump_sum_value)) - 1) * 100
    print(f"Total Return: {total_lump_sum_return:.2f}%")
    print(f"Annualized Return: {annual_lump_sum_return:.2f}%")
    print(f"Final Portfolio Value: ${lump_sum_value[-1]:,.2f}")
    
    print("\nMonthly Investment Analysis ($7.5K/month):")
    total_invested = analyzer.monthly_investment * len(monthly_value)
    total_monthly_return = (monthly_value[-1] / total_invested - 1) * 100
    annual_monthly_return = (
        (1 + total_monthly_return/100) ** (12/len(monthly_value)) - 1) * 100
    print(f"Total Invested: ${total_invested:,.2f}")
    print(f"Total Return: {total_monthly_return:.2f}%")
    print(f"Annualized Return: {annual_monthly_return:.2f}%")
    print(f"Final Portfolio Value: ${monthly_value[-1]:,.2f}")
    
    # Plot analysis
    analyzer.plot_scenario_analysis(lump_sum_value, monthly_value)
    
    print("\nAnalysis complete. Results saved in analysis/figures/")

if __name__ == "__main__":
    main() 