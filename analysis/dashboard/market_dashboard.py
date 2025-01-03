import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import sys
import yfinance as yf
from datetime import datetime, timedelta

# Import local version of InvestmentScenarioAnalyzer
from investment_scenario_analysis import InvestmentScenarioAnalyzer

class MarketDashboard:
    def __init__(self):
        """Initialize the dashboard with data"""
        with st.spinner("Downloading data..."):
            self._prices_data = self.download_data()  # Download data first
            self.analyzer = InvestmentScenarioAnalyzer()
            if self._prices_data:
                self.analyzer.load_data(self._prices_data)
    
    def __str__(self):
        """Override string representation to prevent debug output"""
        return "Market Analysis Dashboard"
        
    def __repr__(self):
        """Override repr to prevent debug output"""
        return self.__str__()
        
    @property
    def prices_data(self):
        """Property to prevent direct access to prices_data"""
        return None  # Return None to prevent debug output
        
    def download_data(self):
        """Download ETF data and return as dictionary of DataFrames"""
        try:
            # Set date range (30 years)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365*30)
            
            # ETF tickers
            etfs = ['SPY', 'QQQ']
            prices_data = {}
            
            for ticker in etfs:
                try:
                    # Download data using yfinance
                    etf = yf.Ticker(ticker)
                    df = etf.history(start=start_date, end=end_date, interval="1d")
                    
                    if not df.empty:
                        prices_data[ticker] = df
                    
                except Exception:
                    continue
            
            return prices_data if prices_data else {}
            
        except Exception:
            return {}
    
    def plot_price_history(self):
        """Plot interactive price history"""
        fig = go.Figure()
        
        for etf in self.analyzer.prices_df.columns:
            fig.add_trace(
                go.Scatter(
                    x=self.analyzer.prices_df.index,
                    y=self.analyzer.prices_df[etf],
                    name=f"{etf} Price",
                    hovertemplate=
                    f"{etf}<br>" +
                    "Date: %{x}<br>" +
                    "Price: $%{y:.2f}<br>"
                )
            )
            
        fig.update_layout(
            title="ETF Price History",
            xaxis_title="Date",
            yaxis_title="Price ($)",
            hovermode="x unified"
        )
        
        return fig
    
    def plot_rolling_correlation(self, window=60):
        """Plot rolling correlation between ETFs"""
        rolling_corr = self.analyzer.returns_df['SPY'].rolling(window).corr(
            self.analyzer.returns_df['QQQ'])
        
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=rolling_corr.index,
                y=rolling_corr,
                name="Rolling Correlation",
                hovertemplate=
                "Date: %{x}<br>" +
                "Correlation: %{y:.3f}<br>"
            )
        )
        
        fig.update_layout(
            title=f"{window}-Day Rolling Correlation: SPY vs QQQ",
            xaxis_title="Date",
            yaxis_title="Correlation",
            hovermode="x unified"
        )
        
        return fig
    
    def plot_regime_analysis(self):
        """Plot tech momentum regimes"""
        tech_momentum, regimes = self.analyzer.analyze_tech_momentum()
        
        fig = go.Figure()
        
        # Plot tech momentum
        fig.add_trace(
            go.Scatter(
                x=tech_momentum.index,
                y=tech_momentum,
                name="Tech Momentum",
                hovertemplate=
                "Date: %{x}<br>" +
                "Momentum: %{y:.3f}<br>"
            )
        )
        
        # Add regime highlights
        for date in regimes[regimes['strong']].index:
            fig.add_vrect(
                x0=date,
                x1=date + pd.Timedelta(days=1),
                fillcolor="green",
                opacity=0.2,
                layer="below",
                line_width=0
            )
            
        for date in regimes[regimes['weak']].index:
            fig.add_vrect(
                x0=date,
                x1=date + pd.Timedelta(days=1),
                fillcolor="red",
                opacity=0.2,
                layer="below",
                line_width=0
            )
        
        fig.update_layout(
            title="Tech Momentum Regimes",
            xaxis_title="Date",
            yaxis_title="Momentum",
            hovermode="x unified"
        )
        
        return fig
    
    def plot_investment_scenarios(self):
        """Plot investment scenario analysis"""
        lump_sum_value, _ = self.analyzer.simulate_lump_sum_investment()
        monthly_value, _ = self.analyzer.simulate_monthly_investment()
        
        fig = go.Figure()
        
        # Plot lump sum investment
        fig.add_trace(
            go.Scatter(
                x=lump_sum_value.index,
                y=lump_sum_value,
                name="Lump Sum ($50K)",
                hovertemplate=
                "Date: %{x}<br>" +
                "Value: $%{y:,.2f}<br>"
            )
        )
        
        # Plot monthly investment
        fig.add_trace(
            go.Scatter(
                x=monthly_value.index,
                y=monthly_value,
                name="Monthly ($7.5K)",
                hovertemplate=
                "Date: %{x}<br>" +
                "Value: $%{y:,.2f}<br>"
            )
        )
        
        fig.update_layout(
            title="Investment Scenarios Comparison",
            xaxis_title="Date",
            yaxis_title="Portfolio Value ($)",
            hovermode="x unified"
        )
        
        return fig
    
    def calculate_performance_metrics(self):
        """Calculate and return performance metrics"""
        lump_sum_value, _ = self.analyzer.simulate_lump_sum_investment()
        monthly_value, _ = self.analyzer.simulate_monthly_investment()
        
        # Lump sum metrics
        total_lump_sum_return = (lump_sum_value[-1] / self.analyzer.initial_lump_sum - 1) * 100
        annual_lump_sum_return = (
            (1 + total_lump_sum_return/100) ** (252/len(lump_sum_value)) - 1) * 100
        
        # Monthly investment metrics
        total_invested = self.analyzer.monthly_investment * len(monthly_value)
        total_monthly_return = (monthly_value[-1] / total_invested - 1) * 100
        annual_monthly_return = (
            (1 + total_monthly_return/100) ** (12/len(monthly_value)) - 1) * 100
        
        return {
            'lump_sum': {
                'total_return': total_lump_sum_return,
                'annual_return': annual_lump_sum_return,
                'final_value': lump_sum_value[-1]
            },
            'monthly': {
                'total_invested': total_invested,
                'total_return': total_monthly_return,
                'annual_return': annual_monthly_return,
                'final_value': monthly_value[-1]
            }
        }

