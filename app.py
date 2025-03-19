import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import yfinance as yf
import calendar

# Import modules
from dividend_data import load_dividend_kings_data, fetch_stock_data
from aristocrats_data import load_dividend_aristocrats_data
from etf_data import load_etf_data, fetch_etf_data
from portfolio_analysis import calculate_portfolio_metrics, calculate_monthly_income, calculate_etf_portfolio_metrics, calculate_etf_monthly_income, calculate_income_stability_score
from visualization import plot_monthly_income, plot_dividend_growth, plot_yield_comparison, plot_etf_comparison, plot_etf_allocation, plot_monthly_distribution
from stock_detail import display_stock_detail
from etf_detail import display_etf_detail

# Set page configuration
st.set_page_config(
    page_title="Dividend Kings Income Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2563EB;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

def load_all_stocks_data():
    """
    Load and combine data from all portfolios for the All Stocks view
    
    Returns:
        pd.DataFrame: Combined data from all portfolios
    """
    # Load data from all three portfolio types
    kings_data = load_dividend_kings_data()
    aristocrats_data = load_dividend_aristocrats_data()
    etf_data = load_etf_data()
    
    # Add portfolio source column
    kings_data['Portfolio'] = "Dividend Kings"
    aristocrats_data['Portfolio'] = "Dividend Aristocrats" 
    etf_data['Portfolio'] = "ETF Portfolio"
    
    # Standardize column names for consistency
    if 'Name' in etf_data.columns and 'Company' not in etf_data.columns:
        etf_data = etf_data.rename(columns={'Name': 'Company'})
    
    # Prepare combined dataframe with common columns
    kings_columns = kings_data.columns.tolist()
    aristocrats_columns = aristocrats_data.columns.tolist()
    etf_columns = etf_data.columns.tolist()
    
    # Identify key columns that should be in the final result
    key_columns = ['Ticker', 'Portfolio']
    name_column = 'Company' if 'Company' in kings_columns else 'Name'
    key_columns.append(name_column)
    
    # Add payout information if available
    if 'Payout Month' in kings_columns:
        key_columns.append('Payout Month')
    elif 'Payout Frequency' in etf_columns:
        etf_data['Payout Month'] = etf_data['Payout Frequency']
        key_columns.append('Payout Month')
    
    # Add growth information if available
    if 'Years of Growth' in kings_columns:
        key_columns.append('Years of Growth')
    
    # Add yield information if available
    if 'Current Yield' in aristocrats_columns:
        key_columns.append('Current Yield')
    
    # Add description if available
    if 'Description' in kings_columns:
        key_columns.append('Description')
    
    # Filter data to only include common columns
    all_kings = kings_data[[col for col in kings_data.columns if col in key_columns or col == name_column]]
    all_aristocrats = aristocrats_data[[col for col in aristocrats_data.columns if col in key_columns or col == name_column]]
    
    if 'Payout Month' not in etf_data.columns and 'Payout Frequency' in etf_data.columns:
        etf_data['Payout Month'] = etf_data['Payout Frequency']
    
    all_etfs = etf_data[[col for col in etf_data.columns if col in key_columns or col == name_column]]
    
    # Combine all data
    all_stocks = pd.concat([all_kings, all_aristocrats, all_etfs], ignore_index=True)
    
    return all_stocks

def main():
    # App header
    st.markdown("<h1 class='main-header'>Dividend Monthly Income Tracker</h1>", unsafe_allow_html=True)
    
    # Sidebar for user inputs
    st.sidebar.header("Portfolio Settings")
    
    # Portfolio selection
    portfolio_type = st.sidebar.radio(
        "Select Portfolio Type",
        ["Dividend Kings", "Dividend Aristocrats", "ETF Portfolio"]
    )
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Monthly Income Dashboard", 
        "Portfolio Analysis", 
        "Investment Details",
        "Growth & Projections",
        "All Stocks"
    ])
    
    # Load appropriate data based on selection
    if portfolio_type == "Dividend Kings":
        st.sidebar.subheader("Dividend Kings Portfolio")
        dividend_data = load_dividend_kings_data()
        portfolio_title = "Dividend Kings"
    elif portfolio_type == "Dividend Aristocrats":
        st.sidebar.subheader("Dividend Aristocrats Portfolio")
        dividend_data = load_dividend_aristocrats_data()
        portfolio_title = "Dividend Aristocrats"
    else:  # ETF Portfolio
        st.sidebar.subheader("ETF Portfolio")
        dividend_data = load_etf_data()
        portfolio_title = "ETF Portfolio"
    
    # Default investment amount
    default_investment = 10000  # $10,000 per stock by default
    
    # Add input method selection
    input_method = st.sidebar.radio(
        "Input Method",
        ["Investment Amount", "Share Count"]
    )
    
    # Create a dictionary to store input values
    input_values = {}
    
    # Add inputs to sidebar based on selected method
    st.sidebar.subheader("Portfolio Allocation")
    
    if input_method == "Investment Amount":
        # Option to set equal investment for all stocks
        equal_investment = st.sidebar.checkbox("Equal investment for all stocks", value=True)
        
        if equal_investment:
            default_amount = st.sidebar.number_input(
                "Investment amount per stock ($)",
                min_value=1000,
                max_value=1000000,
                value=default_investment,
                step=1000
            )
            
            for ticker in dividend_data['Ticker'].unique():
                input_values[ticker] = default_amount
        else:
            # Create individual inputs for each stock
            for _, row in dividend_data.iterrows():
                ticker = row['Ticker']
                company = row['Company'] if 'Company' in row else row.get('Name', ticker)
                input_values[ticker] = st.sidebar.number_input(
                    f"{company} ({ticker}) investment ($)",
                    min_value=0,
                    max_value=1000000,
                    value=default_investment,
                    step=1000
                )
    else:  # Share Count
        # Option to set equal shares for all stocks
        equal_shares = st.sidebar.checkbox("Equal shares for all stocks", value=True)
        
        if equal_shares:
            default_shares = st.sidebar.number_input(
                "Number of shares per stock",
                min_value=1,
                max_value=10000,
                value=100,
                step=10
            )
            
            for ticker in dividend_data['Ticker'].unique():
                input_values[ticker] = default_shares
        else:
            # Create individual inputs for each stock
            for _, row in dividend_data.iterrows():
                ticker = row['Ticker']
                company = row['Company'] if 'Company' in row else row.get('Name', ticker)
                input_values[ticker] = st.sidebar.number_input(
                    f"{company} ({ticker}) shares",
                    min_value=0,
                    max_value=10000,
                    value=100,
                    step=10
                )
    
    # Add input data to the dataframe
    if input_method == "Investment Amount":
        # Use investment amounts to calculate shares
        investment_data = []
        for ticker, amount in input_values.items():
            investment_data.append({"Ticker": ticker, "Investment": amount})
        
        investment_df = pd.DataFrame(investment_data)
        portfolio_df = dividend_data.merge(investment_df, on="Ticker")
    else:  # Share Count
        # Use share counts to calculate investment amount
        share_data = []
        for ticker, shares in input_values.items():
            share_data.append({"Ticker": ticker, "Shares": shares})
        
        share_df = pd.DataFrame(share_data)
        portfolio_df = dividend_data.merge(share_df, on="Ticker")
    
    # Fetch latest stock/ETF data and calculate current metrics
    try:
        tickers = dividend_data['Ticker'].tolist()
        
        if portfolio_type == "ETF Portfolio":
            stock_data = fetch_etf_data(tickers)
        else:
            stock_data = fetch_stock_data(tickers)
        
        # Add current price and calculate current yield
        for ticker in tickers:
            if ticker in stock_data:
                current_price = stock_data[ticker]['price']
                
                # For Aristocrats/ETFs, we may already have the yield, so calculate the dividend
                if (portfolio_type in ["Dividend Aristocrats", "ETF Portfolio"]) and 'Current Yield' in dividend_data.columns:
                    # Use the provided yield if stock data yield is not available
                    if stock_data[ticker]['yield'] <= 0:
                        stock_yield = dividend_data.loc[dividend_data['Ticker'] == ticker, 'Current Yield'].values[0]
                        stock_data[ticker]['dividend'] = current_price * stock_yield / 100
                
                portfolio_df.loc[portfolio_df['Ticker'] == ticker, 'Current Price'] = current_price
                
                # For ETFs, get expense ratio if available
                if portfolio_type == "ETF Portfolio" and 'expense_ratio' in stock_data[ticker]:
                    portfolio_df.loc[portfolio_df['Ticker'] == ticker, 'Expense Ratio'] = stock_data[ticker]['expense_ratio']
                
                # For Kings, calculate yield from dividend
                if portfolio_type == "Dividend Kings" or 'Current Yield' not in portfolio_df.columns:
                    portfolio_df.loc[portfolio_df['Ticker'] == ticker, 'Current Yield'] = (
                        stock_data[ticker]['dividend'] / current_price * 100
                    )
                
                # Calculate shares or investment based on input method
                if input_method == "Investment Amount":
                    # Calculate shares based on investment amount
                    portfolio_df.loc[portfolio_df['Ticker'] == ticker, 'Shares'] = (
                        portfolio_df.loc[portfolio_df['Ticker'] == ticker, 'Investment'] / current_price
                    ).round(2)
                else:  # Share Count
                    # Calculate investment based on share count
                    portfolio_df.loc[portfolio_df['Ticker'] == ticker, 'Investment'] = (
                        portfolio_df.loc[portfolio_df['Ticker'] == ticker, 'Shares'] * current_price
                    ).round(2)
                
                # Calculate annual dividend/distribution income
                if portfolio_type in ["Dividend Aristocrats", "ETF Portfolio"] and 'Current Yield' in portfolio_df.columns:
                    # Use the yield to calculate income
                    portfolio_df.loc[portfolio_df['Ticker'] == ticker, 'Annual Income'] = (
                        portfolio_df.loc[portfolio_df['Ticker'] == ticker, 'Investment'] * 
                        portfolio_df.loc[portfolio_df['Ticker'] == ticker, 'Current Yield'] / 100
                    ).round(2)
                else:
                    # Use the dividend rate to calculate income
                    portfolio_df.loc[portfolio_df['Ticker'] == ticker, 'Annual Income'] = (
                        portfolio_df.loc[portfolio_df['Ticker'] == ticker, 'Shares'] * stock_data[ticker]['dividend']
                    ).round(2)
                
                # Calculate monthly income 
                if portfolio_type == "ETF Portfolio" and 'Payout Frequency' in portfolio_df.columns:
                    # For ETFs, handle based on payout frequency
                    frequency = portfolio_df.loc[portfolio_df['Ticker'] == ticker, 'Payout Frequency'].values[0]
                    if frequency == 'Monthly':
                        # Monthly payers get divided by 12
                        portfolio_df.loc[portfolio_df['Ticker'] == ticker, 'Monthly Income'] = (
                            portfolio_df.loc[portfolio_df['Ticker'] == ticker, 'Annual Income'] / 12
                        ).round(2)
                    else:
                        # Quarterly payers get divided by 4
                        portfolio_df.loc[portfolio_df['Ticker'] == ticker, 'Monthly Income'] = (
                            portfolio_df.loc[portfolio_df['Ticker'] == ticker, 'Annual Income'] / 4
                        ).round(2)
                else:
                    # For stocks, divide by 4 since most companies pay quarterly
                    portfolio_df.loc[portfolio_df['Ticker'] == ticker, 'Monthly Income'] = (
                        portfolio_df.loc[portfolio_df['Ticker'] == ticker, 'Annual Income'] / 4
                    ).round(2)
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        st.info("Using sample data instead...")
        # Generate sample data if API fails
        portfolio_df['Current Price'] = np.random.uniform(50, 200, len(portfolio_df))
        
        # For Aristocrats/ETFs, use the provided yield
        if portfolio_type in ["Dividend Aristocrats", "ETF Portfolio"] and 'Current Yield' in portfolio_df.columns:
            pass  # Keep the existing yield
        else:
            portfolio_df['Current Yield'] = np.random.uniform(1.5, 5, len(portfolio_df))
        
        # For ETFs, add expense ratio if not there
        if portfolio_type == "ETF Portfolio" and 'Expense Ratio' not in portfolio_df.columns:
            portfolio_df['Expense Ratio'] = np.random.uniform(0.3, 1.2, len(portfolio_df))
        
        # Calculate shares or investment based on input method
        if input_method == "Investment Amount" and 'Shares' not in portfolio_df.columns:
            portfolio_df['Shares'] = (portfolio_df['Investment'] / portfolio_df['Current Price']).round(2)
        elif input_method == "Share Count" and 'Investment' not in portfolio_df.columns:
            portfolio_df['Investment'] = (portfolio_df['Shares'] * portfolio_df['Current Price']).round(2)
            
        portfolio_df['Annual Income'] = (
            portfolio_df['Shares'] * portfolio_df['Current Price'] * portfolio_df['Current Yield'] / 100
        ).round(2)
        
        # Calculate monthly income
        if portfolio_type == "ETF Portfolio" and 'Payout Frequency' in portfolio_df.columns:
            # Handle different payout frequencies
            for i, row in portfolio_df.iterrows():
                if row['Payout Frequency'] == 'Monthly':
                    portfolio_df.loc[i, 'Monthly Income'] = (row['Annual Income'] / 12).round(2)
                else:
                    portfolio_df.loc[i, 'Monthly Income'] = (row['Annual Income'] / 4).round(2)
        else:
            portfolio_df['Monthly Income'] = (portfolio_df['Annual Income'] / 4).round(2)
    
    # Calculate portfolio metrics
    if portfolio_type == "ETF Portfolio":
        total_investment, total_annual_income, portfolio_yield, weighted_expense_ratio = calculate_etf_portfolio_metrics(portfolio_df)
        monthly_income = calculate_etf_monthly_income(portfolio_df)
    else:
        total_investment, total_annual_income, portfolio_yield = calculate_portfolio_metrics(portfolio_df)
        monthly_income = calculate_monthly_income(portfolio_df)
        weighted_expense_ratio = 0  # Not applicable for stocks
    
    # Tab 1: Monthly Income Dashboard
    with tab1:
        # Summary metrics
        st.markdown(f"<h2 class='sub-header'>{portfolio_title} Monthly Income Dashboard</h2>", unsafe_allow_html=True)
        
        # Add metrics based on portfolio type
        if portfolio_type == "ETF Portfolio":
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Investment", f"${total_investment:,.2f}")
            with col2:
                st.metric("Projected Annual Income", f"${total_annual_income:,.2f}")
            with col3:
                st.metric("Portfolio Yield", f"{portfolio_yield:.2f}%")
            with col4:
                st.metric("Avg Expense Ratio", f"{weighted_expense_ratio:.2f}%")
            
            # Calculate stability score
            stability_score = calculate_income_stability_score(portfolio_df)
            st.progress(stability_score/100, text=f"Income Stability Score: {stability_score:.1f}/100")
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Investment", f"${total_investment:,.2f}")
            with col2:
                st.metric("Projected Annual Income", f"${total_annual_income:,.2f}")
            with col3:
                st.metric("Portfolio Yield", f"{portfolio_yield:.2f}%")
        
        st.markdown("<h2 class='sub-header'>Monthly Income Distribution</h2>", unsafe_allow_html=True)
        
        # Plot monthly income
        if portfolio_type == "ETF Portfolio":
            monthly_fig = plot_monthly_distribution(monthly_income, f"{portfolio_title} Monthly Income")
        else:
            monthly_fig = plot_monthly_income(monthly_income, portfolio_title)
            
        st.plotly_chart(monthly_fig, use_container_width=True)
        
        # Monthly income table
        st.markdown("<h2 class='sub-header'>Monthly Income Breakdown</h2>", unsafe_allow_html=True)
        
        monthly_table = pd.DataFrame({
            'Month': list(calendar.month_name)[1:],
            'Income': [monthly_income.get(month, 0) for month in list(calendar.month_name)[1:]]
        })
        monthly_table['Income'] = monthly_table['Income'].apply(lambda x: f"${x:.2f}")
        
        st.dataframe(monthly_table, use_container_width=True)
    
    # Tab 2: Portfolio Analysis
    with tab2:
        st.markdown(f"<h2 class='sub-header'>{portfolio_title} Composition</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Investment allocation pie chart
            if portfolio_type == "ETF Portfolio":
                fig_allocation = plot_etf_allocation(portfolio_df)
            else:
                fig_allocation = px.pie(
                    portfolio_df,
                    values='Investment',
                    names='Company' if 'Company' in portfolio_df.columns else 'Name',
                    title='Investment Allocation',
                    hole=0.4,
                )
            st.plotly_chart(fig_allocation, use_container_width=True)
        
        with col2:
            # Income allocation pie chart
            fig_income = px.pie(
                portfolio_df,
                values='Annual Income',
                names='Company' if 'Company' in portfolio_df.columns else 'Name',
                title='Income Allocation',
                hole=0.4,
            )
            st.plotly_chart(fig_income, use_container_width=True)
        
        # Yield comparison
        st.markdown("<h2 class='sub-header'>Yield Comparison</h2>", unsafe_allow_html=True)
        
        if portfolio_type == "ETF Portfolio":
            metric_option = st.selectbox(
                "Select comparison metric",
                ["yield", "expense_ratio", "income"],
                format_func=lambda x: {
                    "yield": "Yield (%)", 
                    "expense_ratio": "Expense Ratio (%)", 
                    "income": "Annual Income ($)"
                }.get(x)
            )
            yield_fig = plot_etf_comparison(portfolio_df, metric=metric_option)
        else:
            yield_fig = plot_yield_comparison(portfolio_df, portfolio_title)
            
        st.plotly_chart(yield_fig, use_container_width=True)
        
        # Portfolio table
        st.markdown("<h2 class='sub-header'>Complete Portfolio</h2>", unsafe_allow_html=True)
        
        if portfolio_type == "ETF Portfolio":
            display_columns = [
                'Name', 'Ticker', 'Investment', 'Current Price', 'Shares', 
                'Current Yield', 'Annual Income', 'Expense Ratio', 'Payout Frequency'
            ]
        else:
            display_columns = [
                'Company', 'Ticker', 'Investment', 'Current Price', 'Shares', 
                'Current Yield', 'Annual Income', 'Payout Month', 'Years of Growth'
            ]
            
            # Add Notes column for Aristocrats if it exists
            if 'Notes' in portfolio_df.columns and portfolio_df['Notes'].astype(bool).any():
                display_columns.append('Notes')
        
        # Filter to only columns that exist
        display_columns = [col for col in display_columns if col in portfolio_df.columns]
        
        # Format currency columns
        formatted_df = portfolio_df[display_columns].copy()
        formatted_df['Investment'] = formatted_df['Investment'].apply(lambda x: f"${x:,.2f}")
        formatted_df['Current Price'] = formatted_df['Current Price'].apply(lambda x: f"${x:.2f}")
        formatted_df['Annual Income'] = formatted_df['Annual Income'].apply(lambda x: f"${x:.2f}")
        formatted_df['Current Yield'] = formatted_df['Current Yield'].apply(lambda x: f"{x:.2f}%")
        if 'Expense Ratio' in formatted_df.columns:
            formatted_df['Expense Ratio'] = formatted_df['Expense Ratio'].apply(lambda x: f"{x:.2f}%")
        
        st.dataframe(formatted_df, use_container_width=True)
    
    # Tab 3: Investment Details
    with tab3:
        if portfolio_type == "ETF Portfolio":
            st.markdown(f"<h2 class='sub-header'>{portfolio_title} Details</h2>", unsafe_allow_html=True)
            
            # Select ETF for detailed view
            selected_etf = st.selectbox(
                "Select an ETF or CEF",
                options=portfolio_df['Name'].tolist()
            )
            
            # Display ETF details
            etf_row = portfolio_df[portfolio_df['Name'] == selected_etf].iloc[0]
            display_etf_detail(etf_row, stock_data.get(etf_row['Ticker'], None))
        else:
            st.markdown(f"<h2 class='sub-header'>{portfolio_title} Stock Details</h2>", unsafe_allow_html=True)
            
            # Select stock for detailed view
            selected_stock = st.selectbox(
                f"Select a {portfolio_title.rstrip('s')}",
                options=portfolio_df['Company'].tolist()
            )
            
            # Display stock details
            stock_row = portfolio_df[portfolio_df['Company'] == selected_stock].iloc[0]
            display_stock_detail(stock_row, stock_data.get(stock_row['Ticker'], None))
    
    # Tab 4: Growth & Projections
    with tab4:
        if portfolio_type == "ETF Portfolio":
            st.markdown("<h2 class='sub-header'>Distribution Projection Analysis</h2>", unsafe_allow_html=True)
            
            # For ETF Portfolio, show a comparison of projected income over time
            st.write("""
            This analysis projects the income growth from your ETF portfolio over time. 
            While ETFs generally have more stable distributions compared to individual dividend stocks, 
            they may still experience growth over time.
            """)
            
            # Create time series prediction of portfolio income
            years = list(range(1, 11))
            growth_scenario = {
                'Low': 0.01,     # 1% annual growth
                'Moderate': 0.03, # 3% annual growth
                'High': 0.05      # 5% annual growth
            }
            
            # Allow user to select growth scenario
            selected_scenario = st.radio(
                "Select income growth scenario",
                ["Low", "Moderate", "High"],
                horizontal=True
            )
            
            growth_rate = growth_scenario[selected_scenario]
            
            # Calculate growth projections
            initial_annual_income = total_annual_income
            projection_data = []
            
            for year in range(1, 11):
                year_income = initial_annual_income * (1 + growth_rate) ** (year - 1)
                projection_data.append({
                    'Year': year,
                    'Annual Income': year_income,
                    'Monthly Income': year_income / 12
                })
            
            # Create dataframe
            projection_df = pd.DataFrame(projection_data)
            
            # Plot projection
            fig = px.line(
                projection_df,
                x='Year',
                y='Annual Income',
                title=f"Projected Annual Income ({selected_scenario} Growth: {growth_rate*100:.1f}%)",
                markers=True
            )
            
            fig.update_layout(
                xaxis_title='Year',
                yaxis_title='Annual Income ($)',
                template='plotly_white',
                height=400
            )
            
            fig.update_yaxes(tickprefix='$')
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Calculate cumulative income
            projection_df['Cumulative Income'] = projection_df['Annual Income'].cumsum()
            
            # Compare to original investment
            final_cumulative = projection_df['Cumulative Income'].iloc[-1]
            roi_percent = (final_cumulative / total_investment) * 100
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("10-Year Cumulative Income", f"${final_cumulative:,.2f}")
                st.metric("Return on Investment", f"{roi_percent:.2f}%")
                
            with col2:
                st.metric("Year 10 Annual Income", f"${projection_df['Annual Income'].iloc[-1]:,.2f}")
                income_growth = (projection_df['Annual Income'].iloc[-1] / projection_df['Annual Income'].iloc[0] - 1) * 100
                st.metric("Income Growth Over 10 Years", f"{income_growth:.2f}%")
                
            # Show detailed table
            st.write("### Year-by-Year Projection")
            detailed_df = projection_df.copy()
            detailed_df['Annual Income'] = detailed_df['Annual Income'].apply(lambda x: f"${x:,.2f}")
            detailed_df['Monthly Income'] = detailed_df['Monthly Income'].apply(lambda x: f"${x:,.2f}")
            detailed_df['Cumulative Income'] = detailed_df['Cumulative Income'].apply(lambda x: f"${x:,.2f}")
            
            st.dataframe(detailed_df, use_container_width=True)
            
        else:
            st.markdown(f"<h2 class='sub-header'>{portfolio_title} Dividend Growth & Income Forecast</h2>", unsafe_allow_html=True)
            
            # Add tabs within the Growth & Projections tab for different forecast views
            forecast_tab1, forecast_tab2 = st.tabs(["Monthly Income Forecast", "Dividend Growth History"])
            
            with forecast_tab1:
                st.markdown("<h3>Monthly Income Forecast</h3>", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Allow user to select forecast horizon
                    forecast_years = st.slider(
                        "Forecast Horizon (Years)",
                        min_value=1,
                        max_value=10,
                        value=5
                    )
                
                with col2:
                    # Allow user to select growth scenario
                    growth_scenario = st.radio(
                        "Dividend Growth Scenario",
                        ["Conservative (3%)", "Moderate (5%)", "Aggressive (7%)"],
                        horizontal=True
                    )
                
                # Map scenario to annual growth rate
                growth_rates = {
                    "Conservative (3%)": 0.03,
                    "Moderate (5%)": 0.05,
                    "Aggressive (7%)": 0.07
                }
                
                annual_growth_rate = growth_rates[growth_scenario]
                
                # Calculate current monthly income
                monthly_income = calculate_monthly_income(portfolio_df)
                
                # Create forecast for each month over the forecast period
                forecast_data = []
                
                for year in range(1, forecast_years + 1):
                    year_growth_factor = (1 + annual_growth_rate) ** (year - 1)
                    
                    for month, income in monthly_income.items():
                        # Apply growth factor to monthly income
                        projected_income = income * year_growth_factor
                        
                        forecast_data.append({
                            'Year': year,
                            'Month': month,
                            'Projected Income': projected_income
                        })
                
                # Create dataframe
                forecast_df = pd.DataFrame(forecast_data)
                
                # Create visualization
                view_option = st.radio(
                    "Visualization View",
                    ["Monthly View", "Yearly Comparison"],
                    horizontal=True
                )
                
                if view_option == "Monthly View":
                    # Line chart showing projected income by month for each year
                    fig = px.line(
                        forecast_df,
                        x='Month',
                        y='Projected Income',
                        color='Year',
                        title=f"Projected Monthly Income ({growth_scenario})",
                        markers=True
                    )
                    
                    # Custom month order
                    month_order = list(calendar.month_name)[1:]
                    fig.update_xaxes(categoryorder='array', categoryarray=month_order)
                    
                else:  # Yearly Comparison
                    # Calculate yearly totals
                    yearly_totals = forecast_df.groupby('Year')['Projected Income'].sum().reset_index()
                    yearly_totals['Projected Annual Income'] = yearly_totals['Projected Income']
                    
                    fig = px.bar(
                        yearly_totals,
                        x='Year',
                        y='Projected Annual Income',
                        title=f"Projected Annual Income Over {forecast_years} Years ({growth_scenario})",
                        color='Projected Annual Income',
                        color_continuous_scale='blues'
                    )
                
                fig.update_layout(
                    xaxis_title='Month' if view_option == "Monthly View" else 'Year',
                    yaxis_title='Income ($)',
                    template='plotly_white',
                    height=500
                )
                
                fig.update_yaxes(tickprefix='$')
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Calculate and display summary statistics
                total_current_annual = sum(monthly_income.values()) * 4  # Quarterly payments
                total_final_annual = forecast_df[forecast_df['Year'] == forecast_years]['Projected Income'].sum()
                
                # Create columns for metrics
                metric_col1, metric_col2, metric_col3 = st.columns(3)
                
                with metric_col1:
                    st.metric(
                        "Current Annual Income", 
                        f"${total_current_annual:,.2f}"
                    )
                
                with metric_col2:
                    st.metric(
                        f"Projected Annual Income (Year {forecast_years})", 
                        f"${total_final_annual:,.2f}",
                        delta=f"{((total_final_annual / total_current_annual) - 1) * 100:.2f}%"
                    )
                
                with metric_col3:
                    monthly_avg_current = total_current_annual / 12
                    monthly_avg_projected = total_final_annual / 12
                    
                    st.metric(
                        f"Average Monthly Income (Year {forecast_years})", 
                        f"${monthly_avg_projected:,.2f}",
                        delta=f"${monthly_avg_projected - monthly_avg_current:,.2f}"
                    )
                
                # Add detailed forecast table
                with st.expander("Detailed Monthly Income Forecast"):
                    # Calculate average monthly income for each year
                    yearly_avg = forecast_df.groupby('Year')['Projected Income'].mean().reset_index()
                    yearly_avg['Average Monthly Income'] = yearly_avg['Projected Income'].round(2)
                    yearly_avg = yearly_avg[['Year', 'Average Monthly Income']]
                    
                    # Calculate total annual income for each year
                    yearly_sum = forecast_df.groupby('Year')['Projected Income'].sum().reset_index()
                    yearly_sum['Total Annual Income'] = yearly_sum['Projected Income'].round(2)
                    yearly_sum = yearly_sum[['Year', 'Total Annual Income']]
                    
                    # Merge the two
                    yearly_stats = pd.merge(yearly_avg, yearly_sum, on='Year')
                    
                    # Format as currency
                    yearly_stats['Average Monthly Income'] = yearly_stats['Average Monthly Income'].apply(lambda x: f"${x:,.2f}")
                    yearly_stats['Total Annual Income'] = yearly_stats['Total Annual Income'].apply(lambda x: f"${x:,.2f}")
                    
                    st.dataframe(yearly_stats, use_container_width=True)
                    
                    # Show monthly breakdown for selected year
                    selected_year = st.selectbox("Select Year for Monthly Breakdown", options=range(1, forecast_years + 1))
                    
                    monthly_breakdown = forecast_df[forecast_df['Year'] == selected_year][['Month', 'Projected Income']]
                    monthly_breakdown['Projected Income'] = monthly_breakdown['Projected Income'].apply(lambda x: f"${x:,.2f}")
                    
                    st.dataframe(monthly_breakdown, use_container_width=True)
            
            with forecast_tab2:
                # Keep existing dividend growth history visualization
                # Select stock for dividend growth history
                selected_growth_stock = st.selectbox(
                    f"Select a {portfolio_title.rstrip('s')} for Growth History",
                    options=portfolio_df['Company'].tolist(),
                    key="growth_select"
                )
                
                # Display dividend growth chart
                stock_row = portfolio_df[portfolio_df['Company'] == selected_growth_stock].iloc[0]
                growth_fig = plot_dividend_growth(stock_row['Ticker'])
                st.plotly_chart(growth_fig, use_container_width=True)
    
    # Tab 5: All Stocks
    with tab5:
        st.markdown("<h2 class='sub-header'>All Available Stocks</h2>", unsafe_allow_html=True)
        
        # Load and display all stocks
        all_stocks = load_all_stocks_data()
        
        # Add filtering options
        col1, col2 = st.columns(2)
        
        with col1:
            portfolio_filter = st.multiselect(
                "Filter by Portfolio Type",
                options=["Dividend Kings", "Dividend Aristocrats", "ETF Portfolio"],
                default=["Dividend Kings", "Dividend Aristocrats", "ETF Portfolio"]
            )
        
        with col2:
            # Add search functionality
            search_term = st.text_input("Search by Company or Ticker")
        
        # Apply filters
        filtered_stocks = all_stocks[all_stocks['Portfolio'].isin(portfolio_filter)]
        
        if search_term:
            filtered_stocks = filtered_stocks[
                filtered_stocks['Company'].str.contains(search_term, case=False) | 
                filtered_stocks['Ticker'].str.contains(search_term, case=False)
            ]
        
        # Sort options
        sort_by = st.selectbox(
            "Sort by",
            options=["Company", "Ticker", "Portfolio"] + 
                    (["Years of Growth"] if "Years of Growth" in all_stocks.columns else []) +
                    (["Current Yield"] if "Current Yield" in all_stocks.columns else [])
        )
        
        # Sort the data
        sorted_stocks = filtered_stocks.sort_values(by=sort_by)
        
        # Display the data
        st.dataframe(sorted_stocks, use_container_width=True)
        
        # Add export functionality
        if st.button("Export All Stocks to CSV"):
            # Convert dataframe to CSV
            csv = sorted_stocks.to_csv(index=False)
            
            # Create download button
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="all_dividend_stocks.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()