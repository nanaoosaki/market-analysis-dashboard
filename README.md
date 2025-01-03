# Market Analysis Dashboard

An interactive dashboard for analyzing ETF performance and investment strategies.

## Features

- Price history visualization for SPY and QQQ
- Rolling correlation analysis
- Tech momentum regime analysis
- Investment scenario comparison (lump sum vs. monthly investment)

## Live Demo

[Access the live dashboard here](https://share.streamlit.io/nanaoosaki/market-analysis-dashboard)

## Local Development

1. Clone the repository:
```bash
git clone https://github.com/nanaoosaki/market-analysis-dashboard.git
cd market-analysis-dashboard
```

2. Create a virtual environment:
```bash
python -m venv py310
source py310/bin/activate  # On Windows: .\py310\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the dashboard:
```bash
streamlit run analysis/dashboard/market_dashboard.py
```

## Data Sources

- Historical ETF data from Yahoo Finance
- Price and volume data updated daily

## Investment Strategy

The dashboard implements a momentum-based strategy:
- Analyzes relative strength between SPY and QQQ
- Dynamically adjusts allocations based on tech momentum
- Compares lump sum vs. dollar-cost averaging approaches

## Contributing

Feel free to open issues or submit pull requests with improvements.
