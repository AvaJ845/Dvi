# Dividend Monthly Income Tracker

A Streamlit application for tracking and analyzing dividend income from both Dividend Kings and Dividend Aristocrats that pay dividends across different months of the year, allowing you to create consistent monthly income streams.

## Portfolio Options

1. **Dividend Kings**: 12 companies with 50+ years of consecutive dividend growth, with payments spread across all 12 months of the year
2. **Dividend Aristocrats**: 10 top dividend aristocrats (25+ years of consecutive dividend growth) with payments spread across the calendar
3. **ETF Portfolio**: A selection of dividend-focused ETFs and Closed-End Funds (including CLM and SDVI) that provide high yields and consistent income

## Features

- **Monthly Income Dashboard**: Visualize your dividend income throughout the year
- **Portfolio Analysis**: Analyze investment allocation and dividend yield comparison
- **Stock Details**: Get detailed information about each Dividend King
- **Dividend Growth History**: Track historical dividend growth for each stock

## Installation

1. Clone this repository or download the files
2. Install the required dependencies:

```bash
pip install streamlit pandas numpy matplotlib seaborn plotly yfinance
```

3. Run the application:

```bash
streamlit run app.py
```

## Project Structure

- `app.py`: Main application file
- `dividend_data.py`: Module for loading and fetching dividend data
- `portfolio_analysis.py`: Module for portfolio metrics calculation
- `visualization.py`: Module for data visualization
- `stock_detail.py`: Module for displaying detailed stock information

## Usage

1. The application will open in your web browser
2. Use the sidebar to select your portfolio type:
   - **Dividend Kings**: Companies with 50+ years of dividend growth
   - **Dividend Aristocrats**: Companies with 25+ years of dividend growth
   - **ETF Portfolio**: Dividend ETFs and CEFs including high-yield options

3. Choose your input method:
   - **Investment Amount**: Specify dollar amounts to invest in each security
   - **Share Count**: Enter the number of shares you own of each security

4. The app will calculate your projected income and display it across different tabs:
   - **Monthly Income Dashboard**: View your projected monthly dividend income
   - **Portfolio Analysis**: Analyze investment allocation and yield comparison
   - **Investment Details**: Get detailed information about each investment
   - **Growth & Projections**: Track historical growth or analyze future projections

## Customization

- You can modify the `load_dividend_kings_data()` function in `dividend_data.py` to add or replace stocks
- Adjust the investment amounts in the sidebar to see how changes affect your income
- The application uses the Yahoo Finance API to fetch real-time data, but includes fallback sample data if the API is unavailable

## Data Sources

- Stock data is fetched from Yahoo Finance using the `yfinance` library
- Dividend Kings information is stored in the application

## Requirements

- Python 3.7+
- Streamlit
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Plotly
- yfinance

## Contributing

Feel free to submit issues or pull requests for improvements or bug fixes.

## License

This project is released under the MIT License.