def main():
    st.set_page_config(
        page_title="Market Analysis Dashboard",
        page_icon="📈",
        layout="wide"
    )
    
    # Hide Streamlit menu and footer
    hide_streamlit_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    st.title("📊 Market Analysis Dashboard")
    
    # Initialize dashboard silently
    dashboard = None
    with st.spinner("Loading data..."):
        try:
            dashboard = MarketDashboard()
            
            if dashboard and dashboard.analyzer and dashboard.analyzer.prices_df is not None:
                # Create tabs for different analyses
                tab1, tab2, tab3, tab4 = st.tabs([
                    "Price History", 
                    "Rolling Correlation",
                    "Tech Momentum",
                    "Investment Scenarios"
                ])
                
                with tab1:
                    st.plotly_chart(dashboard.plot_price_history(), use_container_width=True)
                    
                with tab2:
                    window = st.slider("Rolling Window (Days)", 30, 252, 60)
                    st.plotly_chart(dashboard.plot_rolling_correlation(window), use_container_width=True)
                    
                with tab3:
                    st.plotly_chart(dashboard.plot_regime_analysis(), use_container_width=True)
                    
                with tab4:
                    st.plotly_chart(dashboard.plot_investment_scenarios(), use_container_width=True)
                    
                    # Display performance metrics
                    metrics = dashboard.calculate_performance_metrics()
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Lump Sum Investment ($50K)")
                        st.metric("Total Return", f"{metrics['lump_sum']['total_return']:.2f}%")
                        st.metric("Annualized Return", f"{metrics['lump_sum']['annual_return']:.2f}%")
                        st.metric("Final Value", f"${metrics['lump_sum']['final_value']:,.2f}")
                        
                    with col2:
                        st.subheader("Monthly Investment ($7.5K)")
                        st.metric("Total Invested", f"${metrics['monthly']['total_invested']:,.2f}")
                        st.metric("Total Return", f"{metrics['monthly']['total_return']:.2f}%")
                        st.metric("Annualized Return", f"{metrics['monthly']['annual_return']:.2f}%")
                        st.metric("Final Value", f"${metrics['monthly']['final_value']:,.2f}")
            else:
                st.error("Unable to load market data. Please try again later.")
                    
        except Exception:
            st.error("Error initializing dashboard. Please try again later.")

if __name__ == "__main__":
    main() 